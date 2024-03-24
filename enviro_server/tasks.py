import os
from json import loads
from enviro_server import app

if not app.config["TESTING"]:
    from .extensions import celery, db, redis_client

from enviro_server.auth.tasks import token_required
from celery.signals import worker_ready
from .EnvironmentData import Units, EnvironmentData
from .database.models import EnvironmentUnitModel, EnvironmentRecordModel, User
from .transform_utils import transform_data, calculate_slices
from celery.utils.log import get_task_logger
if not app.config["TESTING"]:
    from .EnvironmentThread import EnvironmentThread
    from .LedMatrix import MatrixThread
from requests import get

if(os.getenv("UNITTEST_ENVIRONMENT") is None):
    celery.conf.beat_schedule = {
        'update_task': {
            'task': 'enviro_server.tasks.update_data_from_sensors',
            'schedule': 5.0,
        },
        'weather_task': {
            'task': 'enviro_server.tasks.load_weather',
            'schedule': 100.0,
        },
    }
    celery.conf.timezone = 'UTC'
    logger = get_task_logger(__name__)

@worker_ready.connect
def initialize(sender, **k):
    with app.app_context():
        app.matrix = MatrixThread(not bool(app.app_config['Devices']['matrix_with_lcd']), redis_client)
        app.matrix.start()
        app.interface = EnvironmentThread(redis_client)
        app.interface.start()
        if(not EnvironmentUnitModel.query.first()):
            for unit in Units:
                new_entry = EnvironmentUnitModel(
                    type = unit.name.lower(),
                    unit = unit.value
                )
                db.session.add(new_entry)
            db.session.commit()
        if(not User.query.filter_by(nickname="WeatherAdmin").first()): # TODO: Maybe move to init.sql?
            weather_admin = User(
                nickname = "WeatherAdmin",
                password = os.getenv("ADMIN_PASSWORD"),
                admin=True
            ) # TODO: Somehow generate token and sync it with app
            db.session.add(weather_admin)
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
    by_date_task(args, db.session)


@celery.task
def current_state(args):
    args.append(redis_client)
    return current_state_task(args, db.session)

@celery.task
def last_entries(args):
    return last_entries_task(args, db.session)

@celery.task
def load_weather(args):
    return load_weather_task(args, False, redis_client)

@token_required
def last_entries_task(args, session):
    with app.app_context():
        last_entries = session.query(EnvironmentRecordModel) \
            .order_by(EnvironmentRecordModel.ptime.desc())
        startSlice, endSlice, amount = calculate_slices(args[2:], last_entries.count())
        return transform_data(last_entries.slice(startSlice, endSlice), amount)

@token_required
def load_weather_task(args, session, testing, client):
    url = os.getenv("WEATHER_API_URL") + "?lat=" + args[2] + "&lon=" + args[3] + "&appid=" + os.getenv("WEATHER_API_KEY")
    try:
        if(not testing):
            response = get(url).content
        else:
            response = args[4]
        client.rpush('Weather', response)
        return loads(response), 200
    except Exception as e:
        return {
            "Error": str(e)
        }, e.status_code

@token_required
def by_date_task(args, session):
    with app.app_context():
        sorted_by_date =  session.query(EnvironmentRecordModel).filter_by(ptime=args[2])
        return transform_data(sorted_by_date, 1)[0]

@token_required
def current_state_task(args, session):
    with app.app_context():
        return EnvironmentData.from_message(args[2].lrange('Data', -1, -1)[0]).dict