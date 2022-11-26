from flask import Blueprint, request, Response
from . import service

bp = Blueprint('planner', __name__)

@bp.route('/events', methods=['GET', 'POST', 'PUT'])
def event():
    # username = request.cookies.get('username')
    username = 'user2'
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
    # username = request.cookies.get('username')
    username = 'user2'
    service.delete_event(username, id)
    return Response(None, status=204)