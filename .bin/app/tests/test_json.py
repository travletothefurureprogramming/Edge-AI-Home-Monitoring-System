import os

def test_devices_json_exists():

    assert os.path.exists(
        "config/devices_config.json"
    )