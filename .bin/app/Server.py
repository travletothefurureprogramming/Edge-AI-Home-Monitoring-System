from android_tv_rc.logger import Logger
import os
from flask import Flask, request,jsonify,render_template, Blueprint, redirect, url_for, render_template_string, session
from flask_cors import CORS
import ollama
import json
import threading
from android_tv_rc.android_tv_controller import AndroidTVController
import asyncio
from tapo import ApiClient
from dotenv import load_dotenv, dotenv_values 
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, SystemControl, InputControl
import requests
import cv2
import ultralytics
import random
import time
import sys
from phue import Bridge
from yeelight import Bulb
import uptime
import psutil
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import aiohttp
from pydaikin.daikin_base import Appliance
from pydaikin.factory import DaikinFactory
from datetime import datetime
from croniter import croniter
import ShellyPy
from kasa import Discover
import broadlink
from samsungtvws import SamsungTVWS 
from soco import SoCo
import platform
import subprocess
from pathlib import Path
import secrets

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable) 
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


config_exists = (
    Path(f"{BASE_DIR}/config/.env").exists()
    and Path(f"{BASE_DIR}/config/devices_config.json").exists()
)

auth_bp = Blueprint("auth", __name__)

load_dotenv(
    os.path.join(BASE_DIR, "config/.env"),
    override=True
)
ADMIN_USERNAME = os.environ.get("USER","admin")
ADMIN_PASSWORD = os.environ.get("PASSWORD","")

LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Edge-AI Home Monitoring — Login</title>
  <style>
    body { font-family: system-ui, sans-serif; background:#0f1115; color:#eee;
           display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
    .card { background:#181b22; padding:2rem 2.5rem; border-radius:12px; width:280px; }
    h1 { font-size:1.1rem; margin-bottom:1.2rem; }
    input { width:100%; padding:.6rem; margin-bottom:.8rem; border-radius:6px;
            border:1px solid #333; background:#0f1115; color:#eee; box-sizing:border-box; }
    button { width:100%; padding:.6rem; border:none; border-radius:6px;
             background:#4f8cff; color:#fff; font-weight:600; cursor:pointer; }
    .error { color:#ff6b6b; font-size:.85rem; margin-bottom:.8rem; }
  </style>
</head>
<body>
  <form class="card" method="POST">
    <h1>🔒 Edge-AI Home Hub</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <input type="text" name="username" placeholder="Username" required autofocus>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""
 
class Auth:
    def login_required(self, view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("authenticated"):
                if request.path.startswith("/api/"):
                    return {"error": "Authentication required"}, 401
                return redirect(url_for("auth.login", next=request.path))
            return view_func(*args, **kwargs)
        return wrapped

auth = Auth()
errors = {
   "connection":{
      "module":{
         "TV":None,
         "Light":None 
      },
   }
}

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BACKEND_IP = os.getenv("SERVER_IP")
BACKEND_URL = f"{BACKEND_IP}:8080"

yolo = ultralytics.YOLO(os.path.join(BASE_DIR, "models/yolov8s.pt"))

is_running = False


tv_registry = {}


def read_json_file(file):
 try:
    with open(file, 'r') as f:
        data = json.load(f)
        return data
 except:
     return jsonify({"response":"Failed to read json file."})

def send_to_server(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/communicate", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to server. Error:{error}")

def send_tv(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/tv", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tv api endpoint. Error:{error}")

def send_tapo_light(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/tapo_light", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tapo light api endpoint. Error:{error}")

def send_tapo_led_strip(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/tapo_led_strip", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tapo ledsript api endpoint. Error:{error}")

def send_phue_light(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/phue_light", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to phue light api endpoint. Error:{error}")

def send_yeelight(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/yeelight", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to yeelight api endpoint. Error:{error}")

def send_daikin(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/daikin", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to daikin api endpoint. Error:{error}")

def send_shelly(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/shelly", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to shelly api endpoint. Error:{error}")

def send_kasa(content):
    try:
        requests.post(f"http://{BACKEND_URL}/api/kasa", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to kasa api endpoint. Error:{error}")


def send_ai(content):
    try:
        return requests.post(f"http://{BACKEND_URL}/api/ai", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to AI api endpoint. Error:{error}")

def send_security_notification(content):
    try:
        return requests.post(f"http://{BACKEND_URL}/api/security/notification", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send security notification. Error:{error}")

def send_security(content):
    try:
        return requests.post(f"http://{BACKEND_URL}/api/security", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to security api endpoint. Error:{error}")


def getColours(cls_num):
    try:
      random.seed(cls_num)
      return tuple(random.randint(0, 255) for _ in range(3))
    except:
        return "Failed to generate the colour"
    

def start_security():
    global is_running
    
    if is_running:
        print("Security already running!")
        return
        
    videoCap = cv2.VideoCapture(0)
    if not videoCap.isOpened():
        print("Error: The connection with camera has failed")
        return

    is_running = True
    person_detected = False
    print("The Edge-AI Monitoring System has started")

    while is_running:
        ret, frame = videoCap.read()
        if not ret:
            print("Failed to receive frame from the camera")
            break
        try:   
            results = yolo.track(frame, stream=True)
            detected_person_now = False

            for result in results:
                class_names = result.names

                for box in result.boxes:
                    if box.conf[0] > 0.4:
                        cls = int(box.cls[0])
                        class_name = class_names[cls]

                        if class_name == "person":
                            detected_person_now = True

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        colour = getColours(cls)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                        cv2.putText(
                            frame,
                            f"{class_name} {float(box.conf[0]):.2f}",
                            (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            colour,
                            2
                        )

            if detected_person_now and not person_detected:
                try:
                    send_security_notification({"person": "yes"})
                    person_detected = True
                except Exception as e:
                    Logger.error(f"Unexpected notification error: {e}")
                    continue

            if not detected_person_now:
                person_detected = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except FileNotFoundError as e:
            Logger.error(f"YOLO model not found: {e}")
            break

        except RuntimeError as e:
            Logger.error(f"YOLO runtime error: {e}")
            continue

        except Exception as e:
            Logger.error(f"Unexpected YOLO error: {e}")
            continue

    print("Shutdown camera")
    is_running = False
    videoCap.release()
    cv2.destroyAllWindows()
    
    cv2.waitKey(1) 

def stop_security():
    global is_running
    print("Receive command to close security")
    is_running = False  



def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown" 
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Error during send: {response.text}")
    except Exception as e:
        print(f"Failed in connection: {e}")

def check_for_messages(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    payload = {
        "timeout": 30,  
        "offset": offset
    }
    try:
        response = requests.get(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("result", [])
    except Exception as e:
        print(f"An error has occured during the receive of messages: {e}")
    return []

def load_devices_config():
    config_path = os.path.join(BASE_DIR, "config/devices_config.json") 
    if not os.path.exists(config_path):
        print(f"Error: The file {config_path} not found.")
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"An error has occured during the read of json: {e}")
        return None

def get_devices_list_message():
    config = load_devices_config()
    if not config or "Room" not in config:
        return "Failed to load the devices configure from the list.."

    msg = "List of subsribed Devices:*\n\n"
    
    for room_name, dev_types in config["Room"].items():
        room_title = room_name.replace("_", " ").title()
        msg += f"🏠 *{room_title}:*\n"
        
        has_devices = False
        for dev_type, devices in dev_types.items():
            for dev_id, dev_info in devices.items():
                has_devices = True
                dev_name = dev_info.get("name", "Uknown")
                
                emoji = "📺" if dev_type.lower() == "tv" else "💡"
                
                msg += f"  {emoji} `{dev_name}` (Type: {dev_type})\n"
        
        if not has_devices:
            msg += "  _(Devices Not Found)_\n"
        msg += "\n"
        
    return msg

def execute_device_command(room, dev_type, dev_id, dev_name, action):
    if dev_type.lower() == "lg_tv":
        endpoint = f"{BACKEND_URL}/api/tv"
    elif dev_type.lower() == "android_tv":
        endpoint = f"{BACKEND_URL}/api/tv"
    elif dev_type.lower() == "tapo_light":
        endpoint = f"{BACKEND_URL}/api/tapo_light"
    elif dev_type.lower() == "yeelight":
        endpoint = f"{BACKEND_URL}/api/yeelight"
    elif dev_type.lower() == "phue_light":
        endpoint = f"{BACKEND_URL}/api/phue_light"
    elif dev_type.lower() == "tapo_led_strip":
        endpoint = f"{BACKEND_URL}/api/tapo_led_strip"
    elif dev_type.lower() == "daikin":
        endpoint = f"{BACKEND_URL}/api/daikin"
    elif dev_type.lower() == "shelly":
        endpoint = f"{BACKEND_URL}/api/shelly"
    elif dev_type.lower() == "kasa":
        endpoint = f"{BACKEND_URL}/api/kasa"

    



    if action in ["άναψε", "on", "open", "άνοιξε"]:
        command_str = "power" if dev_type.lower() == "tv" else "on"
    elif action in ["κλείσε", "off", "close"]:
        command_str = "power" if dev_type.lower() == "tv" else "off"
    elif action in ["channel up", "πάνω κανάλλι", "επόμενο"]:
        command_str = "channel_up"
    elif action in ["channel down", "κάτω κανάλλι", "προηγούμενο"]:
        command_str = "channel_down"
    elif action in ["volume up", "πάνω ήχος"]:
        command_str = "volume_up"
    elif action in ["volume down", "κάτω ήχος"]:
        command_str = "volume_down"
    else:
        command_str = action

    payload = {
        "room": room,
        "type": dev_type,
        "number": str(dev_id),
        "command": command_str,
        "device": dev_name
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.status_code == 200:
            return True, f"The command *{command_str}* has send succesfully in the device: *{dev_name}* in the room: *{room}*."
        else:
            return False, f"The backend has returned an error: {response.text}"
    except Exception as e:
        return False, f"Failed to connect with backend: {e}"

def parse_and_execute(command_text):
    config = load_devices_config()
    if not config or "Room" not in config:
        return "Error during the loading of the devices."

    command_lower = command_text.lower()
    
    action = None
    if any(word in command_lower for word in ["άναψε", "on", "άνοιξε"]):
        action = "on"
    elif any(word in command_lower for word in ["κλείσε", "off"]):
        action = "off"
    elif "up" in command_lower or "πάνω" in command_lower:
        if "volume" in command_lower or "φωνή" in command_lower:
         action = "volume_up"
        elif "channel" in command_lower or "κανάλλι" in command_lower:
         action = "channel_up"
    elif "down" in command_lower or "κάτω" in command_lower:
        if "volume" in command_lower or "φωνή" in command_lower:
         action = "volume_down"
        elif "channel" in command_lower or "κανάλλι" in command_lower:
         action = "channel_down"
    if not action:
        return "Δεν κατάλαβα ποια ενέργεια θέλεις να κάνω (π.χ. άναψε, κλείσε)."

    for room_name, dev_types in config["Room"].items():
        room_clean = room_name.replace("_", " ").lower()
        
        for dev_type, devices in dev_types.items():
            for dev_id, dev_info in devices.items():
                dev_name = dev_info.get("name", "").lower()
                
                if dev_name in command_lower or (dev_type.lower() in command_lower and (room_clean in command_lower or room_name.lower() in command_lower)):
                    success, output_msg = execute_device_command(room_name, dev_type, dev_id, dev_info.get("name"), action)
                    return output_msg

    return "I didn't find any device in the configuration file that matches your command."

def main_bot_loop():
    print("The telegram bot has started and it receives messages...")
    last_update_id = None
    
    initial_updates = check_for_messages()
    if initial_updates:
        last_update_id = initial_updates[-1]["update_id"] + 1

    while True:
        updates = check_for_messages(offset=last_update_id)
        
        for update in updates:
            last_update_id = update["update_id"] + 1
            
            if "message" in update and "text" in update["message"]:
                message_text = update["message"]["text"]
                sender_id = str(update["message"]["chat"]["id"])
                
                if sender_id != CHAT_ID:
                    print(f"A message has ingored becuase of uknown sender ID: {sender_id}")
                    continue
                
                print(f"A new message from you: {message_text}")
                command = message_text.lower().strip()
                
                if command in ["συσκευές", "συσκευες", "devices", "/devices"]:
                    reply_list = get_devices_list_message()
                    send_telegram_message(reply_list)
                
                elif "άνοιξε την κάμερα" in command or "camera on" in command:
                    send_security({"status":"on"})
                    send_telegram_message("Monitoring system and camera has turned on.")
                elif "κλείσε την κάμερα" in command or "camera off" in command:
                    send_security({"status":"off"})
                    send_telegram_message("Security system has turned off.")

                elif "/ai" in command:
                   try:
                        prompt = {"prompt":command}
                        response = send_ai(prompt).json()
                        send_telegram_message(response["response"])
                   except TypeError as e:
                        return jsonify({"response": f"Bad Request: {e}"}), 400

                   except ConnectionError as e:
                        return jsonify({"response": f"Service Unavailable: {e}"}), 503

                   except KeyError as e:
                        return jsonify({"response": f"Missing field: {e}"}), 400

                   except Exception as e:
                        Logger.error(f"Unexpected error in /api/ai: {e}")
                        return jsonify({"response": "Internal Server Error"}), 500

                
                else:
                    reply = parse_and_execute(message_text)
                    send_telegram_message(reply)
                    
        time.sleep(2)




def get_tv_controller(ip):
    global tv_registry
    if ip not in tv_registry:
        print(f"Creation of new connetction for {ip}...")
        controller = AndroidTVController(ip)
        try:
            if controller.connect():
                tv_registry[ip] = controller
                send_to_server({"module": "TV", "type": "connection", "error": None, "action": "reset"})
            else:
                send_to_server({"module": "TV", "type": "connection", "error": f"Failed {ip}"})
                return None
        
        except TypeError as e:
            return f"Bad Request: {e}"
    
        except ConnectionError as e:
            return f"Service Unavailable: {e}"
        
        except KeyError as e:
            return f"Missing field: {e}"
        
        except Exception as e:
            Logger.error(f"Unexpected error in /api/devices: {e}")
            return "Internal Server Error"
        
    return tv_registry[ip]


class ServerMonitorAndRemoteControl:
    def __init__(self):
        self.net_sent = 0
        self.net_recv = 0
        if platform.system() == "Windows":
         from pycaw.pycaw import AudioUtilities
         self.devices = AudioUtilities.GetSpeakers()
        else:
            self.devices = None
        self.volume = self.devices.EndpointVolume

    def get_cpu(self):
        return psutil.cpu_percent(interval=0.5)
    
    def get_ram(self):
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self):
        return psutil.disk_usage('/').percent
    
    def network_usage(self):
        old_sent = psutil.net_io_counters().bytes_sent
        old_recv = psutil.net_io_counters().bytes_recv

        time.sleep(1)

        new_sent = psutil.net_io_counters().bytes_sent
        new_recv = psutil.net_io_counters().bytes_recv

        sent = new_sent - old_sent
        recv = new_recv - old_recv

        self.net_sent = new_sent - old_sent
        self.net_recv = new_recv - old_recv

        return sent,recv
    
    def get_uptime(self):
        return uptime.uptime()
    
    def sleep_pc(self):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def shutdown_pc(self):
        os.system("shutdown /s /t 0")

    def restart_pc(self):
        os.system("shutdown /r")

    def get_battery(self):
        try:
            battery = psutil.sensors_battery().percent
            return battery
        except:
            return "N/A"
    
    def get_volume(self):

        current_volume = self.volume.GetMasterVolumeLevelScalar() * 100
        return int(current_volume)

    def increase_volume(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        new_volume = min(current + 0.01, 1.0)  

        self.volume.SetMasterVolumeLevelScalar(new_volume, None)

    def decrease_volume(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        new_volume = min(current - 0.01, 1.0)  

        self.volume.SetMasterVolumeLevelScalar(new_volume, None)

if platform.system() == "Windows":
    Server_Monitor = ServerMonitorAndRemoteControl()

class Phue:
    def __init__(self,ip):
        self.bridge = Bridge(ip)

        self.bridge.connect()
    
    def turn_on(self,number):
        self.bridge.set_light(number, 'on', True)

    def turn_off(self,number):
        self.bridge.set_light(number, 'off', True)

    def command(self,command,number):
        if command == "on":
            self.turn_on(number)
        elif command == "off":
            self.turn_off(number)




class AndroidTV:
    def __init__(self, ip):
        self.ip = ip
        
    def send_command(self, command, is_dict):
        device = get_tv_controller(self.ip)
        if not device:
            return

        if not is_dict:
            match command:
                case "power": device.press_power()
                case "volume_up": device.press_volume_up()
                case "volume_down": device.press_volume_down()
                case "mute": device.press_volume_mute()
                case "channel_up": device.press_channel_up()
                case "channel_down": device.press_channel_down()
                case "home": device.press_home()
        else:
            if command["command"] == "channel":
                device.press_channel_number(str(command["number"]))


class Tapo_Led_strip:
    def __init__(self,ip,device):
     self.tapo_username = os.getenv("TAPO_USERNAME")
     self.tapo_password = os.getenv("TAPO_PASSWORD")

     self.ip_address = ip
     self.device = device

     self.client = ApiClient(self.tapo_username, self.tapo_password)

     self.connect()

    async def async_connect(self):
        model = self.device.lower().strip()
        if model == "l900":
            self.device = await self.client.l900(self.ip_address)
        elif model == "l920":
            self.device = await self.client.l920(self.ip_address)
        elif model == "l930":
            self.device = await self.client.l930(self.ip_address)
        else:
            raise ValueError(f"Άγνωστο μοντέλο Tapo LED strip: '{self.device}'")


    async def async_execute_command(self, command):
        match command:
            case "on": await self.device.on()
            case "off": await self.device.off()
    
    def connect(self):
        asyncio.run(self.async_connect())
    
    def command(self,command):
        asyncio.run(self.async_execute_command(command))

        
class Tapo_Smart_Bulbs:
    def __init__(self,ip,device):
     self.tapo_username = os.getenv("TAPO_USERNAME")
     self.tapo_password = os.getenv("TAPO_PASSWORD")

     self.ip_address = ip
     self.device = device

     self.client = ApiClient(self.tapo_username, self.tapo_password)

     self.connect()

    async def async_connect(self):
        model = self.device.lower().strip()
        if model == "l510":
            self.device = await self.client.l510(self.ip_address)
        elif model == "l520":
            self.device = await self.client.l520(self.ip_address)
        elif model == "l530":
            self.device = await self.client.l530(self.ip_address)
        elif model == "l535":
            self.device = await self.client.l535(self.ip_address)
        elif model == "l610":
            self.device = await self.client.l610(self.ip_address)
        elif model == "l630":
            self.device = await self.client.l630(self.ip_address)
        else:
            raise ValueError(f"Άγνωστο μοντέλο Tapo bulb: '{self.device}'")
        

    async def async_execute_command(self, command):
        match command:
            case "on": await self.device.on()
            case "off": await self.device.off()
    
    def connect(self):
        asyncio.run(self.async_connect())
    
    def command(self,command):
        asyncio.run(self.async_execute_command(command))

class LG_TV:
    def __init__(self, ip):
        self.STORE_FILE = os.path.join(BASE_DIR, "config/lg_store.json")

        self.store = self.load_from_your_custom_storage() if not self.your_custom_storage_is_empty() else {}

        self.ip = ip
        self.client = WebOSClient(ip, secure=True)

        self.connect()
        self.register()

        self.media = MediaControl(self.client)
        self.system = SystemControl(self.client)
        self.inputc = InputControl(self.client)

    def your_custom_storage_is_empty(self):
     return not os.path.exists(self.STORE_FILE) or os.path.getsize(self.STORE_FILE) == 0


    def load_from_your_custom_storage(self):
     try:
        with open(self.STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
     except (json.JSONDecodeError, FileNotFoundError):
        return {}


    def persist_to_your_custom_storage(self, store):
        with open(self.STORE_FILE, "w") as f:
            json.dump(store, f)

    def connect(self):
        self.client.connect()

    def register(self):


        for status in self.client.register(self.store):
            if status == WebOSClient.PROMPTED:
                print("Please accept the connect on the TV!")
            elif status == WebOSClient.REGISTERED:
                print("Registration successful!")

        self.persist_to_your_custom_storage(self.store)

    def play(self): self.media.play()
    def pause(self): self.media.pause()
    def stop(self): self.media.stop()
    def rewind(self): self.media.rewind()
    def fast_forward(self): self.media.fast_forward()
    def volume_up(self): self.media.volume_up()
    def volume_down(self): self.media.volume_down()
    def set_volume(self, level): self.media.set_volume(level)
    def mute(self, mute: bool): self.media.mute(mute)

    def home(self): self.system.home()

    def on(self): self.system.power_on()
    def off(self): self.system.power_off()

    def execute_command(self, command):
        match command:
            case "play": self.play()
            case "pause": self.pause()
            case "stop": self.stop()
            case "rewind": self.rewind()
            case "fast_forward": self.fast_forward()
            case "volume_up": self.volume_up()
            case "volume_down": self.volume_down()
            case "on": self.on()
            case "off": self.off()
            case "home": self.home()
        

class Yeelight:
    def __init__(self, ip):
        self.bulb = Bulb(ip)

    def on(self):
        self.bulb.turn_on()

    def off(self):
        self.bulb.turn_off()

    def command(self,command):
        if command == "on":
            self.on()
        elif command == "off":
            self.off()


class DaikinAC:
    def __init__(self, ip):
        self.HOST = ip

    async def async_on(self):
        async with await DaikinFactory(self.HOST) as device:
            await device.set_power(True)
    
    async def async_off(self):
        async with await DaikinFactory(self.HOST) as device:
            await device.set_power(False)

    async def async_increase_temperature(self):
        async with await DaikinFactory(self.HOST) as device:
            await device.update_status()

            await device.set_temperature(device.target_temperature+1)

    async def async_decrease_temperature(self):
        async with await DaikinFactory(self.HOST) as device:
            await device.update_status()

            await device.set_temperature(device.target_temperature-1)

    async def async_set_mode(self,mode):
        async with await DaikinFactory(self.HOST) as device:
            await device.set_mode(mode)

    def on(self):
        asyncio.run(self.async_on())

    def off(self):
        asyncio.run(self.async_off())

    def increase_temperature(self):
        asyncio.run(self.async_increase_temperature())

    def decrease_temperature(self):
        asyncio.run(self.async_decrease_temperature())

    def set_mode(self,mode):
        asyncio.run(self.async_set_mode(mode))

    
    def execute_command(self,command ,*args):
        if command == "on":
            self.on()
        elif command == "off":
            self.off()
        elif command == "increase_temperature":
            self.increase_temperature()
        elif command == "decrease_temperature":
            self.decrease_temperature()
        elif command == "set_mode":
            self.set_mode(args[0])


class Shelly:
    def __init__(self, ip):
        self.HOST = ip
        self.device = ShellyPy.Shelly(ip)
    
    def turn_on_relay(self, rellay_number=0):
        self.device.relay(rellay_number, turn=True)
    
    def turn_off_relay(self, rellay_number=0):
        self.device.relay(rellay_number, turn=False)

    def execute_command(self, command, *args):
        if command == "on":
            self.turn_on_relay(args)
        
        elif command == "off":
            self.turn_off_relay(args)

class Kasa:
    def __init__(self, ip):
        self.HOST = ip
        
        self.username = os.getenv("KASA_USERNAME")
        self.password = os.getenv("KASA_PASSWORD")
        
        self.device = None
        self.connect()
        
        
    async def async_connect(self):
        self.device = await Discover.discover_single(self.HOST, username=self.username, password=self.password)
        await self.device.update()
    
    def connect(self):
        asyncio.run(self.async_connect())

    async def async_turn_on(self):
        await self.device.turn_on()
        await self.device.update()

    def turn_on(self):
        asyncio.run(self.async_turn_on())

    async def async_turn_off(self):
        await self.device.turn_off()
        await self.device.update()

    def turn_off(self):
        asyncio.run(self.async_turn_off())

    def execute_command(self, command):
        if command == "on": self.turn_on()
        elif command == "off": self.turn_off()


class Broadlink:
    def __init__(self, ip):
        self.HOST = ip

        self.device = broadlink.hello(self.HOST)
        self.device.auth()

        self.JSON_FILE = "broadlink_codes.json"
        self.CONFIG_FILE = "devices_config.json"  

    def send_packet(self, room, device_name, command):
        with open(self.JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            hex_packet = data[room][device_name][command]
            byte_packet = bytes.fromhex(hex_packet)

            self.device.send_data(byte_packet)


class Samsung_TV:
    def __init__(self, ip):
        self.HOST = ip
        self.token_file = os.path.dirname(os.path.realpath(__file__)) + "config/samsung_store.txt"

        self.device = SamsungTVWS(host=self.HOST, port=8002, token_file=self.token_file)
    
    def power(self):
        self.device.shortcuts().power()

    def home(self):
        self.device.shortcuts().home()
    
    def volume_up(self):
        self.device.shortcuts().volume_up()

    def volume_down(self):
        self.device.shortcuts().volume_down()

    def mute(self):
        self.device.shortcuts().mute()
    
    def channel_up(self):
        self.device.shortcuts().channel_up()
    
    def channel_down(self):
        self.device.shortcuts().channel_down()

    def execute_command(self, command):
        if command == "power":
            self.power()
        elif command == "home":
            self.home()
        elif command == "volume_up":
            self.volume_up()
        elif command == "volume_down":
            self.volume_down()
        elif command == "mute":
            self.mute()
        elif command == "channel_up":
            self.channel_up()
        elif command == "channel_down":
            self.channel_down()

class Sonos:
    def __init__(self, ip):
        self.HOST = ip
        self.device = SoCo(ip)
    
    def play(self):
        self.device.play()
    
    def pause(self):
        self.device.pause()
    
    def stop(self):
        self.device.stop()
    
    def volume_up(self):
        self.device.volume += 5
    
    def volume_down(self):
        self.device.volume -= 5

    def current_track(self):
        return self.device.get_current_track_info()["title"]

    def execute_command(self, command):
        if command == "play":
            self.play()
        elif command == "pause":
            self.pause()
        elif command == "stop":
            self.stop()
        elif command == "volume_up":
            self.volume_up()
        elif command == "volume_down":
            self.volume_down()

DEVICE_ENDPOINTS = {
    "android_tv": "api/tv",
    "lg_tv": "api/tv",
    "samsung_tv": "api/tv",
    "tapo_light": "api/tapo_light",
    "tapo_led_strip": "api/tapo_led_strip",
    "phue_light": "api/phue_light",
    "yeelight": "api/yeelight",
    "daikin_ac": "api/daikin",
    "shelly": "api/shelly",
    "kasa": "api/kasa",
    "broadlink_ac": "api/broadlink/ac",
    "broadlink_decoder": "api/broadlink/decoder",
    "sonos": "/api/music/control"
}


def create_device_action(name, room, dev_type, number, command, device_name, model=None, mode=None, rellay_number=0):
    def action():
        try:
            with open(f"{BASE_DIR}/config/devices_config.json", "r") as f:
                data = json.load(f)
            dev_info = data["Room"][room][dev_type][number]
            ip = dev_info["ip"]

            if dev_type == "tapo_led_strip":
                Tapo_Led_strip(ip, dev_info["model"]).command(command)
            elif dev_type == "tapo_light":
                Tapo_Smart_Bulbs(ip, dev_info["model"]).command(command)
            elif dev_type == "yeelight":
                Yeelight(ip).command(command)
            elif dev_type == "phue_light":
                Phue(ip).command(command, dev_info["id"])
            elif dev_type == "android_tv":
                AndroidTV(ip).send_command(command, isinstance(command, dict))
            elif dev_type == "lg_tv":
                LG_TV(ip).execute_command(command)
            elif dev_type == "samsung_tv":
                Samsung_TV(ip).execute_command(command)
            elif dev_type == "daikin_ac":
                DaikinAC(ip).execute_command(command, mode)
            elif dev_type == "shelly":
                Shelly(ip).execute_command(command, rellay_number)
            elif dev_type == "kasa":
                Kasa(ip).execute_command(command)
            elif dev_type == "broadlink_ac":
                Broadlink(ip).send_packet(room, device_name, command)
            elif dev_type == "broadlink_decoder":
                Broadlink(ip).send_packet(room, device_name, command)            
            elif dev_type == "sonos":
                Sonos(ip).execute_command(command)
            else:
                Logger.error(f"Automation '{name}': άγνωστος τύπος συσκευής '{dev_type}'")

        except Exception as e:
            Logger.error(f"Automation '{name}' απέτυχε: {e}")

    action.__name__ = f"auto_{name}"
    return action


def emit_device_event(room, dev_type, command):
    event_name = f"{room}_{dev_type}_{command}"
    automation_manager.trigger_event(event_name)


class AutomationManager:
    def __init__(self, rules_file=None):

        self.rules_file = rules_file or os.path.join(
            BASE_DIR,
            "config/automation.json"
        )

        self.is_running = False
        self.rules = []
        self.available_actions = {}
        self.lock = threading.Lock()

    def register_action(self, func):
        self.available_actions[func.__name__] = func
        return func

    def _load_rules(self):
        try:
            with open(self.rules_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_rules(self):
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        with open(self.rules_file, "w") as f:
            json.dump(self.rules, f, indent=4)

    def add_schedule_rule(self, name, time_string, action_function, action_params=None):
        if action_function.__name__ not in self.available_actions:
            self.register_action(action_function)

        hour, minute = time_string.split(":")
        hour, minute = str(int(hour)), str(int(minute))
        cron_expression = f"{minute} {hour} * * *"

        rule = {
            "name": name,
            "trigger": {"type": "schedule", "cron": cron_expression},
            "action": action_function.__name__,
            "action_params": action_params or {},
            "last_fired": datetime.min.isoformat(),
        }

        with self.lock:
            self.rules = self._load_rules()
            self.rules.append(rule)
            self._save_rules()

    def add_event_rule(self, name, event_name, action_function, action_params):
        if action_function.__name__ not in self.available_actions:
            self.register_action(action_function)

        rule = {
            "name": name,
            "trigger": {"type": "event", "event": event_name},
            "action": action_function.__name__,
            "action_params": action_params or {},
            "last_fired": datetime.min.isoformat(),
        }

        with self.lock:
            self.rules = self._load_rules()
            self.rules.append(rule)
            self._save_rules()

    def rebuild_actions_from_rules(self):
        with self.lock:
            self.rules = self._load_rules()
        
        for rule in self.rules:
            params = rule.get("action_params")
            if not params:
                Logger.warning(f"Το rule '{rule['name']}' δεν έχει action_params — δεν μπορεί να ξαναδημιουργηθεί (παλιό format).")
                continue

            action_func = create_device_action(
                rule["name"],
                params.get("room"),
                params.get("type"),
                params.get("number"),
                params.get("command"),
                params.get("device",""),
                params.get("model"),
                params.get("mode"),
                params.get("rellay_number"),
            )

            self.register_action(action_func)
        
        Logger.info(f" Ξαναδημιουργήθηκαν {len(self.available_actions)} automation actions.")

    def delete_rule(self, name):
        with self.lock:
            self.rules = self._load_rules()
            self.rules = [r for r in self.rules if r["name"] != name]
            self._save_rules()

    def _try_run(self, rule):
        action_name = rule["action"]
        action_func = self.available_actions.get(action_name)

        if action_func:
            try:
                print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] Running: {rule['name']}")
                action_func()
            except Exception as e:
                print(f"Σφάλμα κατά την εκτέλεση του {action_name}: {e}")
        else:
            print(f"Η συνάρτηση '{action_name}' δεν βρέθηκε στα available_actions "
                  f"(μάλλον ο server έκανε restart και χάθηκαν τα registered actions)")

    def trigger_event(self, event_name):

        with self.lock:
            self.rules = self._load_rules()
        for rule in self.rules:
            trigger = rule.get("trigger", {})
            if trigger.get("type") == "event" and trigger.get("event") == event_name:
                self._try_run(rule)

    def _run_scheduler_loop(self):
        while self.is_running:
            now = datetime.now()

            with self.lock:
                self.rules = self._load_rules()

            file_needs_update = False

            for rule in self.rules:
                trigger = rule.get("trigger", {})
                if trigger.get("type") == "schedule":
                    cron = croniter(trigger["cron"], now)
                    prev_fire_time = cron.get_prev(datetime)
                    last_fired = datetime.fromisoformat(rule.get("last_fired"))

                    if (now - prev_fire_time).total_seconds() < 30 and prev_fire_time > last_fired:
                        self._try_run(rule)
                        rule["last_fired"] = prev_fire_time.isoformat()
                        file_needs_update = True

            if file_needs_update:
                with self.lock:
                    self._save_rules()

            time.sleep(30)

    def start(self):
        if not self.is_running:
            self.rebuild_actions_from_rules()
            self.is_running = True
            self.thread = threading.Thread(target=self._run_scheduler_loop, daemon=True)
            self.thread.start()
            print("The Automation Manager has started...")


automation_manager = AutomationManager()





def run_server():
    try:
        from app import create_app

        server = create_app()
        SETUP_FILE = os.path.join(BASE_DIR, "config", "setup-complete.txt")


        @server.before_request
        def check_setup():

            if (
                not os.path.exists(SETUP_FILE)
                and request.path not in ("/setup", "/api/setup")
                and not request.path.startswith("/static")
            ):
                return redirect("/setup")

        automation_manager.start()
        threading.Thread(target=main_bot_loop, daemon=True).start()
        
        server.run(host="0.0.0.0", port=8080)

    except TypeError as e:
        Logger.error({"response": f"Bad Request: {e}"})
    
    except ConnectionError as e:
        Logger.error({"response": f"Service Unavailable: {e}"})
    
    except KeyError as e:
        Logger.error({"response": f"Missing field: {e}"})
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":    
    run_server()
