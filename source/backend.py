from flask import Flask, request,jsonify,render_template
from flask_cors import CORS
from control import AndroidTV
from android_tv_rc.logger import Logger
import utils
import ollama
from control import Led_strip
import json


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


@server.route("/api/ai", methods=["POST"])
def handle_ai():
    content = request.json
    user_input = content["prompt"]
    
    # Χρήση του phi3 για ταχύτητα
    response = ollama.chat(model='phi3', messages=[
    {'role': 'system', 'content': 'You are a helpful assistant. Provide extremely concise, short, and direct answers in one or two sentences max.'},
    {'role': 'user', 'content': user_input}
])    
    ai_text = response['message']['content']
    
    return jsonify({"response": ai_text}), 200


@server.route('/api/devices', methods=['GET'])
def get_devices():
    with open('devices_config.json', 'r') as f:
        return jsonify(json.load(f))

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


@server.route("/api/light",methods=["POST"])
def handle_lights():
   
    content = request.json

    device = content["device"]
    room = content["room"]
    type = content["type"]
    command = content["command"]

    Logger.info(f"/api/light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {type}")
    
    led_strip = Led_strip()

    led_strip.command(command)

    return jsonify({"status": "success", "message": "Command received"}), 200
   


@server.route("/api/tv", methods=["POST"])
def handle_tv():
    content = request.json
    room = content["room"]
    dev_type = content["type"] # Μετονομασία σε dev_type για να μην συγκρούεται με τη λέξη-κλειδί 'type'
    number = str(content["number"]) # Μετατροπή σε string για το key του JSON
    command = content["command"]
    device = content["device"]
    
    # Φόρτωση από το αρχείο ρυθμίσεων
    with open("devices_config.json", "r") as f:
        data = json.load(f)
    
    try:
        ip = data["Room"][room][dev_type][number]["ip"]
        tv = AndroidTV(ip) 
        tv.send_command(command, isinstance(command, dict))
        
        if errors["connection"]["module"]["TV"] is None:
            Logger.info(f"/api/tv -> Command {command} sent to {device} at {ip}.")
            return jsonify({"status": "success", "message": "Command sent successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "TV communication error"}), 503
    except KeyError:
        return jsonify({"status": "error", "message": "Device not found in config"}), 404