from flask import Blueprint, request
from enviro_server.auth.tasks import signup_task, login_task

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return login_task.delay([request.get_json(), ]).get()

@auth.route('/signup', methods=['POST'])
def signup():
    return signup_task.delay([request.get_json(), ]).get()