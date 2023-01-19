from circuitbreaker import circuit
import requests
import time

@circuit(failure_threshold=3, recovery_timeout=10)
def communicate(method, url, body=None):
    if body is not None:
        response = requests.request(method, url, json=body)
    else:
        response = requests.request(method, url)
    if response.status_code == 200:
        return response.json()

def validate_event(event, method):
    if method == "POST" or method == "PUT":
        if "timestamp" not in event:
            return False, "No timestamp provided"
        if type(event["timestamp"]) != int:
            return False, "Timestamp must be an integer"
        if int(event["timestamp"]) < int(time.time()):
            return False, "Date is in the past"
        year = int(time.strftime('%Y', time.localtime(event["timestamp"])))
        if year > int(time.strftime('%Y', time.localtime(time.time()))) + 5:
            return False, "Date is more than 5 years in the future"

    if method == "POST":
        if "id" not in event:
            return False, "No recipe id provided"
        if type(event["id"]) != str:
            return False, "Recipe id must be a string"
        return True, "OK"
    
    if method == "PUT":
        if "id" not in event:
            return False, "No event id provided"
        if type(event["id"]) != str:
            return False, "Event id must be a string"
        if "synced" not in event:
            return False, "No synced provided"
        if type(event["synced"]) != bool:
            return False, "Synced must be a boolean"
        return True, "OK"

def validate_refresh_token(body):
    if "refreshToken" not in body:
        return False, "No refresh token provided"
    if type(body["refreshToken"]) != str:
        return False, "Refresh token must be a string"
    return True, body["refreshToken"]
