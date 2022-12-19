from dotenv import load_dotenv
from firebase import firebase
import os
from . import utils
import uuid

load_dotenv()
database_url = os.getenv('DATABASE_URL')
firebase = firebase.FirebaseApplication(database_url, None)

def get_firebase_events(username):
    events = firebase.get('/events', None)
    events_id = None
    if events is not None:
        events_id = list(events)[0]
        events = events[events_id]
    else:
        return None, None
    if username not in events:
        events[username] = []
    return events, events_id

def create_event(username, body):
    events, events_id = get_firebase_events(username)

    exist_events = True
    if events is None:
        exist_events = False
        events = {username: []}

    my_events = events[username]
    new_event = {
        "id": uuid.uuid4().hex,
        "timestamp": body["timestamp"],
        "synced": False,
        "recipe": body["id"]
    }
    my_events.append(new_event)
    events[username] = my_events

    if not exist_events:
        firebase.post('/events', events)
    else:
        firebase.put('/events', events_id, events)

def get_events(username):
    events, _ = get_firebase_events(username)
    my_events = events[username]
    detailed_events = []
    for event in my_events:
        # detailed_recipe = utils.communicate('GET', "".join(['http://localhost:5001/api/v1/recipes/', event['recipe']]), None, username)
        detailed_recipe = {
            "id": 1,
            "name": "recipe1",
            "description": "recipe1 description",
            "tags": ["tag1","tag2"],
            "ingredients": [
                {
                    "id": 1,
                    "name": "ingredient1",
                    "quantity": 1,
                },
                {
                    "id": 2,
                    "name": "ingredient2",
                    "quantity": 2,
                }
            ],
        }
        detailed_event = {
            'id': event['id'],
            'timestamp': event['timestamp'],
            'synced': event['synced'],
            'recipe': detailed_recipe
        }
        detailed_events.append(detailed_event)
    return detailed_events

def update_event(username, modified_event):
    events, events_id = get_firebase_events(username)
    my_events = events[username]
    for event in my_events:
        if event['id'] == modified_event['id']:
            if modified_event['synced']:
                # communicate with Google Calendar API
                pass
            event['synced'] = modified_event['synced']
            event['timestamp'] = modified_event['timestamp']
            break
    events[username] = my_events
    firebase.put('/events', events_id, events)

def delete_event(username, id):
    events, events_id = get_firebase_events(username)
    my_events = events[username]
    for event in my_events:
        if event['id'] == id:
            my_events.remove(event)
            break
    events[username] = my_events
    firebase.put('/events', events_id, events)