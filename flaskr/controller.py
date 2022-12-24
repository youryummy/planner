from flask import Blueprint, request, Response
from flask_cors import cross_origin
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
@cross_origin()
def event():
    # auth_token = request.cookies.get('authToken')
    # encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    # username = encoded_jwt['username']
    # logger.info(f'Processing request for user {username}')
    username = 'user1'
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
@cross_origin()
def delete_event(id):
    auth_token = request.cookies.get('authToken')
    encoded_jwt = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
    username = encoded_jwt['username']

    service.delete_event(username, id)
    return Response(None, status=204)