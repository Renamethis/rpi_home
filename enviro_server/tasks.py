from .extensions import celery, db, redis_client
from . import create_app
from celery.signals import task_prerun
import os
from celery.signals import worker_ready
from .EnvironmentData import Units, EnvironmentData
from .database.models import EnvironmentUnitModel
from celery.utils.log import get_task_logger
from .EnvironmentThread import EnvironmentInterface

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery.conf.beat_schedule = {
    'update_task': {
        'task': 'enviro_server.tasks.update_data_from_sensors',
        'schedule': 1.0,
    },
}
celery.conf.timezone = 'UTC'
logger = get_task_logger(__name__)

@worker_ready.connect
def initialize(sender, **k):
    with app.app_context():
        app.interface = EnvironmentInterface(redis_client)
        app.interface.start()
        for unit in Units:
            new_entry = EnvironmentUnitModel(
                field_name = unit.name.lower(),
                unit = unit.value
            )
            db.session.add(new_entry)
        db.session.commit()


@celery.task
def update_data_from_sensors():
    with app.app_context():
        logger.info("TEST")
        data = redis_client.lrange('Data', -1, -1)
        data = EnvironmentData.from_message(data[0])
        print(data.serialize())
