from flask import Blueprint, request
from enviro_server.auth.tasks import signup_task, login_task

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    response = login_task.delay([request.get_json(), ]).get()
    return response[0], response[1]

@auth.route('/signup', methods=['POST'])
def signup():
    response = signup_task.delay([request.get_json(), ]).get()
    return response[0], response[1]