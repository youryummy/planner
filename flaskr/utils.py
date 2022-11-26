from circuitbreaker import circuit
import requests

@circuit(failure_threshold=3, recovery_timeout=10)
def communicate(method, url, body, username):
    cookies = {"username": username}
    return requests.request(method, url, json=body, cookies=cookies)
