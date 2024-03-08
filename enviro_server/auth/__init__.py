from flask import request
from enviro_server.auth.tasks import auth, signup_task, login_task, signup_routine, login_routine

@auth.route('/login', methods=['POST'])
def login():
    if(auth.config['TESTING']):
        response = login_routine([request.get_json()], auth.config['session'])
    else:
        response = login_task.delay([request.get_json(), ]).get()
    return response[0], response[1]

@auth.route('/signup', methods=['POST'])
def signup():
    if(auth.config['TESTING']):
        response = signup_routine([request.get_json()], auth.config['session'])
    else:
        response = signup_task.delay([request.get_json(), ]).get()
    return response[0], response[1]
