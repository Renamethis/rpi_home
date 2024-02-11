import os

if os.getenv("UNITTEST_ENVIRONMENT") is None:
    from flask import Flask
    from config import config
    from .extensions import db, celery, cors

    # Flask factory
    def create_app(config_name):
        app = Flask(__name__)
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        db.init_app(app)
        celery.init_app(app)
        cors.init_app(app, resources={r"*": {"origins": "*"}})
        app.config['CORS_HEADERS'] = 'application/json'
        return app
