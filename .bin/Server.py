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

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable) # Αν τρέχει ως .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Αν τρέχει ως .py

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

TOKEN = "8998096928:AAHfxCOWoZ8Um032pdqhyuKk9IN3YNolYmk"
CHAT_ID = "8532508249"

BACKEND_URL = "http://127.0.0.1:8080"

yolo = ultralytics.YOLO(os.path.join(BASE_DIR, "yolov8s.pt"))

is_running = False

load_dotenv(os.path.join(BASE_DIR, ".env"))

tv_registry = {}


def read_json_file(file):
 with open(file, 'r') as f:
    data = json.load(f)
    return data

def send_to_server(content):
    requests.post("http://192.168.1.2:8080/api/communicate", json=content)


def send_tv(content):
    requests.post("http://192.168.1.2:8080/api/tv", json=content)

def send_light(content):
    requests.post("http://192.168.1.2:8080/api/light", json=content)

def send_led_strip(content):
    requests.post("http://192.168.1.2:8080/api/led_strip", json=content)

def send_ai(content):
    return requests.post("http://192.168.1.2:8080/api/ai", json=content)

def send_security_notification(content):
    return requests.post("http://192.168.1.2:8080/api/security/notification", json=content)

def send_security(content):
    return requests.post("http://192.168.1.2:8080/api/security", json=content)




def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))

def start_security():
    global is_running
    
    if is_running:
        print("Η ασφάλεια τρέχει ήδη!")
        return
        
    videoCap = cv2.VideoCapture(0)
    if not videoCap.isOpened():
        print("Σφάλμα: Δεν είναι δυνατή η πρόσβαση στην κάμερα.")
        return

    is_running = True
    person_detected = False
    print("Το σύστημα Edge-AI Monitoring ξεκίνησε...")

    while is_running:
        ret, frame = videoCap.read()
        if not ret:
            print("Αποτυχία λήψης frame από την κάμερα.")
            break

        # YOLO tracking
        results = yolo.track(frame, stream=True)
        detected_person_now = False

        for result in results:
            class_names = result.names

            for box in result.boxes:
                if box.conf[0] > 0.4:
                    cls = int(box.cls[0])
                    class_name = class_names[cls]

                    # Αν βρέθηκε άνθρωπος
                    if class_name == "person":
                        detected_person_now = True

                    # Σχεδίαση bounding box
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

        # Στείλε ειδοποίηση ΜΟΝΟ όταν εμφανιστεί για πρώτη φορά άνθρωπος
        if detected_person_now and not person_detected:
            send_security_notification({"person": "yes"})
            person_detected = True

        # Αν δεν υπάρχει άνθρωπος στο frame, reset για την επόμενη ειδοποίηση
        if not detected_person_now:
            person_detected = False

        # Εμφάνιση εικόνας
        cv2.imshow("Edge-AI Camera Monitoring", frame)

        # Έξοδος με 'q' από το πληκτρολόγιο
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Σωστό κλείσιμο και αποδέσμευση της κάμερας
    print("Τερματισμός κάμερας και αποδέσμευση πόρων...")
    is_running = False
    videoCap.release()
    cv2.destroyAllWindows()
    
    # Μερικές φορές στα Windows/Linux χρειάζεται ένα μικρό waitKey για να κλείσει όντως το UI
    cv2.waitKey(1) 

def stop_security():
    global is_running
    print("Λήψη εντολής για κλείσιμο της ασφάλειας...")
    is_running = False  # Αυτό θα σπάσει το while loop στο επόμενο iteration



def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown" 
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Σφάλμα αποστολής: {response.text}")
    except Exception as e:
        print(f"Αποτυχία σύνδεσης κατά την αποστολή: {e}")

def check_for_messages(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    payload = {
        "timeout": 30,  # Long polling timeout
        "offset": offset
    }
    try:
        response = requests.get(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("result", [])
    except Exception as e:
        print(f"Σφάλμα κατά τη λήψη μηνυμάτων: {e}")
    return []

def load_devices_config():
    """Φορτώνει δυναμικά το αρχείο ρυθμίσεων συσκευών"""
    config_path = os.path.join(BASE_DIR, "devices_config.json") # <-- Αλλαγή εδώ
    if not os.path.exists(config_path):
        print(f"Σφάλμα: Το αρχείο {config_path} δεν βρέθηκε.")
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Σφάλμα κατά το διάβασμα του json: {e}")
        return None

def get_devices_list_message():
    """Διαβάζει το αρχείο και επιστρέφει μια μορφοποιημένη λίστα συσκευών"""
    config = load_devices_config()
    if not config or "Room" not in config:
        return "❌ Δεν μπόρεσα να φορτώσω τις ρυθμίσεις των συσκευών για τη λίστα."

    msg = "📱 *Λίστα Εγγεγραμμένων Συσκευών:*\n\n"
    
    for room_name, dev_types in config["Room"].items():
        # Μορφοποίηση ονόματος δωματίου (π.χ. maria_room -> Maria Room)
        room_title = room_name.replace("_", " ").title()
        msg += f"🏠 *{room_title}:*\n"
        
        has_devices = False
        for dev_type, devices in dev_types.items():
            for dev_id, dev_info in devices.items():
                has_devices = True
                dev_name = dev_info.get("name", "Άγνωστο")
                
                # Επιλογή κατάλληλου Emoji
                emoji = "📺" if dev_type.lower() == "tv" else "💡"
                
                msg += f"  {emoji} `{dev_name}` (Τύπος: {dev_type})\n"
        
        if not has_devices:
            msg += "  _(Δεν βρέθηκαν συσκευές)_\n"
        msg += "\n"
        
    return msg

def execute_device_command(room, dev_type, dev_id, dev_name, action):
    """Στέλνει το σωστό αίτημα στο Flask backend ανάλογα με τον τύπο της συσκευής"""
    if dev_type.lower() == "lg_tv":
        endpoint = f"{BACKEND_URL}/api/tv"
    elif dev_type.lower() == "android_tv":
        endpoint = f"{BACKEND_URL}/api/tv"
    elif dev_type.lower() == "light":
        endpoint = f"{BACKEND_URL}/api/light"
    else:
        endpoint = f"{BACKEND_URL}/api/led_strip"


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
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            return True, f"Η εντολή *{command_str}* στάλθηκε επιτυχώς στη συσκευή *{dev_name}* στο δωμάτιο *{room}*."
        else:
            return False, f"Το backend επέστρεψε σφάλμα: {response.text}"
    except Exception as e:
        return False, f"Αποτυχία σύνδεσης με το backend: {e}"

def parse_and_execute(command_text):
    """Αναλύει το κείμενο με βάση το αρχείο json και εκτελεί την εντολή"""
    config = load_devices_config()
    if not config or "Room" not in config:
        return "Δεν μπόρεσα να φορτώσω τις ρυθμίσεις των συσκευών."

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

    return "Δεν βρήκα κάποια συσκευή στο αρχείο ρυθμίσεων που να ταιριάζει με την εντολή σου."

def main_bot_loop():
    print("Το Telegram Bot ξεκίνησε και ακούει για μηνύματα...")
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
                    print(f"Αγνοήθηκε μήνυμα από άγνωστο Chat ID: {sender_id}")
                    continue
                
                print(f"Νέο μήνυμα από εσένα: {message_text}")
                command = message_text.lower().strip()
                
                # 1. Έλεγχος για εμφάνιση λίστας συσκευών
                if command in ["συσκευές", "συσκευες", "devices", "/devices"]:
                    reply_list = get_devices_list_message()
                    send_telegram_message(reply_list)
                
                # 2. Ειδική διαχείριση για την κάμερα ασφαλείας
                elif "άνοιξε την κάμερα" in command or "camera on" in command:
                    send_security({"status":"on"})
                    send_telegram_message("📹 Το σύστημα ασφαλείας και η κάμερα ενεργοποιήθηκαν.")
                elif "κλείσε την κάμερα" in command or "camera off" in command:
                    send_security({"status":"off"})
                    send_telegram_message("🛑 Το σύστημα ασφαλείας απενεργοποιήθηκε.")

                elif "/ai" in command:
                   
                   prompt = {"prompt":command}
                   response = send_ai(prompt)["response"]
                   send_telegram_message(response['message']['content'])

                
                # 3. Δυναμικός έλεγχος όλων των άλλων συσκευών από το JSON
                else:
                    reply = parse_and_execute(message_text)
                    send_telegram_message(reply)
                    
        time.sleep(2)




def get_tv_controller(ip):
    global tv_registry
    if ip not in tv_registry:
        print(f"Δημιουργία νέου connection για {ip}...")
        controller = AndroidTVController(ip)
        if controller.connect():
            tv_registry[ip] = controller
            send_to_server({"module": "TV", "type": "connection", "error": None, "action": "reset"})
        else:
            send_to_server({"module": "TV", "type": "connection", "error": f"Failed {ip}"})
            return None
    return tv_registry[ip]

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

    async def async_connect(self):
        if self.device == "l900":
         self.device = await self.client.l900(self.ip_address)
        elif self.device == "l920":
         self.device = await self.client.l920(self.ip_address)
        elif self.device == "l930":
         self.device = await self.client.l930(self.ip_address)


    async def async_execute_command(self, command):
        device = await self.client.l900(self.ip_address)
        match command:
            case "on": await device.on()
            case "off": await device.off()
    
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

    async def async_connect(self):
        if self.device == "l510":
         self.device = await self.client.l510(self.ip_address)
        elif self.device == "l520":
         self.device = await self.client.l520(self.ip_address)  
        elif self.device == "l520":
         self.device = await self.client.l530(self.ip_address)
        elif self.device == "l535":
         self.device = await self.client.l535(self.ip_address)
        elif self.device == "l610":
         self.device = await self.client.l610(self.ip_address)
        elif self.device == "l630":
         self.device = await self.client.l630(self.ip_address)
        

    async def async_execute_command(self, command):
        device = await self.client.l900(self.ip_address)
        match command:
            case "on": await device.on()
            case "off": await device.off()
    
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
     # Άδειο αν δεν υπάρχει ή έχει μέγεθος 0
     return not os.path.exists(self.STORE_FILE) or os.path.getsize(self.STORE_FILE) == 0


    def load_from_your_custom_storage(self):
     try:
        with open(self.STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
     except (json.JSONDecodeError, FileNotFoundError):
        # Αν το JSON είναι άδειο ή χαλασμένο → ξεκινάμε από την αρχή
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

        # Αποθήκευση ΜΟΝΟ μετά το REGISTERED
        self.persist_to_your_custom_storage(self.store)

    # --- MEDIA ---
    def play(self): self.media.play()
    def pause(self): self.media.pause()
    def stop(self): self.media.stop()
    def rewind(self): self.media.rewind()
    def fast_forward(self): self.media.fast_forward()
    def volume_up(self): self.media.volume_up()
    def volume_down(self): self.media.volume_down()
    def set_volume(self, level): self.media.set_volume(level)
    def mute(self, mute: bool): self.media.mute(mute)

    # --- POWER ---
    def on(self): self.system.power_on()
    def off(self): self.system.power_off()

    # --- COMMAND ROUTER ---
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

@server.route('/api/security',methods=['POST'])
def handle_security():
    content = request.json
    
    sequrity_status = content["status"]

    if sequrity_status == "on":
        threading.Thread(target=start_security).start()
        send_telegram_message("The camera has turned on")
        return jsonify({"status": "the camera has turned on"}), 200

    else:
        threading.Thread(target=stop_security).start()
        threading.Thread(target=send_telegram_message("The camera has turned off")).start()
        return jsonify({"status": "the camera has turned off"}), 200


@server.route('/api/security/notification',methods=['POST'])
def send_notification():
    content = request.json

    is_person = content["person"]

    if is_person == "yes":
        print("ALARM")
        send_telegram_message("ALARM!!!!!!! PERSON DETECTED ALARM PERSON DETECTED!!!!!!")
        return jsonify({"status": "Person has detected"}), 200
    
    return jsonify({"status": "All is ok"}), 200



@server.route('/api/devices', methods=['GET'])
def get_devices():
    config_path = os.path.join(BASE_DIR, 'devices_config.json')
    with open(config_path, 'r', encoding="utf-8") as f:
        return jsonify(json.load(f))

@server.route("/")
def inferance():
   template_path = os.path.join('index.html')

   return render_template(template_path)


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


@server.route("/api/led_strip", methods=["POST"])
def handle_lights():
    content = request.json

    device = content["device"]
    room = content["room"]
    dev_type = content["type"]
    command = content["command"]
    number = str(content["number"]) 

    Logger.info(f"/api/led_strip -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
    
    with open("devices_config.json", "r") as f:
        data = json.load(f)
    
    try:
        ip = data["Room"][room][dev_type][number]["ip"]
        
        
        led_strip = Tapo_Led_strip(ip)
        led_strip.command(command)

        return jsonify({"status": "success", "message": "Command received"}), 200
        
    except KeyError:
        return jsonify({"status": "error", "message": "Light device not found in config"}), 404
    


@server.route("/api/light", methods=["POST"])
def handle_led_strip():
    content = request.json

    device = content["device"]
    room = content["room"]
    dev_type = content["type"]
    command = content["command"]
    number = str(content["number"]) 

    Logger.info(f"/api/light -> Received the command {command} for the device {device}. This device is part of the {room} and it is a {dev_type}")
    
    with open("devices_config.json", "r") as f:
        data = json.load(f)
    
    try:
        ip = data["Room"][room][dev_type][number]["ip"]
        
        
        smart_bulb = Tapo_Smart_Bulbs(ip)
        smart_bulb.command(command)

        return jsonify({"status": "success", "message": "Command received"}), 200
        
    except KeyError:
        return jsonify({"status": "error", "message": "Light device not found in config"}), 404
   


@server.route("/api/tv", methods=["POST"])
def handle_tv():
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

def run_server():
    try:
        server.run("0.0.0.0", 8080, debug=True)
    except Exception as e:
        Logger.error(f"An error has occurred on the server: {e}")

if __name__ == "__main__":
    threading.Thread(target=main_bot_loop).start()
    run_server()
