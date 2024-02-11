import os
from flask import Flask
from config import config
from .extensions import db, celery, cors

# Flask factory
def create_app(config_name):
    if(os.getenv("UNITTEST_ENVIRONMENT") is None):
        app = Flask(__name__)
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        db.init_app(app)
        celery.init_app(app)
        cors.init_app(app, resources={r"*": {"origins": "*"}})
        app.config['CORS_HEADERS'] = 'application/json'
        return app
    return None
