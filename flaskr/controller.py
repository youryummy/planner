from flask import Blueprint, request, Response
from dotenv import load_dotenv
from . import service
import logging
import jwt
import os

bp = Blueprint('planner', __name__)
logger = logging.getLogger(__name__)
load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')

@bp.route('/events', methods=['GET', 'POST', 'PUT'])
def event():
    auth_token = request.cookies.get('authToken')
    logger.info(f'Authtoken: {auth_token}')
    if auth_token is None:
        return Response(None, status=401)
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']
    logger.info(f'Processing request for user {username}')
    if request.method == 'POST':
        body = request.get_json()
        service.create_event(username, body)
        return Response(None, status=201)

    elif request.method == 'GET':
        return service.get_events(username)

    elif request.method == 'PUT':
        modified_event = request.get_json()
        service.update_event(username, modified_event)
        return Response(None, status=200)

@bp.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    auth_token = request.cookies.get('authToken')
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']

    service.delete_event(username, id)
    return Response(None, status=204)

@bp.route('/events/sync', methods=['POST'])
def login_with_google():
    '''auth_token = request.cookies.get('authToken')
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']'''
    username = 'javivm17'

    body = request.get_json()
    refresh_token = body['refreshToken']
    service.login_with_google(username, refresh_token)
    return Response(None, status=200)
    

@bp.route('/events/logout', methods=['GET'])
def logout_from_google():
    '''auth_token = request.cookies.get('authToken')
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']'''
    username = 'javivm17'

    service.logout_from_google(username)
    return Response(None, status=200)