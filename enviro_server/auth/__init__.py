from flask import request
from enviro_server.auth.tasks import auth, signup, login, signup_task, login_task

@auth.route('/login', methods=['POST'])
def login():
    if(auth.config['TESTING']):
        return tuple(login_task([request.get_json()], auth.config['session']))
    return tuple(login.delay([request.get_json(), ]).get())

@auth.route('/signup', methods=['POST'])
def signup():
    if(auth.config['TESTING']):
        return tuple(signup_task([request.get_json()], auth.config['session']))
    return tuple(signup.delay([request.get_json(), ]).get())
