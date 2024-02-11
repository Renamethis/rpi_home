
import os
import pytest
from celery.exceptions import Retry
from unittest.mock import patch
from enviro_server.tasks import last_entries

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': os.getenv("REDIS_URL"),
        'result_backend': os.getenv("REDIS_URL")
    }

def test_last_entries():
    test_pointer = 0
    test_amount = 10
    assert last_entries.delay([int(test_pointer), int(test_amount),]).get() != 5