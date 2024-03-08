import json
import pytest
from enviro_server import create_app
from enviro_server.database.models import User
from enviro_server.extensions import db

@pytest.fixture(scope="function")
def sqlalchemy_declarative_base():
    return db.Model

@pytest.fixture()
def app(mocked_session):
    app = create_app("testing")
    app.config.update({
        "session": mocked_session
    })
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# TODO: For database tests
# @pytest.fixture(scope="function")
# def sqlalchemy_mock_config():
#     return [("user", [
#         {
#             "nickname": "test_1",
#             "password": "test1"
#         },
#         {
#             "nickname": "test_2",
#             "password": "test2"
#         }
#     ])]

def test_decode_auth_token(mocked_session):
    user = User(
        nickname='nickname',
        password='test'
    )
    mocked_session.add(user)
    mocked_session.commit()
    auth_token = user.encode_auth_token(user.nickname)
    assert isinstance(auth_token, str)
    assert User.decode_auth_token(auth_token.encode("utf-8")) == 'nickname'

