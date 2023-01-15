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

def test_post_in_db(client, monkeypatch):
    token = jwt.encode({'username': 'user_test', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "id": "1",
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    body = {
        "timestamp": 3471698180,
        "id": "1"
    }

    response = client.post('/api/v1/events', json=body)
    assert response.status_code == 201

def test_get_in_db(client, monkeypatch):
    token = jwt.encode({'username': 'user_test', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "_id": "1",
        "name": "test",
        "summary": "test",
        "tags": ["test"],
        "imageUrl": "https://spoonacular.com/recipeImages/1-556x370.jpg"
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    response = client.get('/api/v1/events')
    assert response.status_code == 200

def test_put_in_db(client, monkeypatch):
    token = jwt.encode({'username': 'user_test', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)

    recipes_stub = Mock()
    recipes_stub.return_value = {
        "_id": "1",
        "name": "test",
        "summary": "test",
        "tags": ["test"],
        "imageUrl": "https://spoonacular.com/recipeImages/1-556x370.jpg"
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    test_events = client.get('/api/v1/events')
    test_events = test_events.get_json()
    id = test_events['events'][0]["id"]

    body = {
        "timestamp": 1736526673,
        "id": id,
        "synced": False
    }

    response = client.put('/api/v1/events', json=body)
    assert response.status_code == 200

def test_delete_in_db(client, monkeypatch):
    token = jwt.encode({'username': 'user_test', 'plan': 'base'}, JWT_SECRET, algorithm='HS256')
    client.set_cookie('localhost', 'authToken', token)
    
    recipes_stub = Mock()
    recipes_stub.return_value = {
        "_id": "1",
        "name": "test",
        "summary": "test",
        "tags": ["test"],
        "imageUrl": "https://spoonacular.com/recipeImages/1-556x370.jpg"
    }

    monkeypatch.setattr('flaskr.controller.service.utils.communicate', recipes_stub)

    test_events = client.get('/api/v1/events')
    test_events = test_events.get_json()
    id = test_events['events'][0]["id"]

    response = client.delete('/api/v1/events/' + id)
    assert response.status_code == 204
    