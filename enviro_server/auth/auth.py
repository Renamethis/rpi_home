from flask import Blueprint, request
from enviro_server.extensions import db
from enviro_server.auth.tasks import signup_task

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return 'Login'

@auth.route('/signup', methods=['POST'])
def signup():
    return signup_task(request).delay().get()

@auth.route('/logout')
def logout():
    return 'Logout'