import json
import requests

def read_json_file(file):
 with open(file, 'r') as f:
    data = json.load(f)
    return data

def send_to_server(content):
    requests.post("http://192.168.1.2:8080/api/communicate", json=content)