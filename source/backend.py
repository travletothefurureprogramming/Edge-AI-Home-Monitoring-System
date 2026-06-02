from flask import Flask, request,jsonify,render_template
from flask_cors import CORS
from control import AndroidTV
from android_tv_rc.logger import Logger
import utils

server = Flask(__name__)
CORS(server)
all_is_ok = True

errors = {
   "connection":{
      "module":{
         "TV":None,
         "Light":None 
      },
   }
}


@server.route("/")
def inferance():
   return render_template("index.html")


@server.route("/api/communicate", methods=["POST"])
def communicate_for_errors():
    data = request.json
    module = data["module"]  
    error = data["error"]   
    err_type = data["type"]  
    action = data.get("action", "report") 

    if action == "reset":
        errors[err_type]["module"][module] = None
        Logger.info(f"Error reset for {module}")
        return jsonify({"status": "success", "message": "Error cleared"}), 200
    else:
        errors[err_type]["module"][module] = error
        return jsonify({"status": "error recorded"}), 200


@server.route("/api/light",methods=["POST","GET"])
def handle_lights():
   if request.method == "POST":
    content = request.json

    device = content["device"]
    room = content["room"]
    type = content["type"]
    command = content["command"]

    Logger.info(f"/api/light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {type}")

    return jsonify({"status": "success", "message": "Command received"}), 200
   
   else:  
      device_status = utils.read_json_file("source/files/device_status.json")["Lights"]

      return jsonify(device_status)

@server.route("/api/tv", methods=["POST"])
def handle_tv():
    content = request.json
    
    room = content["room"]
    type = content["type"]
    number = content["number"]
    command = content["command"]
    device = content["device"]
    
    data = utils.read_json_file("source/files/devices.json")
    ip = data["Room"][room][type][number]["ip"]

    tv = AndroidTV(ip) 
    
    tv.send_command(command, isinstance(command, dict))

    if errors["connection"]["module"]["TV"] is None:
        Logger.info(f"/api/tv -> Command {command} sent to {device}.")
        return jsonify({"status": "success", "message": "Command sent successfully"}), 200
    else:
        Logger.warning(f"/api/tv -> Error on communication with {device}.")
        return jsonify({"status": "error", "message": f"Communication with {device} failed."}), 503 # Το 503 είναι καλύτερο για "Service Unavailable"

    