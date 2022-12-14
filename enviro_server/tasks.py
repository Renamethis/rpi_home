from .extensions import celery, db
from enviro_server import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')