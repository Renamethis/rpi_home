from .extensions import celery, db, redis_client
from . import create_app
from celery.signals import task_prerun
import os
from celery.signals import worker_ready
from .EnvironmentData import Units, EnvironmentData, CHANNELS, Limits
from .database.models import EnvironmentUnitModel, EnvironmentRecordModel
from celery.utils.log import get_task_logger
from .EnvironmentThread import EnvironmentInterface
from datetime import datetime

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
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
        app.interface = EnvironmentInterface(redis_client)
        app.interface.start()
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
        data = EnvironmentData.from_message(data[0]).get_dict()
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
        return __transform_data(sorted_by_date, 1)[0]


@celery.task
def current_state():
    with app.app_context():
        return EnvironmentData.from_message(redis_client.lrange('Data', -1, -1)[0]).get_dict()


@celery.task
def last_entries(args):
    with app.app_context():
        last_entries = EnvironmentRecordModel.query \
            .order_by(EnvironmentRecordModel.ptime.desc()) \
            .slice(args[0] * CHANNELS, args[1] * CHANNELS)
        return __transform_data(last_entries, args[1])

def __transform_data(entries, amount):
        timebuf = list([str(entries[i*8].ptime) for i in range(0, amount)]) # TODO: Simplify
        result = [{entry.field_name: \
                {key: value for key, value in entry.to_dict().items() \
                    if key != "field_name" and key != "ptime"} \
            for entry in entries[i*8:i*8 + 8]} \
                for i in range(0, amount)]
        cnt = 0
        for entry in result:
            for key in entry:
                entry[key]['limits'] = Limits[key]
                entry[key]['unit'] = Units[entry[key]['unit'].upper()]
            entry['datetime'] = timebuf[cnt]
            cnt += 1
        return result
