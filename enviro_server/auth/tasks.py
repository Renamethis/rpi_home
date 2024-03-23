from flask import Blueprint
from enviro_server.extensions import celery, db
from enviro_server.database.models import User, Blacklist

auth = Blueprint('auth', __name__)

def token_required(func):
    def wrapper(args, session, *optargs):
        token = args[0]
        secret = args[1]
        if token:
            token = token.split(" ")[1]
        else:
            token = ''
        resp, rc = User.decode_auth_token(secret, token, session)
        if(not rc and token):
            args.append(resp)
            return func(args, session, *optargs)
        return {"status": "token authentication failed", "message": resp}, 401
    return wrapper

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

@token_required
def logout_task(args, session):
    auth_token = args[0]
    # mark the token as blacklisted
    blacklist_token = Blacklist(token=auth_token)
    try:
        # insert the token
        session.add(blacklist_token)
        session.commit()
        responseObject = {
            'status': 'success',
            'message': 'Successfully logged out.'
        }
        return (responseObject, 200)
    except Exception as e:
        responseObject = {
            'status': 'fail',
            'message': str(e)
        }
        return (responseObject, 200)

@token_required
def status_task(args, session):
    resp = args[2]
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


def login_task(args, session, testing=False):
    post_data = args[0]
    secret = args[1]
    try:
        # fetch the user data
        user = session.query(User).filter_by(
            nickname=post_data['nickname']
            ).first()
        if user and check_password_hash(user.password, post_data.get('password')):
            if(testing): # TODO: Refactor
                auth_token = user.encode_auth_token(secret, user.nickname, datetime.timedelta(seconds=1))
            else:
                auth_token = user.encode_auth_token(secret, user.nickname)
            if auth_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token
                }
                return (responseObject, 200)
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist.'
            }
            return (responseObject, 404)
    except Exception as e:
        responseObject = {
            'status': 'fail',
            'message': 'Try again'
        }
        return (responseObject, 500)

def signup_task(args, session, testing=False):
    post_data = args[0]
    secret = args[1]
    user = session.query(User).filter_by(nickname=post_data['nickname']).first()
    if not user:
        try:
            user = User(
                nickname=post_data['nickname'],
                password=post_data['password']
            )
            session.add(user)
            session.commit()
            if(testing):
                auth_token = user.encode_auth_token(secret, user.nickname, datetime.timedelta(seconds=1))
            else:
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