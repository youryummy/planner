from flask import Blueprint, request, Response
from dotenv import load_dotenv
from . import service
import logging
import jwt
import os
from . import utils
import json

bp = Blueprint('planner', __name__)
logger = logging.getLogger(__name__)
load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')


@bp.route('/events', methods=['GET', 'POST', 'PUT'])
def event():
    auth_token = request.cookies.get('authToken')
    logger.info(f'auth_token: {auth_token}')
    if auth_token is None:
        resp = json.dumps({'message': 'Unauthorized'})
        return Response(resp, status=401, mimetype='application/json')
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']
    logger.info(f'Processing request for user {username}')
    
    if request.method == 'POST':
        body = request.get_json()
        is_valid, message = utils.validate_event(body, 'POST')
        if not is_valid:
            resp = json.dumps({'message': message})
            return Response(resp, status=400, mimetype='application/json')
        created, message, *error_code = service.create_event(username, body)
        if not created:
            resp = json.dumps({'message': message})
            if len(error_code) == 0:
                return Response(resp, status=400, mimetype='application/json')
            return Response(resp, status=error_code[0], mimetype='application/json')
        return Response(None, status=201)

    elif request.method == 'GET':
        events = service.get_events(username)
        if type(events) is str:
            resp = json.dumps({'message': events})
            return Response(resp, status=500, mimetype='application/json')
        return events

    elif request.method == 'PUT':
        modified_event = request.get_json()
        is_valid, message = utils.validate_event(modified_event, 'PUT')
        if not is_valid:
            resp = json.dumps({'message': message})
            return Response(resp, status=400, mimetype='application/json')
        modified, message, *error_code = service.update_event(username, modified_event)
        if not modified:
            resp = json.dumps({'message': message})
            if len(error_code) == 0:
                return Response(resp, status=400, mimetype='application/json')
            return Response(resp, status=error_code[0], mimetype='application/json')
        return Response(None, status=200)


@bp.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    auth_token = request.cookies.get('authToken')
    if auth_token is None:
        return Response(None, status=401)
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']
    logger.info(f'Processing request for user {username}')

    service.delete_event(username, id)
    return Response(None, status=204)


@bp.route('/events/sync', methods=['POST'])
def login_with_google():
    auth_token = request.cookies.get('authToken')
    if auth_token is None:
        return Response(None, status=401)
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']
    logger.info(f'Processing request for user {username}')

    body = request.get_json()
    is_valid, refresh_token_or_message = utils.validate_refresh_token(body)
    if not is_valid:
        resp = json.dumps({'message': refresh_token_or_message})
        return Response(resp, status=400, mimetype='application/json')
    service.login_with_google(username, refresh_token_or_message)
    return Response(None, status=200)


@bp.route('/events/logout', methods=['GET'])
def logout_from_google():
    auth_token = request.cookies.get('authToken')
    if auth_token is None:
        return Response(None, status=401)
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']
    logger.info(f'Processing request for user {username}')

    service.logout_from_google(username)
    return Response(None, status=200)
