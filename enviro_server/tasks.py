from .extensions import celery, db, redis_client
from . import create_app
from celery.signals import task_prerun
import os
from celery.signals import worker_ready
from .EnvironmentData import Units, EnvironmentData
from .database.models import EnvironmentUnitModel, EnvironmentRecordModel
from .transform_utils import transform_data, calculate_slices
from celery.utils.log import get_task_logger
from .EnvironmentThread import EnvironmentThread
from .LedMatrix import MatrixThread
from json import dump

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
if(os.getenv("UNITTEST_ENVIRONMENT") is None):
    celery.conf.beat_schedule = {
        'update_task': {
            'task': 'enviro_server.tasks.update_data_from_sensors',
            'schedule': 30.0,
        },
    }
    celery.conf.timezone = 'UTC'
    logger = get_task_logger(__name__)

@worker_ready.connect
def initialize(sender, **k):
    with app.app_context():
        app.interface = EnvironmentThread(redis_client)
        app.interface.start()
        app.matrix = MatrixThread()
        app.matrix.start()
        if(not EnvironmentUnitModel.query.first()):
            for unit in Units:
                new_entry = EnvironmentUnitModel(
                    type = unit.name.lower(),
                    unit = unit.value
                )
                db.session.add(new_entry)
            db.session.commit()


@celery.task
def update_data_from_sensors():
    with app.app_context():
        data = redis_client.lrange('Data', -1, -1)
        data = EnvironmentData.from_message(data[0]).dict
        last = EnvironmentRecordModel.query. \
            order_by(EnvironmentRecordModel.id.desc()).first()
        current_id = 0 if last is None else last.id + 1
        time = data['datetime']
        for key in data:
            if(key == 'datetime'):
                continue
            unit = EnvironmentUnitModel.query.\
                   filter_by(type = data[key]['unit'].name.lower())[0].type
            new_entry = EnvironmentRecordModel(
                id=current_id,
                ptime=time,
                field_name=key,
                unit=unit,
                value=data[key]['value'],
            )
            db.session.add(new_entry)
            current_id += 1
        db.session.commit()

@celery.task
def by_date(args):
    with app.app_context():
        sorted_by_date =  EnvironmentRecordModel.query.filter_by(ptime=args[0])
        return transform_data(sorted_by_date, 1)[0]


@celery.task
def current_state():
    with app.app_context():
        return EnvironmentData.from_message(redis_client.lrange('Data', -1, -1)[0]).dict


@celery.task
def last_entries(args):
    with app.app_context():
        last_entries = EnvironmentRecordModel.query \
            .order_by(EnvironmentRecordModel.ptime.desc())
        with open("data_transform_resource.json", "w") as file:
            dump([entry.to_dict() for entry in last_entries], file, indent=4, sort_keys=True, default=str)
        startSlice, endSlice, amount = calculate_slices(args, last_entries.count())
        return transform_data(last_entries.slice(startSlice, endSlice), amount)