# routes/devices.py
from flask import Blueprint, request, jsonify
import os
import json
from functools import wraps
from android_tv_rc.logger import Logger
from Server import auth, Sonos


music_bp = Blueprint('music', __name__, url_prefix='/api')

@music_bp.route("/music/current", methods=["POST"])
@auth.login_required
def current_song():
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = content["number"]
        command = content["command"]
        device = content["device"]

        Logger.info(f"/music/current -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")

        with open(f"{BASE_DIR}/config/devices_config.json") as f:
            data = json.load(f)

        ip = data["Room"][room][dev_type][number]["ip"]

        sonos = Sonos(ip)
        return jsonify({"title":sonos.current_track()})