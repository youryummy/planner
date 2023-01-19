import pytest
from flaskr import create_app
from unittest.mock import Mock
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')

@pytest.fixture
def app():
    app = create_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_health(client):
    response = client.get('/')
    assert response.status_code == 200

def test_swagger_schema(client):
    response = client.get('/docs/swagger.json')
    assert response.status_code == 200
    assert response.json['info']['title'] == 'Planner Service'

############################################################################################################
############################################ GET TESTS ##################################################
############################################################################################################

def test_get_events_without_auth(client):
    response = client.get('/api/v1/events')
    assert response.status_code == 401

def test_get_events_with_auth(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value ={
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 1578243461
            }
        ],
        }
    }
    logged_in_stub = Mock()
    logged_in_stub.return_value = "auth_token"

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "_id": "1",
        "name": "test",
        "summary": "test",
        "tags": ["test"],
        "imageUrl": "https://spoonacular.com/recipeImages/1-556x370.jpg",
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)
    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 200
    assert response.json['isLogged'] == True

def test_get_events_with_auth_and_no_events_exists_in_db(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value = None

    logged_in_stub = Mock()
    logged_in_stub.return_value = "auth_token"

    monkeypatch.setattr('flaskr.controller.service.firebase.get' , events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)
    
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 200
    assert response.json['isLogged'] == True

def test_get_events_with_auth_and_no_events(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value = events_stub.return_value ={
        "-NJioAHojZF1Plwd4QC3": {
        "javivm17": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    logged_in_stub = Mock()
    logged_in_stub.return_value = "auth_token"

    monkeypatch.setattr('flaskr.controller.service.firebase.get' , events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)
    
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 200
    assert response.json['isLogged'] == True

def test_get_events_with_auth_and_user_not_logged_in(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value = None

    logged_in_stub = Mock()
    logged_in_stub.return_value = None

    monkeypatch.setattr('flaskr.controller.service.firebase.get' , events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)
    
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 200
    assert response.json['isLogged'] == False

def test_get_events_with_auth_and_fail_to_connect_with_recipes(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value ={
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 1578243461
            }
        ],
        }
    }
    logged_in_stub = Mock()
    logged_in_stub.return_value = "auth_token"

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)

    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 500
    assert response.json['message'] == 'Failed to communicate with recipes service'

def test_get_events_with_auth_and_an_invalid_recipe(client, monkeypatch):
    events_stub = Mock()
    events_stub.return_value ={
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 1578243461
            }
        ],
        }
    }
    logged_in_stub = Mock()
    logged_in_stub.return_value = "auth_token"

    recipes_stub = Mock()
    recipes_stub.return_value = None

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', logged_in_stub)
    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    response = client.get('/api/v1/events')
    assert response.status_code == 200

############################################################################################################
############################################ CREATE TESTS ##################################################
############################################################################################################

def test_create_event_with_auth_and_no_data(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {}
    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_valid_data(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)


    recipes_stub = Mock()
    recipes_stub.return_value = {
        "id": "1",
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 1737250585,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 201

def test_create_event_with_auth_and_old_timestamp(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 100,
        "id": "1"
    }
    
    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_invalid_timestamp_type(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": "3471698180",
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_no_provided_id(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 3471698180
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_invalid_id(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 3471698180,
        "id": 12
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_invalid_recipe(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)


    recipes_stub = Mock()
    recipes_stub.return_value = None

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 1737250585,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400


def test_create_event_with_auth_and_valid_data_for_user_with_events(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "id": "1",
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 1737250585,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 201
    
def test_create_event_with_auth_and_no_data(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {}
    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_valid_data(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "id": "1",
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 1737250585,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 201

def test_create_event_with_auth_and_old_timestamp(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 100,
        "id": "1"
    }
    
    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_invalid_timestamp_type(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": "3471698180",
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_no_provided_id(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 1737250585
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_invalid_id(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 1737250585,
        "id": 12
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 400

def test_create_event_with_auth_and_valid_data_and_fail_to_connect_with_recipes(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    body = {
        "timestamp": 1737250585,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 500
    assert response.json['message'] == 'Failed to communicate with recipes service'

############################################################################################################
############################################ UPDATE TESTS ##################################################
############################################################################################################

def test_update_event_with_auth_and_no_data(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {}
    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_valid_data_timestamp(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": False
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 200

def test_update_event_with_auth_and_valid_data_synced_and_logged_in_google(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 1737250585
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    check_user_stub = Mock()
    check_user_stub.return_value = "refreshtoken"
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', check_user_stub)

    build_stub = Mock()
    build_stub.return_value = True
    monkeypatch.setattr('flaskr.controller.service.build', build_stub)

    service_stub = Mock()
    service_stub.return_value = {}
    monkeypatch.setattr('flaskr.controller.service.insert_event_in_google_calendar', service_stub)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "_id": "1",
        "name": "test",
        "summary": "test",
        "tags": ["test"],
        "imageUrl": "https://spoonacular.com/recipeImages/1-556x370.jpg",
    }
    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 200

def test_update_event_with_auth_and_valid_data_synced_and_not_logged_in_google(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    check_user_stub = Mock()
    check_user_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', check_user_stub)

    build_stub = Mock()
    build_stub.return_value = True
    monkeypatch.setattr('flaskr.controller.service.build', build_stub)

    service_stub = Mock()
    service_stub.return_value = {}
    monkeypatch.setattr('flaskr.controller.service.insert_event_in_google_calendar', service_stub)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_valid_data_synced_for_event_synced(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": True,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": True,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    check_user_stub = Mock()
    check_user_stub.return_value = "refreshtoken"
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', check_user_stub)

    build_stub = Mock()
    build_stub.return_value = True
    monkeypatch.setattr('flaskr.controller.service.build', build_stub)

    service_stub = Mock()
    service_stub.return_value = {}
    monkeypatch.setattr('flaskr.controller.service.insert_event_in_google_calendar', service_stub)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_valid_data_synced_for_non_exists_event(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    check_user_stub = Mock()
    check_user_stub.return_value = "refreshtoken"
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', check_user_stub)

    build_stub = Mock()
    build_stub.return_value = True
    monkeypatch.setattr('flaskr.controller.service.build', build_stub)

    service_stub = Mock()
    service_stub.return_value = {}
    monkeypatch.setattr('flaskr.controller.service.insert_event_in_google_calendar', service_stub)

    body = {
        "timestamp": 1737250585,
        "id": "inventedid",
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_no_event_id_provided(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 1737250585,
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_id_no_valid(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 1737250585,
        "id": 12123,
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_no_synced_provided(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06"
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_synced_no_boolean(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {    
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": "true"
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 400

def test_update_event_with_auth_and_valid_data_synced_and_logged_in_google_and_fail_to_connect_with_recipes(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": "1",
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    check_user_stub = Mock()
    check_user_stub.return_value = "refreshtoken"
    monkeypatch.setattr('flaskr.controller.service.check_user_logged_in', check_user_stub)

    build_stub = Mock()
    build_stub.return_value = True
    monkeypatch.setattr('flaskr.controller.service.build', build_stub)

    service_stub = Mock()
    service_stub.return_value = {}
    monkeypatch.setattr('flaskr.controller.service.insert_event_in_google_calendar', service_stub)

    body = {
        "timestamp": 1737250585,
        "id": "6d0cde4325df4821afd2d71153f4ae06",
        "synced": True
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 500
    assert response.json['message'] == 'Failed to communicate with recipes service'

############################################################################################################
############################################ DELETE TESTS ##################################################
############################################################################################################

def test_delete_event_with_no_auth(client, monkeypatch):
    response = client.delete('/api/v1/events/1')
    assert response.status_code == 401

def test_delete_event_with_auth_and_event_exists(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    events_stub = Mock()
    events_stub.return_value = {
        "-NJioAHojZF1Plwd4QC3": {
        "maribelrb": [
            {
                "id": "6d0cde4325df4821afd2d71153f4ae06",
                "recipe": {"id":"1"},
                "synced": False,
                "timestamp": 3471698180
            },
            {
                "id": "612dd6ffb76744a2951ca14e0755d7d7",
                "recipe": {"id":"1"},
                "synced": False,
                "timestamp": 3471698180
            }
        ],
        }
    }

    monkeypatch.setattr('flaskr.controller.service.firebase.get', events_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    response = client.delete('/api/v1/events/6d0cde4325df4821afd2d71153f4ae06')
    assert response.status_code == 204

############################################################################################################
############################################ GOOGLE TESTS ##################################################
############################################################################################################   

def test_post_google_login_without_auth(client):
    response = client.post('/api/v1/events/sync')
    assert response.status_code == 401

def test_post_google_login_with_auth_and_no_users_are_logged(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    user_get_stub = Mock()
    user_get_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', user_get_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    body = {
        "refreshToken": "refreshToken"
    }

    response = client.post('/api/v1/events/sync', json=body)
    assert response.status_code == 200

def test_post_google_login_with_auth_and_users_are_logged(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    user_get_stub = Mock()
    user_get_stub.return_value = {
        "-NL0UNZwgVjJxq0dUxQK": {
            "javivm17": "refreshToken"
        }
    }
    monkeypatch.setattr('flaskr.controller.service.firebase.get', user_get_stub)

    post_stub = Mock()
    post_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.post', post_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    body = {
        "refreshToken": "refreshToken"
    }

    response = client.post('/api/v1/events/sync', json=body)
    assert response.status_code == 200

def test_post_google_login_with_auth_and_no_refresh_token_provided(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {}

    response = client.post('/api/v1/events/sync', json=body)
    assert response.status_code == 400

def test_post_google_login_with_auth_and_no_valid_refresh_token_provided(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "refreshToken": 213123
    }

    response = client.post('/api/v1/events/sync', json=body)
    assert response.status_code == 400

def test_post_google_login_with_auth_and_base_plan(client):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    body = {
        "refreshToken": "refreshToken"
    }

    response = client.post('/api/v1/events/sync', json=body)
    assert response.status_code == 401


def test_get_google_logout_without_auth(client):
    response = client.get('/api/v1/events/logout')
    assert response.status_code == 401

def test_get_google_logout_with_auth_and_no_users_are_logged(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    user_get_stub = Mock()
    user_get_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.get', user_get_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    response = client.get('/api/v1/events/logout')
    assert response.status_code == 200

def test_get_google_logout_with_auth_and_users_are_logged(client, monkeypatch):
    token = jwt.encode({'username': 'maribelrb', 'plan': 'premium'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    user_get_stub = Mock()
    user_get_stub.return_value = {
        "-NL0UNZwgVjJxq0dUxQK": {
            "javivm17": "refreshToken"
        }
    }
    monkeypatch.setattr('flaskr.controller.service.firebase.get', user_get_stub)

    put_stub = Mock()
    put_stub.return_value = None
    monkeypatch.setattr('flaskr.controller.service.firebase.put', put_stub)

    response = client.get('/api/v1/events/logout')
    assert response.status_code == 200
