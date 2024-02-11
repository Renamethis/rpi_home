
import os
import pytest
from celery.exceptions import Retry
from unittest.mock import patch
from enviro_server.tasks import last_entries
from enviro_server.EnvironmentData import CHANNELS

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': os.getenv("REDIS_URL"),
        'result_backend': os.getenv("REDIS_URL")
    }

# TODO: Add testset with pointer bigger than amount
last_entries_test_set = ((20, 50), (2, 5))

def test_last_entries():
    for test_set in last_entries_test_set:
        __test_last_entries(test_set[0], test_set[1])

def __test_last_entries(pointer, amount):
    result = last_entries.delay([int(pointer), int(amount),]).get()
    assert result is not None
    assert len(result) < amount * CHANNELS
    for entry in result:
        assert entry is not None