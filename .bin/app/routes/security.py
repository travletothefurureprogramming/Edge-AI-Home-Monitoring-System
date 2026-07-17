# routes/security.py
from flask import Blueprint, request, jsonify, render_template
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps
import threading
from Server import send_security_notification, send_telegram_message, automation_manager, start_security, stop_security, auth

security_bp = Blueprint('security', __name__, url_prefix='/api')

@security_bp.route('/security',methods=['POST'])
@auth.login_required
def handle_security():
    try:
        content = request.json
    
        sequrity_status = content["status"]

        if sequrity_status == "on":
            threading.Thread(target=start_security).start()
            send_telegram_message("The camera has turned on")
            return jsonify({"status": "the camera has turned on"}), 200

        else:
            threading.Thread(target=stop_security).start()
            threading.Thread(target=send_telegram_message, args=("The camera has turned off",)).start()
            return jsonify({"status": "the camera has turned off"}), 200
   
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /security: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
    


@security_bp.route('/security/notification',methods=['POST'])
@auth.login_required
def send_notification():
    try:
        content = request.json

        is_person = content["person"]

        if is_person == "yes":
            print("ALARM")
            automation_manager.trigger_event("person_detected")
            send_telegram_message("ALARM!!!!!!! PERSON DETECTED ALARM PERSON DETECTED!!!!!!")
            return jsonify({"status": "Person has detected"}), 200
        
        return jsonify({"status": "All is ok"}), 200
    
    except TypeError as e:
        Logger.error(f"400 Bad request: {e}")
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        Logger.error(f"503 Service Unavailable: {e}")
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        Logger.error(f"400 Missing field: {e}")
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /security/notification: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
