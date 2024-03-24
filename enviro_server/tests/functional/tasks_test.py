
import os
import pytest
from pytest_mock_resources import create_redis_fixture
import logging
import pathlib
from json import load, dumps
from datetime import datetime
from enviro_server.database.models import User
from enviro_server.EnvironmentData import EnvironmentData, EnvironmentValue, Limits
from enviro_server import create_app
from enviro_server.tasks import last_entries_task, current_state_task, by_date_task, load_weather_task
from enviro_server.extensions import db
from enviro_server.EnvironmentData import CHANNELS, Units, Limits

LOGGER = logging.getLogger(__name__)
ENVIRONMENT_DATA_PATH = pathlib.Path(__file__).parent.parent.resolve() / "resources" / "data_transform_resource.json"

redis = create_redis_fixture()

@pytest.fixture(scope="function")
def sqlalchemy_declarative_base():
    return db.Model

@pytest.fixture()
def app(mocked_session):
    app = create_app("testing")
    app.config.update({
        "session": mocked_session,
        "args": ["Bearer " + mocked_session.query(User).first().encode_auth_token("TEST_SECRET"),
                 "TEST_SECRET"]
    })
    return app

@pytest.fixture(scope="function")
def sqlalchemy_mock_config():
    resource_path = ENVIRONMENT_DATA_PATH
    with open(resource_path, "r") as resource:
        dict_data = load(resource)
        _raw_data = dict_data
        _data = [{"id" : entry["id"], "ptime" : datetime.strptime(entry["ptime"], '%Y-%m-%d %H:%M:%S.%f'),
                                                "value" : entry["value"], "field_name" : entry["field_name"],
                                                "unit": entry["unit"]}
                        for entry in dict_data]
        _users_data = [{"nickname": "testname", "is_admin": False, "registered_on": datetime.now(), "password": "test"}]
    return [("environment_record", _data), ("users", _users_data)]


token_args = []
# TODO: Add testset with pointer bigger than amount
last_entries_test_set = ((20, 50), (2, 5))

def test_current_state(app, redis, mocked_session):
    data = EnvironmentData(
            datetime.now(),
            EnvironmentValue(28, Units.TEMPERATURE, Limits["temperature"]),
            EnvironmentValue(970, Units.PRESSURE, Limits["pressure"]),
            EnvironmentValue(45, Units.HUMIDITY, Limits["humidity"]),
            EnvironmentValue(30, Units.ILLUMINATION, Limits["illumination"]),
            EnvironmentValue(20, Units.GAS, Limits["oxidizing"]),
            EnvironmentValue(700, Units.GAS, Limits["reducing"]),
            EnvironmentValue(80, Units.GAS, Limits["nh3"]),
            EnvironmentValue(80, Units.DUST, Limits["dust"])
    )
    redis.rpush('Data', data.serialize())
    result = current_state_task(app.config["args"] + [redis], mocked_session)
    assert len(result) != 0
    assert len(result) == CHANNELS + 1
    for key in result.keys():
        __test_record(key, result[key], True)

def test_by_date(app, mocked_session):
    date = last_entries_task(app.config["args"] + [0, 1], mocked_session)[0]['datetime']
    assert date is not None
    result = by_date_task(app.config["args"] + [date], mocked_session)
    assert result is not None
    assert len(result) == CHANNELS + 1
    for key in result:
        __test_record(key, result[key])

@pytest.mark.skip(reason="Not implemented")
def test_update_data_from_sensors():
    raise NotImplementedError

def test_last_entries(app, mocked_session):
    for test_set in last_entries_test_set:
        __test_last_entries(app, test_set[0], test_set[1], mocked_session)

def test_load_weather(app, redis, mocked_session):
    with open(pathlib.Path(__file__).parent.parent.resolve() / "resources" / "weather_data.json") as file:
        mock_weather = file.read()
        weather = load_weather_task(app.config["args"] + ["55.6961287", "37.5604322", mock_weather], mocked_session, True, redis)[0]
        assert weather["timezone"] == "Europe/Moscow"

def __test_record(key, value, precise=False):
    assert key is not None
    assert value is not None
    if(key != 'datetime'):
        assert value['unit'] in iter(Units)
        assert tuple(value['limits']) in Limits.values()
    else:
        __test_datetime(value, precise)

def __test_datetime(value, precise=False):
    try:
        time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        time = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    except TypeError:
        time = value
    assert time is not None
    if(precise):
        assert datetime.now().year == time.year
        assert datetime.now().month == time.month
        assert datetime.now().day == time.day


def __test_last_entries(app, pointer, amount, mocked_session):
    result = last_entries_task(app.config["args"] + [int(pointer), int(amount)], mocked_session)
    assert result is not None
    assert len(result) < amount * CHANNELS
    for entry in result:
        assert entry is not None