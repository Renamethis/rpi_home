from flask import request
from enviro_server.auth.tasks import auth, signup, login, logout, status, signup_task, login_task, logout_task, status_task

@auth.route('/login', methods=['POST'])
def login_route():
    if(auth.config['TESTING']):
        return tuple(login_task([request.get_json(), auth.config["SECRET_KEY"]], auth.config['session']))
    return tuple(login.delay([request.get_json(), auth.config["SECRET_KEY"]]).get())

@auth.route('/signup', methods=['POST'])
def signup_route():
    if(auth.config['TESTING']):
        return tuple(signup_task([request.get_json(), auth.config['SECRET_KEY']], auth.config['session']))
    return tuple(signup.delay([request.get_json(), auth.config['SECRET_KEY']]).get())

@auth.route('/logout', methods=['POST'])
def logout_route():
    if(auth.config['TESTING']):
        return tuple(logout_task([request.headers.get("Authorization"), auth.config['SECRET_KEY']], auth.config['session']))
    print(request.headers.get("Authorization"))
    return tuple(logout.delay([request.headers.get("Authorization"), auth.config['SECRET_KEY']]).get())

@auth.route('/status', methods=['POST'])
def status_route():
    if(auth.config['TESTING']):
        return tuple(status_route([request.headers.get("Authorization"), auth.config['SECRET_KEY']], auth.config['session']))
    return tuple(status.delay([request.headers.get("Authorization"), auth.config['SECRET_KEY']]).get())
