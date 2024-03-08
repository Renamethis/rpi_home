
import os
import pytest
import logging
from datetime import datetime
from unittest.mock import patch
from enviro_server.tasks import last_entries, current_state, by_date, load_weather
from enviro_server.EnvironmentData import CHANNELS, Units, Limits

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': os.getenv("REDIS_URL"),
        'result_backend': os.getenv("REDIS_URL")
    }

# TODO: Add testset with pointer bigger than amount
last_entries_test_set = ((20, 50), (2, 5))

def test_current_state():
    result = current_state.delay().get()
    assert len(result) != 0
    assert len(result) == CHANNELS + 1
    for key in result.keys():
        __test_record(key, result[key], True)

@pytest.mark.skip(reason="Not working - move to mock")
def test_by_date():
    date = last_entries.delay([0, 1, ]).get()[0]['datetime']
    assert date is not None
    result = by_date.delay([date, ]).get()
    assert result is not None
    assert len(result) == CHANNELS + 1
    for key in result:
        __test_record(key, result[key])

@pytest.mark.skip(reason="Not implemented")
def test_update_data_from_sensors():
    raise NotImplementedError

def test_last_entries():
    for test_set in last_entries_test_set:
        __test_last_entries(test_set[0], test_set[1])

def test_load_weather(): # TODO: Test Redis
    weather = load_weather.delay(("55.6961287", "37.5604322")).get()[0]
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
    assert time is not None
    if(precise):
        assert datetime.now().year == time.year
        assert datetime.now().month == time.month
        assert datetime.now().day == time.day
        assert datetime.now().hour == time.hour


def __test_last_entries(pointer, amount):
    result = last_entries.delay([int(pointer), int(amount),]).get()
    assert result is not None
    assert len(result) < amount * CHANNELS
    for entry in result:
        assert entry is not None