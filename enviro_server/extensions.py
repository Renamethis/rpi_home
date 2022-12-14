import flask
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from enviro_server.EnvironmentThread import EnvironmentThread

# Celery class extension for Flask
class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config)

# Define database and Celery objects
db = SQLAlchemy()
celery = FlaskCelery(
    'enviro_server',
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["enviro_server.routes"]
)
cors = CORS()
enviroThread = EnvironmentThread()
enviroThread.start()