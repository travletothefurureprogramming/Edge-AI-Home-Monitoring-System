from android_tv_rc.logger import Logger
import os
from flask import Flask, request,jsonify,render_template
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
from pycaw.pycaw import AudioUtilities
import uptime
import psutil



if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable) 
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))


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

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BACKEND_IP = os.getenv("SERVER_IP")
BACKEND_URL = f"{BACKEND_IP}:8080"

yolo = ultralytics.YOLO(os.path.join(BASE_DIR, "yolov8s.pt"))

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
        requests.post("http://192.168.1.2:8080/api/communicate", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to server. Error:{error}")

def send_tv(content):
    try:
        requests.post("http://192.168.1.2:8080/api/tv", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tv api endpoint. Error:{error}")

def send_tapo_light(content):
    try:
        requests.post("http://192.168.1.2:8080/api/tapo_light", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tapo light api endpoint. Error:{error}")

def send_tapo_led_strip(content):
    try:
        requests.post("http://192.168.1.2:8080/api/tapo_led_strip", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to tapo ledsript api endpoint. Error:{error}")

def send_phue_light(content):
    try:
        requests.post("http://192.168.1.2:8080/api/phue_light", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to phue light api endpoint. Error:{error}")

def send_yeelight(content):
    try:
        requests.post("http://192.168.1.2:8080/api/yeelight", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to yeelight api endpoint. Error:{error}")

def send_ai(content):
    try:
        return requests.post("http://192.168.1.2:8080/api/ai", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send the message to AI api endpoint. Error:{error}")

def send_security_notification(content):
    try:
        return requests.post("http://192.168.1.2:8080/api/security/notification", json=content, timeout=5)
    except Exception as error:
        Logger.error(f"An error has occured during the attemp to send security notification. Error:{error}")

def send_security(content):
    try:
        return requests.post("http://192.168.1.2:8080/api/security", json=content, timeout=5)
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
    config_path = os.path.join(BASE_DIR, "devices_config.json") 
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
    else:
        endpoint = f"{BACKEND_URL}/api/tapo_led_strip"


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
        self.devices = AudioUtilities.GetSpeakers()
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
        if self.device == "l900":
         self.device = await self.client.l900(self.ip_address)
        elif self.device == "l920":
         self.device = await self.client.l920(self.ip_address)
        elif self.device == "l930":
         self.device = await self.client.l930(self.ip_address)


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
        if self.device == "l510":
         self.device = await self.client.l510(self.ip_address)
        elif self.device == "l520":
         self.device = await self.client.l520(self.ip_address)  
        elif self.device == "l530":
         self.device = await self.client.l530(self.ip_address)
        elif self.device == "l535":
         self.device = await self.client.l535(self.ip_address)
        elif self.device == "l610":
         self.device = await self.client.l610(self.ip_address)
        elif self.device == "l630":
         self.device = await self.client.l630(self.ip_address)
        

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
        self.STORE_FILE = os.path.join(BASE_DIR, "lg_store.json")

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



@server.route("/api/ai", methods=["POST"])
def handle_ai():
    try:
        content = request.json
        user_input = content["prompt"]
    
        response = ollama.chat(model='phi3', messages=[
        {'role': 'system', 'content': 'You are a helpful assistant. Provide extremely concise, short, and direct answers in one or two sentences max.'},
        {'role': 'user', 'content': user_input}
        ])   

        ai_text = response['message']['content']
        
        return jsonify({"response": ai_text}), 200

    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400

    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503

    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400

    except Exception as e:
        Logger.error(f"Unexpected error in /api/ai: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
    

@server.route('/api/security',methods=['POST'])
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
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/security: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
    


@server.route('/api/security/notification',methods=['POST'])
def send_notification():
    try:
        content = request.json

        is_person = content["person"]

        if is_person == "yes":
            print("ALARM")
            send_telegram_message("ALARM!!!!!!! PERSON DETECTED ALARM PERSON DETECTED!!!!!!")
            return jsonify({"status": "Person has detected"}), 200
        
        return jsonify({"status": "All is ok"}), 200
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/security/notification: {e}")
        return jsonify({"response": "Internal Server Error"}), 500




@server.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        config_path = os.path.join(BASE_DIR, 'devices_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding="utf-8") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"response": f"Missing file"}), 400 
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/devices: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/")
def inferance():
   template_path = os.path.join('index.html')

   return render_template(template_path)


@server.route("/api/communicate", methods=["POST"])
def communicate_for_errors():
    try:
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
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/communicate: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

@server.route("/system")
def monitor_dashboard():
    return render_template("system.html")


@server.route("/api/system", methods=["GET"])
def return_system_info():
    try:
        system_info = {
            "cpu": Server_Monitor.get_cpu(),
            "ram": Server_Monitor.get_ram(),
            "disk": Server_Monitor.get_disk_usage(),
            "net_sent": Server_Monitor.net_sent,
            "net_recv": Server_Monitor.net_recv,
            "volume":Server_Monitor.get_volume(),
            "battery":Server_Monitor.get_battery(),
            "uptime":Server_Monitor.get_uptime()
        }
        return jsonify(system_info)
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/system: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/system/actions/sleep", methods=["POST"])
def sleep_api():
    try:
        data = request.json
        if data.get("action") == "sleep":
            Server_Monitor.sleep_pc()
        return jsonify({"message": "ok", "status": 200})
        
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/system/actions/sleep: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

@server.route("/api/system/actions/volume", methods=["GET","POST"])
def volume_api():
    if request.method == "GET":
        try:
            return jsonify({"volume":int(Server_Monitor.get_volume())})
         
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
        try:
            data = request.json
            if data.get("action") == "increase":
                Server_Monitor.increase_volume()
            else:
                Server_Monitor.decrease_volume()
            return jsonify({"message": "ok", "status": 200})
        
        except TypeError as e:
            return jsonify({"response": f"Bad Request: {e}"}), 400 
    
        except ConnectionError as e:
            return jsonify({"response": f"Service Unavailable: {e}"}), 503
        
        except KeyError as e:
            return jsonify({"response": f"Missing field: {e}"}), 400
        
        except Exception as e:
            Logger.error(f"Unexpected error in /api/system/actions/volume: {e}")
            return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/system/actions/shutdown", methods=["POST"])
def shutdown_api():
    try:
        data = request.json
        if data.get("action") == "shutdown":
            Server_Monitor.shutdown_pc()
        return jsonify({"message": "ok", "status": 200})
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/system/actions/shutdown: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/system/actions/restart", methods=["POST"])
def restart_api():
    try:
        data = request.json
        if data.get("action") == "restart":
            Server_Monitor.restart_pc()
        return jsonify({"message": "ok", "status": 200})
        
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/system/actions/restart: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/system/processes", methods=["GET"])
def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter():
            with proc.oneshot():
                try:
                    mem = proc.memory_info().rss / (1024 * 1024)
                    processes.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "mem": round(mem, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        top_procs = sorted(processes, key=lambda x: x['mem'], reverse=True)[:10]
        return jsonify(top_procs)
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/system/processes: {e}")
        return jsonify({"response": "Internal Server Error"}), 500

@server.route("/api/tapo_led_strip", methods=["POST"])
def handle_tapo_led_strip():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"]) 
        model = content["model"]

        Logger.info(f"/api/tapo_led_strip -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open("devices_config.json", "r") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            
            
            led_strip = Tapo_Led_strip(ip,model)
            led_strip.command(command)

            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Tapo_led_strip device not found in config"}), 404
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/tapo_led_strip: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/tapo_light", methods=["POST"])
def handle_tapo_light():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])
        model = content["model"]
    

        Logger.info(f"/api/tapo_light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open("devices_config.json", "r") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            
            
            smart_bulb = Tapo_Smart_Bulbs(ip,model)
            smart_bulb.command(command)

            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Tapo_light device not found in config"}), 404
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/tapo_light: {e}")
        return jsonify({"response": "Internal Server Error"}), 500
   

@server.route("/api/yeelight", methods=["POST"])
def handle_yeelight():
    try:
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])

        
        Logger.info(f"/api/yeelight -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open("devices_config.json", "r") as f:
            data = json.load(f)


        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            id = data["Room"][room][dev_type][number]["id"]
            
            
            yeelight = Yeelight(ip)
            yeelight.command(command)

            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Yeelight device not found in config"}), 404
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/yeelight: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/phue_light", methods=["POST"])
def handle_phue_lights():
    try:    
        content = request.json

        device = content["device"]
        room = content["room"]
        dev_type = content["type"]
        command = content["command"]
        number = str(content["number"])

        
        Logger.info(f"/api/phue_light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
        
        with open("devices_config.json", "r") as f:
            data = json.load(f)


        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            id = data["Room"][room][dev_type][number]["id"]
            
            
            phue_bridge = Phue(ip)
            phue_bridge.command(command,id)

            return jsonify({"status": "success", "message": "Command received"}), 200
            
        except KeyError:
            return jsonify({"status": "error", "message": "Phue_Light device not found in config"}), 404
    
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/phue_light: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


@server.route("/api/tv", methods=["POST"])
def handle_tv():
    try:
        content = request.json
        room = content["room"]
        dev_type = content["type"] 
        number = str(content["number"]) 
        command = content["command"]
        device = content["device"]
        
        with open("devices_config.json", "r") as f:
            data = json.load(f)
        
        try:
            ip = data["Room"][room][dev_type][number]["ip"]
            if dev_type == "android_tv":
                tv = AndroidTV(ip) 
                tv.send_command(command, isinstance(command, dict))
            
                if errors["connection"]["module"]["TV"] is None:
                    Logger.info(f"/api/tv -> Command {command} sent to {device} at {ip}.")
                    return jsonify({"status": "success", "message": "Command sent successfully"}), 200
                else:
                    return jsonify({"status": "error", "message": "TV communication error"}), 503
            elif dev_type == "lg_tv":
                tv = LG_TV(ip)

                tv.execute_command(command)

                Logger.info(f"/api/tv -> Command {command} sent to {device} at {ip}.")

                return jsonify({"status": "success", "message": "Command sent successfully"}), 200

        except KeyError:
            return jsonify({"status": "error", "message": "Device not found in config"}), 404
        
    except TypeError as e:
        return jsonify({"response": f"Bad Request: {e}"}), 400 
    
    except ConnectionError as e:
        return jsonify({"response": f"Service Unavailable: {e}"}), 503
    
    except KeyError as e:
        return jsonify({"response": f"Missing field: {e}"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/tv: {e}")
        return jsonify({"response": "Internal Server Error"}), 500


def run_server():
    try:
        server.run(
            host=BACKEND_IP,
            port=8080,
            debug=False,
            use_reloader=False
        )
    except TypeError as e:
        Logger.error({"response": f"Bad Request: {e}"})
    
    except ConnectionError as e:
        Logger.error({"response": f"Service Unavailable: {e}"})
    
    except KeyError as e:
        Logger.error({"response": f"Missing field: {e}"})
    
    except Exception as e:
        Logger.error(f"Unexpected error in /api/ai: {e}")

if __name__ == "__main__":
    threading.Thread(target=main_bot_loop).start()
    run_server()
