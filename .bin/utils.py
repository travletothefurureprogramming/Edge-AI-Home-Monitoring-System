import json
import requests

def read_json_file(file):
 with open(file, 'r') as f:
    data = json.load(f)
    return data

def send_to_server(content):
    requests.post(f"http://{BACKEND_URL}api/communicate", json=content, timeout=5)


def send_tv(content):
    requests.post(f"http://{BACKEND_URL}api/tv", json=content, timeout=5)

def send_light(content):
    requests.post(f"http://{BACKEND_URL}api/light", json=content, timeout=5)

def send_led_strip(content):
    requests.post(f"http://{BACKEND_URL}api/led_strip", json=content, timeout=5)

def send_ai(content):
    return requests.post(f"http://{BACKEND_URL}api/ai", json=content, timeout=5)

def send_security_notification(content):
    return requests.post(f"http://{BACKEND_URL}api/security/notification", json=content, timeout=5)

def send_security(content):
    return requests.post(f"http://{BACKEND_URL}api/security", json=content, timeout=5)

