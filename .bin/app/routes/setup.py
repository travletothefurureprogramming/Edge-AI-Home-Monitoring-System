# routes/setup.py
from flask import Blueprint, request, jsonify, render_template, redirect
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import threading
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
import sys
from pathlib import Path
from Server import auth, main_bot_loop, automation_manager

setup_bp = Blueprint('system', __name__, url_prefix='')
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable) 
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config_exists = (
    Path(f"{BASE_DIR}/config/.env").exists()
    and Path(f"{BASE_DIR}/config/devices_config.json").exists()
)


load_dotenv(
    os.path.join(BASE_DIR, "config/.env"),
    override=True
)

def update_env_file(key, value):
        env_path = os.path.join(BASE_DIR, "config/.env")

        dir_path = os.path.dirname(env_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        lines = []
        key_found = False

        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f'{key}="{value}"\n'
                key_found = True
                break

        if not key_found:
            lines.append(f'{key}="{value}"\n')

        with open(env_path, "w") as f:
            f.writelines(lines)

SETUP_FILE = os.path.join(BASE_DIR, "config", "setup-complete.txt")


@setup_bp.route("/setup")
def setup_page():
    return render_template("setup.html")


@setup_bp.route("/api/setup", methods=["POST"])
def finish_setup():

    data=request.json

    update_env_file("USER","admin")
    update_env_file("PASSWORD",generate_password_hash(data["password"]))
    update_env_file("FLASK_SECRET_KEY",secrets.token_hex(32))
    update_env_file("TELEGRAM_BOT_TOKEN",data["telegram_token"])
    update_env_file("TELEGRAM_CHAT_ID",data["telegram_chat_id"])

    for device in data["devices"]:
        update_env_file("TAPO_USERNAME", device.get("username", ""))
        update_env_file("TAPO_PASSWORD", device.get("password", ""))

    for device in data["devices"]:
        save_device(
            room=device["room"],
            device_type=device["type"],
            name=device["name"],
            ip=device["ip"],
            username=device.get("username", ""),
            password=device.get("password", ""),
            model=device.get("model", ""),
            device_id=device.get("id", ""),
            relay_number=device.get("relay_number", "")
        )

    with open(SETUP_FILE, "w") as f:
        f.write("ok")
    
    load_dotenv(override=True)

    automation_manager.start()
    threading.Thread(target=main_bot_loop, daemon=True).start()

    return {"status": "success"}


CONFIG_FILE = os.path.join(BASE_DIR, "config", "devices_config.json")

def save_device(
    room,
    device_type,
    name,
    ip,
    username="",
    password="",
    model="",
    device_id="",
    relay_number=""
):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    data = {"Room": {}}

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    data.setdefault("Room", {})
    data["Room"].setdefault(room, {})
    data["Room"][room].setdefault(device_type, {})

    existing_ids = [
        int(i)
        for i in data["Room"][room][device_type].keys()
        if str(i).isdigit()
    ]

    new_id = str(max(existing_ids, default=0) + 1)

    data["Room"][room][device_type][new_id] = {
        "name": name,
        "type": device_type,
        "ip": ip,
        "username": username,
        "password": password,
        "model": model,
        "id": device_id,
        "relay_number": relay_number
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return new_id
