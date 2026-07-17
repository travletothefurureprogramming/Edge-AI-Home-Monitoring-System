# tests/conftest.py

import pytest
import sys
import os
import json

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app import create_app

@pytest.fixture
def client():

    app = create_app({
        "TESTING": True
    })

    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_client(client):

    client.post(
        "/login",
        data={
            "username": "admin",
            "password": "2611"
        },
        follow_redirects=True
    )

    return client

@pytest.fixture(autouse=True)
def mock_devices_config():

    config = {
        "Room": {
            "living_room": {
                "test_type": {
                    "1": {
                        "ip": "127.0.0.1"
                    }
                }
            }
        }
    }


    path = "config/devices_config.json"

    os.makedirs("config", exist_ok=True)

    with open(path,"w") as f:
        json.dump(config,f)