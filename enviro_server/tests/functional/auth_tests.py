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
        "session": mocked_session,
        "SECRET_KEY": "TEST_KEY"
    })
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_decode_auth_token(mocked_session):
    user = User(
        nickname='nickname',
        password='test'
    )
    mocked_session.add(user)
    mocked_session.commit()
    auth_token = user.encode_auth_token("TEST_SECRET", user.nickname)
    assert isinstance(auth_token, str)
    result, _ = User.decode_auth_token("TEST_SECRET", auth_token.encode("utf-8"), mocked_session)
    assert result == 'nickname'

def test_registration(client):
    with client:
        response = client.post(
            '/auth/signup',
            data=json.dumps(dict(
                nickname='nickname',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Successfully registered.'
        assert data['auth_token']
        assert response.content_type == 'application/json'
        assert response.status_code, 201

def test_registered_with_already_registered_user(client, mocked_session):
    user = User(
        nickname='test',
        password='test'
    )
    mocked_session.add(user)
    mocked_session.commit()
    with client:
        response = client.post(
            '/auth/signup',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'fail'
        assert data['message'] == 'User already exists. Please Log in.'
        assert response.content_type == 'application/json'
        assert response.status_code, 202

def test_registered_user_login(client):
    with client:
        # user registration
        resp_register = client.post(
            '/auth/signup',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json',
        )
        data_register = json.loads(resp_register.data.decode())
        assert data_register['status'] == 'success'
        assert data_register['message'] == 'Successfully registered.'
        assert data_register['auth_token']
        assert resp_register.content_type == 'application/json'
        assert resp_register.status_code, 201
        response = client.post(
            '/auth/login',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Successfully logged in.'
        assert data['auth_token']
        assert response.content_type == 'application/json'
        assert response.status_code, 200

def test_non_registered_user_login(client):
    with client:
        response = client.post(
            '/auth/login',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'fail'
        assert data['message'] == 'User does not exist.'
        assert response.content_type == 'application/json'
        assert response.status_code, 404

def test_valid_logout(client):
    with client:
        resp_register = client.post(
            '/auth/signup',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json',
        )
        data_register = json.loads(resp_register.data.decode())
        assert data_register['status'] == 'success'
        assert data_register['message'] == 'Successfully registered.'
        assert data_register['auth_token']
        assert resp_register.content_type == 'application/json'
        assert resp_register.status_code, 201

        resp_login = client.post(
            '/auth/login',
            data=json.dumps(dict(
                nickname='test',
                password='123456'
            )),
            content_type='application/json'
        )
        data_login = json.loads(resp_login.data.decode())
        assert data_login['status'] == 'success'
        assert data_login['message'] == 'Successfully logged in.'
        assert data_login['auth_token']
        assert resp_login.content_type == 'application/json'
        assert resp_login.status_code, 200
        response = client.post(
            '/auth/logout',
            headers=dict(
                Authorization='Bearer ' + json.loads(
                    resp_login.data.decode()
                )['auth_token']
            )
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Successfully logged out.'
        assert response.status_code == 200
