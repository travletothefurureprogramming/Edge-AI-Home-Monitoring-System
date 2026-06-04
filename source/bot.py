import requests
import time
import json
import os
import utils

TOKEN = "8998096928:AAHfxCOWoZ8Um032pdqhyuKk9IN3YNolYmk"
CHAT_ID = "8532508249"

# Διεύθυνση του Flask backend σου (άλλαξέ το αν τρέχει σε άλλη πόρτα/IP)
BACKEND_URL = "http://127.0.0.1:8080"

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
    config_path = "devices_config.json"
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
    if dev_type.lower() == "tv":
        endpoint = f"{BACKEND_URL}/api/tv"
    elif dev_type.lower() == "light":
        endpoint = f"{BACKEND_URL}/api/light"
    else:
        endpoint = f"{BACKEND_URL}/api/led_strip"


    if action in ["άναψε", "on", "open", "άνοιξε"]:
        command_str = "power" if dev_type.lower() == "tv" else "on"
    elif action in ["κλείσε", "off", "close"]:
        command_str = "power" if dev_type.lower() == "tv" else "off"
    elif action in ["channel up", "πάνω", "επόμενο"]:
        command_str = "channel_up"
    elif action in ["channel down", "κάτω", "προηγούμενο"]:
        command_str = "channel_down"
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
        action = "channel_up"
    elif "down" in command_lower or "κάτω" in command_lower:
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
                    utils.send_security({"status":"on"})
                    send_telegram_message("📹 Το σύστημα ασφαλείας και η κάμερα ενεργοποιήθηκαν.")
                elif "κλείσε την κάμερα" in command or "camera off" in command:
                    utils.send_security({"status":"off"})
                    send_telegram_message("🛑 Το σύστημα ασφαλείας απενεργοποιήθηκε.")

                elif "/ai" in command:
                   
                   prompt = {"prompt":command}
                   response = utils.send_ai(prompt)["response"]
                   send_telegram_message(response['message']['content'])

                
                # 3. Δυναμικός έλεγχος όλων των άλλων συσκευών από το JSON
                else:
                    reply = parse_and_execute(message_text)
                    send_telegram_message(reply)
                    
        time.sleep(2)

if __name__ == "__main__":
    main_bot_loop()