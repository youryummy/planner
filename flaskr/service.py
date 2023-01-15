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

    try:
        detailed_recipe = utils.communicate('GET', "".join(['http://recipes/api/v1/recipes/', body['id']]), None)
    except:
        logger.error("Failed to communicate with recipes service")
        return False, "Failed to communicate with recipes service", 500
    
    if detailed_recipe is None:
        return False, "Recipe not found"

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

    return True, "Created event successfully"

def get_events(username):
    events, _ = get_firebase_events(username)
    if events is None:
        events = {username : []}
    my_events = events[username]
    detailed_events = []
    for event in my_events:
        if event is not None and datetime.datetime.fromtimestamp(int(event['timestamp'])) < datetime.datetime.now():
            continue
        else:
            try:
                detailed_recipe = utils.communicate('GET', "".join(['http://recipes/api/v1/recipes/', event['recipe']]), None)
            except:
                logger.error("Failed to communicate with recipes service")
                return "Failed to communicate with recipes service"
            if detailed_recipe is not None:
                detailed_recipe = {
                    "id": detailed_recipe['_id'],
                    "name": detailed_recipe['name'],
                    "description": " " if 'summary' in detailed_recipe else detailed_recipe['summary'],
                    "tags": detailed_recipe['tags'],
                    "imageUrl": " " if 'imageUrl' not in detailed_recipe else detailed_recipe['imageUrl'],
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
    events, events_id = get_firebase_events(username)
    my_events = events[username]
    aux_event_count = 0
    for event in my_events:
        if event is not None and event['id'] == modified_event['id']:
            aux_event_count += 1
            if event['synced'] is True:
                return False, "You can't modify a synced event"
            if 'timestamp' in modified_event:
                event['timestamp'] = modified_event['timestamp']
            if 'synced' in modified_event and modified_event['synced'] is True:
                modified_event['recipe'] = event['recipe']
                synced, message, *error_code = sync_with_google_calendar(username, modified_event)
                if not synced:
                    if len(error_code) == 0:
                        return False, message
                    return False, message, error_code[0]
                event['synced'] = modified_event['synced']
            break
    if aux_event_count == 0:
        return False, "Event not found"
    events[username] = my_events
    firebase.put('/events', events_id, events)
    return True, "Updated event successfully"


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
        
        try:
            recipe = utils.communicate('GET', "".join(['http://recipes/api/v1/recipes/', event['recipe']]), None)
        except:
            logger.error("Failed to communicate with recipes service")
            return False, "Failed to communicate with recipes service", 500

        insert_event_in_google_calendar(service, event, recipe)
        return True, "Event modified successfully"
    else:
        return False, "User not logged in Google"

def login_with_google(username, refresh_token):
    users = firebase.get('/users', None)
    users_id = None
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

def insert_event_in_google_calendar(service, event, recipe):
    startDateTime = datetime.datetime.fromtimestamp(int(event['timestamp'])).isoformat()
    endDateTime = (datetime.datetime.fromtimestamp(int(event['timestamp'])) + datetime.timedelta(hours=1)).isoformat()
    timeZone = 'Europe/Madrid'

    event = {
        'summary': 'YourYummy: ' + recipe['name'],
        'description': " " if 'summary' in recipe else recipe['summary'],
        'start': {
            'dateTime': startDateTime,
            'timeZone': timeZone,
        },
        'end': {
            'dateTime': endDateTime,
            'timeZone': timeZone,
        }
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    logger.info('Event created: %s' % (event.get('htmlLink')))