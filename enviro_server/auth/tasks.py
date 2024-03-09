from flask import Blueprint
from enviro_server.extensions import celery, db
from enviro_server.database.models import User

auth = Blueprint('auth', __name__)

@celery.task
def login(args):
    return login_task(args, db.session)

@celery.task
def signup(args):
    return signup_task(args, db.session)

def login_task(args, session):
    post_data = args[0]
    try:
        # fetch the user data
        user = session.query(User).filter_by(
            nickname=post_data['nickname']
            ).first()
        auth_token = user.encode_auth_token(user.nickname)
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
    # check if user already exists
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
            # generate the auth token
            auth_token = user.encode_auth_token(user.nickname)
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