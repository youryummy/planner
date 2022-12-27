from dotenv import load_dotenv
from firebase import firebase
import os
from . import utils
import uuid
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging
import datetime

load_dotenv()
database_url = os.getenv('DATABASE_URL')
firebase = firebase.FirebaseApplication(database_url, None)

logger = logging.getLogger(__name__)

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
    # check data before upload to firebase
    events, _ = get_firebase_events(username)
    my_events = events[username]
    detailed_events = []
    for event in my_events:
        if event is not None and datetime.datetime.fromtimestamp(int(event['timestamp'])) < datetime.datetime.now():
            continue
        else:
            # detailed_recipe = utils.communicate('GET', "".join(['http://localhost:5001/api/v1/recipes/', event['recipe']]), None, username)
            detailed_recipe = {
                "id": "1",
                "name": "recipe1",
                "description": "recipe1 description",
                "tags": ["tag1", "tag2"],
                "ingredients": [
                    {
                        "id": "1",
                        "name": "ingredient1",
                        "quantity": 1,
                    },
                    {
                        "id": "2",
                        "name": "ingredient2",
                        "quantity": 2,
                    }
                ],
            }
            detailed_event = {
                'id': event['id'],
                'timestamp': int(event['timestamp']),
                'synced': event['synced'],
                'recipe': detailed_recipe
            }
            detailed_events.append(detailed_event)
    is_logged = check_user_logged_in(username)
    response = {
        "isLogged": True if is_logged is not None else False, 
        "events": detailed_events
    }
    return response


def update_event(username, modified_event):
    # check data before upload to firebase
    events, events_id = get_firebase_events(username)
    my_events = events[username]
    for event in my_events:
        if event is not None and event['id'] == modified_event['id']:
            if 'timestamp' in modified_event:
                event['timestamp'] = modified_event['timestamp']
            if 'synced' in modified_event and modified_event['synced'] is True:
                sync_with_google_calendar(username, modified_event)
                event['synced'] = modified_event['synced']
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

def sync_with_google_calendar(username, event):
    SCOPE= ['https://www.googleapis.com/auth/calendar']
    
    refresh_token = check_user_logged_in(username)
    if refresh_token is not None:
        credentials = {
            "token": None,
            "refresh_token": refresh_token,
            "client_id": os.getenv('CLIENT_ID'),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_secret": os.getenv('CLIENT_SECRET'),
            "scopes": SCOPE
        }
        creds = Credentials.from_authorized_user_info(credentials, SCOPE)
        logger.info('Credentials are valid')
        service = build('calendar', 'v3', credentials=creds)
        
        # TODO: call recipes api
        event = {
            'summary': 'Google I/O 2015',
            'location': '800 Howard St., San Francisco, CA 94103',
            'description': 'A chance to hear more about Google\'s developer products.',
            'start': {
                'dateTime': '2022-12-28T09:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2022-12-28T17:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            }
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        logger.info('Event created: %s' % (event.get('htmlLink')))

def login_with_google(username, refresh_token):
    users = firebase.get('/users', None)
    users_id = None
    print(users)
    if users is not None:
        users_id = list(users)[0]
        users = users[users_id]
    else:
        users = {}
    users[username] = refresh_token
    if users_id is None:
        firebase.post('/users', users)
    else:
        firebase.put('/users', users_id, users)

def check_user_logged_in(username):
    users = firebase.get('/users', None)
    if users is not None:
        users_id = list(users)[0]
        users = users[users_id]
        if username in users:
            return users[username]
    return None

def logout_from_google(username):
    users = firebase.get('/users', None)
    users_id = None
    if users is not None:
        users_id = list(users)[0]
        users = users[users_id]
    else:
        return
    if username in users:
        users.pop(username)
    firebase.put('/users', users_id, users)