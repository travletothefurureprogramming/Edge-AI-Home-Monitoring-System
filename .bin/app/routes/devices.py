# routes/devices.py
from flask import Blueprint, request, jsonify
import os
import json
from android_tv_rc.logger import Logger
from functools import wraps

from Server import (
    Tapo_Smart_Bulbs, Tapo_Led_strip, Yeelight, Phue,
    LG_TV, AndroidTV, Samsung_TV, DaikinAC, Shelly, Kasa,
    Broadlink, Sonos, emit_device_event, auth
)

errors = {
   "connection":{
      "module":{
         "TV":None,
         "Light":None 
      },
   }
}

devices_bp = Blueprint('devices', __name__, url_prefix='/api')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@devices_bp.route("/tapo_led_strip", methods=["POST"])
@auth.login_required
def handle_tapo_led_strip():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"]) 
        

        Logger.info(f"/tapo_led_strip -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            model = data["Room"][room][dev_type][number]["model"]
            
            
            led_strip = Tapo_Led_strip(ip,model)
            led_strip.command(command)
            emit_device_event(room, dev_type, command)

            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Tapo_led_strip device not found in config"}), 404
    
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
        Logger.error(f"Unexpected error in /tapo_led_strip: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route("/tapo_light", methods=["POST"])
@auth.login_required
def handle_tapo_light():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])
    

        Logger.info(f"/tapo_light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            model = data["Room"][room][dev_type][number]["model"]

            
            smart_bulb = Tapo_Smart_Bulbs(ip,model)
            smart_bulb.command(command)
            emit_device_event(room, dev_type, command)


            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Tapo_light device not found in config"}), 404
    
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
        Logger.error(f"Unexpected error in /tapo_light: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500
   

@devices_bp.route("/yeelight", methods=["POST"])
@auth.login_required
def handle_yeelight():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])

        
        Logger.info(f"/yeelight -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)


        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            id = data["Room"][room][dev_type][number]["id"]
            
            
            yeelight = Yeelight(ip)
            yeelight.command(command)
            emit_device_event(room, dev_type, command)


            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Yeelight device not found in config"}), 404
    
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
        Logger.error(f"Unexpected error in /yeelight: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route("/phue_light", methods=["POST"])
@auth.login_required
def handle_phue_lights():
    try:    
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])

        
        Logger.info(f"/phue_light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)


        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            id = data["Room"][room][dev_type][number]["id"]
            
            
            phue_bridge = Phue(ip)
            phue_bridge.command(command,id)
            emit_device_event(room, dev_type, command)


            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Phue_Light device not found in config"}), 404
    
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
        Logger.error(f"Unexpected error in /phue_light: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route("/tv", methods=["POST"])
@auth.login_required
def handle_tv():
    try:
        content = request.json 
        room = content["room"]
        dev_type = content["type"] 
        number = str(content["number"]) 
        command = content["command"]
        device = content["device"]
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)

        is_broadlink = data.get("Room", {})\
                   .get(room, {})\
                   .get(dev_type, {})\
                   .get(number, {})\
                   .get("is_broadlink_device", False)
        
        if is_broadlink:
            try:            
                ip = data["Room"][room][dev_type][number]["ip"]
                broadlink_ = Broadlink(ip)

                broadlink_.send_packet(room,device,command)
                
                return jsonify({"status": "success", "message": "Command sent successfully"}), 200


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
                Logger.error(f"Unexpected error in /tv: {e}")
                return jsonify({"response": "Internal devices_bp Error"}), 500
            
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            if dev_type == "android_tv":
                tv = AndroidTV(ip) 
                tv.send_command(command, isinstance(command, dict))
            
                if errors["connection"]["module"]["TV"] is None:
                    Logger.info(f"/tv -> Command {command} sent to {device} at {ip}.")
                    emit_device_event(room, dev_type, command)
                    return jsonify({"status": "success", "message": "Command sent successfully"}), 200
                else:
                    return jsonify({"status": "error", "message": "TV communication error"}), 503
            elif dev_type == "lg_tv":
                tv = LG_TV(ip)

                tv.execute_command(command)

                Logger.info(f"/tv -> Command {command} sent to {device} at {ip}.")
                emit_device_event(room, dev_type, command)

                return jsonify({"status": "success", "message": "Command sent successfully"}), 200
            elif dev_type == "samsung_tv":
                tv = Samsung_TV(ip)

                tv.execute_command(command)
                
                Logger.info(f"/tv -> Command {command} sent to {device} at {ip}.")
                emit_device_event(room, dev_type, command)

                return jsonify({"status": "success", "message": "Command sent successfully"}), 200

        except KeyError:
            return jsonify({"status": "error", "message": "Device not found in config"}), 404
        
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
        Logger.error(f"Unexpected error in /tv: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route("/daikin", methods=["POST"])
@auth.login_required
def handle_daikin_ac():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"] 
        number = str(content["number"]) 
        command = content["command"]
        device = content["device"]

        Logger.info(f"/daikin -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")

        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)

        try:
            ip = data["Room"][room][dev_type][number]["ip"]

            daikinAC = DaikinAC(ip)

            if command == "set_mode":
                mode = content["mode"]
                daikinAC.execute_command(command,mode)
                emit_device_event(room,dev_type,command)
        
            else:
                daikinAC.execute_command(command)
                emit_device_event(room,dev_type,command)

            return jsonify({"status": "success", "message": "Command received"}), 200
        
        except KeyError:
            return jsonify({"status": "error", "message": "DaikinAC device not found in config"}), 404
        
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500

@devices_bp.route("/shelly", methods=["POST"])
@auth.login_required
def handle_shelly():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = str(content["number"])
        command = content["command"]
        device = content["device"]

        Logger.info(f"/shelly -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = json.load(f)

        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            rellay_number = data["Room"][room][dev_type][number]["rellay_number"]

            shelly = Shelly(ip)

            shelly.execute_command(command, int(rellay_number))
            emit_device_event(room,dev_type,command)
        
            return jsonify({"status": "success", "message": "Command received"}), 200  
        
        except KeyError:
            return jsonify({"status": "error", "message": "DaikinAC device not found in config"}), 404
        
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route("/kasa" , methods=["POST"])
@auth.login_required
def handle_kasa():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = str(content["number"])
        command = content["command"]
        device = content["device"]

        Logger.info(f"/kasa -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")

        with open(f"{BASE_DIR}/config/devices_config.json") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]

            kasa = Kasa(ip)

            kasa.execute_command(command)
            emit_device_event(room,dev_type,command)

            return jsonify({"status": "success", "message": "Command received"}), 200  

        except KeyError:
            return jsonify({"status": "error", "message": "DaikinAC device not found in config"}), 404
        
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500

@devices_bp.route("/broadlink/ac", methods=["POST"])
def handle_broadlink_ac():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = str(content["number"])
        command = content["command"]
        device = content["device"]

        Logger.info(f"/broadlink/ac -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")

        with open(f"{BASE_DIR}/config/devices_config.json") as f:
            data = json.load(f)

        ip = data["Room"][room][dev_type][number]["ip"]

        kasa = Kasa(ip)

        kasa.execute_command(command)
        emit_device_event(room,dev_type,command)

        return jsonify({"status": "success", "message": "Command received"}), 200  
    
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500
    

@devices_bp.route("/broadlink/decoder", methods=["POST"])
def handle_broadlink_decoder():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = content["number"]
        command = content["command"]
        device = content["device"]

        Logger.info(f"/broadlink/decoder -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
            data = f.read()

        ip = data["Room"][room][dev_type][number]["ip"]

        broadlink_ = Broadlink()

        broadlink_.send_packet(room,device,command)
        emit_device_event(room,dev_type,command)

        return jsonify({"status": "success", "message": "Command received"}), 200  

    
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500
    

@devices_bp.route("/music/control", methods=["POST"])
def handle_sonos():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"]
        number = content["number"]
        command = content["command"]
        device = content["device"]

        Logger.info(f"/music/control -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")

        with open(f"{BASE_DIR}/config/devices_config.json") as f:
            data = json.load(f)

        ip = data["Room"][room][dev_type][number]["ip"]

        sonos = Sonos(ip)

        sonos.execute_command(command)

        emit_device_event(room,dev_type,command)

        return jsonify({"status": "success", "message": "Command received"}), 200  

    
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
        Logger.error(f"Unexpected error in /daikin: {e}")
        return jsonify({"response": "Internal devices_bp Error"}), 500


@devices_bp.route('devices', methods=['GET'])
@auth.login_required
def get_devices():
    try:
        config_path = os.path.join(BASE_DIR, 'config/devices_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding="utf-8") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"response": f"Missing file"}), 400 
    
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
        Logger.error(f"Unexpected error in /api/devices: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

