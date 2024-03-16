from flask import Blueprint
from enviro_server.extensions import celery, db
from enviro_server.database.models import User, Blacklist

auth = Blueprint('auth', __name__)

@celery.task
def login(args):
    return login_task(args, db.session)

@celery.task
def signup(args):
    return signup_task(args, db.session)

@celery.task
def logout(args):
    return logout_task(args, db.session)

@celery.task
def status(args):
    return status_task(args, db.session)

def logout_task(args, session):
    request = args[0]
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = Blacklist(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                return (responseObject, 200)
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return (responseObject, 200)
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return (responseObject, 401)
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return (responseObject, 403)

def status_task(args, session):
    auth_header = args[0]
    secret = args[1]
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp, rc = User.decode_auth_token(secret, auth_token, session)
        if not rc:
            user = session.query(User).filter_by(nickname=resp).first()
            responseObject = {
                'status': 'success',
                'data': {
                    'nickname': user.nickname,
                    'is_admin': user.is_admin,
                    'registered_on': user.registered_on
                }
            }
            return (responseObject, 200)
        responseObject = {
            'status': 'fail',
            'message': resp
        }
        return (responseObject, 401)
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return (responseObject, 401)

def login_task(args, session):
    post_data = args[0]
    secret = args[1]
    try:
        # fetch the user data
        user = session.query(User).filter_by(
            nickname=post_data['nickname']
            ).first()
        auth_token = user.encode_auth_token(secret, user.nickname)
        if auth_token:
            responseObject = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token
            }
            return (responseObject, 200)
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Try again'
        }
        return (responseObject, 500)

def signup_task(args, session):
    post_data = args[0]
    secret = args[1]
    user = session.query(User).filter_by(nickname=post_data['nickname']).first()
    if not user:
        try:
            user = User(
                nickname=post_data['nickname'],
                password=post_data['password']
            )
            # insert the user
            session.add(user)
            session.commit()
            auth_token = user.encode_auth_token(secret, user.nickname)
            responseObject = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token
            }
            return (responseObject, 201)
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return (responseObject, 1)
    else:
        responseObject = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return (responseObject, 202)