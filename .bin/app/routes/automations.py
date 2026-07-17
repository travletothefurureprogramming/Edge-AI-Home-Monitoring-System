# routes/automations.py
from flask import Blueprint, request, jsonify, render_template
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
from Server import automation_manager, auth, create_device_action

automations_bp = Blueprint('automations', __name__, url_prefix='/api')


@automations_bp.route("/automations", methods=["GET"])
@auth.login_required
def list_automations():
    return jsonify(automation_manager._load_rules())


@automations_bp.route("/automations", methods=["POST"])
@auth.login_required
def create_automation():
    try:
        content = request.json
        name = content["name"]
        trigger_type = content["trigger_type"]  
        room = content["room"]
        dev_type = content["type"]
        number = str(content["number"])
        command = content["command"]
        device_name = content.get("device", "")
        model = content.get("model")
        mode = content.get("mode")

        action_params = {
            "room": room, "type": dev_type, "number": number,
            "command": command, "device": device_name,
            "model": model, "mode": mode,
        }

        action_func = create_device_action(
            name, room, dev_type, number, command, device_name, model, mode
        )

        if trigger_type == "schedule":
            automation_manager.add_schedule_rule(name, content["time"], action_func, action_params)
        elif trigger_type == "event":
            automation_manager.add_event_rule(name, content["event"], action_func, action_params)
        else:
            return jsonify({"error": "Unknown trigger_type"}), 400

        return jsonify({"status": "success", "message": f"Automation '{name}' created"}), 200

    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    except Exception as e:
        Logger.error(f"Unexpected error in /automations: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@automations_bp.route("/automations/<name>", methods=["DELETE"])
@auth.login_required
def remove_automation(name):
    automation_manager.delete_rule(name)
    return jsonify({"status": "deleted"}), 200
