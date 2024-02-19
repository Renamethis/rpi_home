import os
from flask import Flask
from config import config
from .extensions import db, celery, cors
import configparser

# Flask factory
def create_app(config_name):
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read("enviro_server/config.ini")
    app.app_config = config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    celery.init_app(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'application/json'
    return app
