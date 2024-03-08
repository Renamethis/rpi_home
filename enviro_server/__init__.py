import os
from flask import Flask
from config import config
from .extensions import db, celery, cors
from enviro_server.auth import auth
import configparser

# Flask factory
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    celery.init_app(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'application/json'
    app_config = configparser.ConfigParser()
    app_config.read("enviro_server/config.ini")
    app.app_config = app_config
    db.init_app(app)
    auth.config = app.config
    app.register_blueprint(auth, url_prefix="/auth")
    return app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')