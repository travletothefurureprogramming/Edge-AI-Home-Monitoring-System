import customtkinter as ctk
import subprocess
import threading
import json
import os
import socket
from control.control import LG_TV, Phue, Samsung_TV
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import pyttsx4
import ctypes  
from broadlink_learn import broadlink_learn
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

if platform.system() == "Windows":
    engine = pyttsx4.init()
    engine.setProperty("rate", 150)
else:
    engine = None

def say(text):
    def target():
        try:
            ctypes.windll.ole32.CoInitialize(None)
            
            local_engine = pyttsx4.init()
            local_engine.say(text)
            local_engine.runAndWait()
            
            ctypes.windll.ole32.CoUninitialize()
        except Exception as e:
            print(f"TTS Error: {e}")
            
    threading.Thread(target=target, daemon=True).start()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x500")
        self.title("Edge AI Configuration Wizard")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_config_frame()

        say("Welcome to the Edge AI Configuration Wizard... I'll guide you through the system setup step by step. Let's get your Edge AI Home Monitoring System configured.")

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def update_env_file(self, key, value):
        env_path = os.path.join(CONFIG_DIR, ".env")

        dir_path = os.path.dirname(env_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        lines = []
        key_found = False

        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f'{key}="{value}"\n'
                key_found = True
                break

        if not key_found:
            lines.append(f'{key}="{value}"\n')

        with open(env_path, "w") as f:
            f.writelines(lines)

    def show_error(self, message):
        error_win = ctk.CTkToplevel(self)
        error_win.title("Σφάλμα")
        error_win.geometry("320x150")
        error_win.attributes("-topmost", True)

        ctk.CTkLabel(
            error_win, text=message, wraplength=280, text_color="#ff6b6b"
        ).pack(pady=20, padx=10)

        ctk.CTkButton(error_win, text="OK", command=error_win.destroy).pack(pady=10)
        say(message)

    def update_config_frame(self):
        if self.tailscale_var.get():
            say("Please enter the Tailscale IP address of your server.")
            self.next_btn.pack_forget()
            self.tailscale_entry.pack(pady=10)
            self.next_btn.pack(pady=10)
        else:
            say("The local network will be used.")
            self.tailscale_entry.pack_forget()

    def set_login_password(self):
        password = self.login_pass_entry.get()

        if not password:
            self.show_error("Please enter an administrator password.")
            return False

        self.update_env_file("APP_ADMIN_USER", "admin")
        self.update_env_file("PASSWORD", generate_password_hash(password))
        self.update_env_file("FLASK_SECRET_KEY", secrets.token_hex(32))
        return True

    def show_config_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="System Configuration", font=("Arial", 20, "bold")).pack(pady=20)

        self.login_pass_entry = ctk.CTkEntry(self.container, placeholder_text="Enter login password", width=200, show='*')
        self.login_pass_entry.pack(pady=10)

        self.next_btn = ctk.CTkButton(
            self.container,
            text="Next: Telegram Setup",
            fg_color="teal",
            command=self.handle_next_step
        )
        self.next_btn.pack(pady=20)
        
        say("Please create your administrator password and configure the server settings to continue.")

    def handle_next_step(self):
        if self.is_server_var.get():
            server_ip = self.get_local_ip()
            self.update_env_file("SERVER_IP", server_ip)
            print(f"Saved Server IP ({server_ip}) to .env")

        elif self.tailscale_var.get():
            server_ip = self.tailscale_entry.get().strip()
            if not server_ip:
                self.show_error("Συμπλήρωσε την Tailscale IP.")
                return
            self.update_env_file("SERVER_IP", server_ip)
            print(f"Saved Server IP ({server_ip}) to .env")

        if not self.set_login_password():
            return

        self.show_telegram_frame()

    def show_telegram_frame(self):
        say("Enter your Telegram Bot Token and Chat ID. If you don't need notifications, you can skip this step.")
        
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="Telegram Notification Setup", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self.container, text="Enter your Bot Token and Chat ID to receive alerts.", font=("Arial", 11), text_color="gray").pack(pady=5)

        self.telegram_token_entry = ctk.CTkEntry(self.container, placeholder_text="Telegram Bot Token", width=250)
        self.telegram_token_entry.pack(pady=10)

        self.telegram_chat_id_entry = ctk.CTkEntry(self.container, placeholder_text="Telegram Chat ID", width=250)
        self.telegram_chat_id_entry.pack(pady=10)

        save_tg_btn = ctk.CTkButton(
            self.container,
            text="Next: Add Devices",
            fg_color="teal",
            command=self.save_telegram_and_continue
        )
        save_tg_btn.pack(pady=20)

        back_btn = ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_config_frame)
        back_btn.pack(pady=5)

    def save_telegram_and_continue(self):
        token = self.telegram_token_entry.get().strip()
        chat_id = self.telegram_chat_id_entry.get().strip()

        if token:
            self.update_env_file("TELEGRAM_TOKEN", token)
        if chat_id:
            self.update_env_file("CHAT_ID", chat_id)

        print("Telegram configuration saved to .env")
        self.show_devices_frame()

    def show_devices_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        say("Telegram configuration saved. Now register your smart devices. Enter the room name, choose a device type, and enter its IP address.")

        ctk.CTkLabel(self.container, text="Register New Device", font=("Arial", 16)).pack(pady=10)

        self.room_entry = ctk.CTkEntry(self.container, placeholder_text="Room Name")
        self.room_entry.pack(pady=5)

        self.type_combobox = ctk.CTkComboBox(
            self.container,
            values=["android_tv", "tapo_light", "tapo_led_strip", "tapo_smart_plug",
                    "phue_light", "phue_led_strip", "yeelight", "lg_tv", "daikin_ac", 
                    "shelly", "kasa", "broadlink", "samsung_tv", "sonos"],
            command=self.on_type_change
        )
        self.type_combobox.pack(pady=5)

        self.name_entry = ctk.CTkEntry(self.container, placeholder_text="Device Name")
        self.name_entry.pack(pady=5)

        self.ip_entry = ctk.CTkEntry(self.container, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)

        self.creds_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.user_entry = ctk.CTkEntry(self.creds_frame, placeholder_text="Tapo Username")
        self.user_entry.pack(pady=2)
        self.pass_entry = ctk.CTkEntry(self.creds_frame, placeholder_text="Tapo Password", show="*")
        self.pass_entry.pack(pady=2)
        self.model = ctk.CTkEntry(self.creds_frame, placeholder_text="Device Model")
        self.model.pack(pady=2)

        self.phue_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.id_entry = ctk.CTkEntry(self.phue_frame, placeholder_text="ID of phue device")
        self.id_entry.pack(pady=2)
        self.shelly_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        self.rellay_numer_entry = ctk.CTkEntry(
            self.shelly_frame,
            placeholder_text="Relay Number of Shelly device"
        )
        self.rellay_numer_entry.pack(pady=2)

        ctk.CTkButton(self.container, text="Save Device", command=self.save_to_json).pack(pady=15)
        ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_telegram_frame).pack(pady=5)

    def on_type_change(self, choice):
        if choice in ["tapo_light", "tapo_led_strip", "tapo_smart_plug"]:
            self.creds_frame.pack(pady=5)
            say(f"You have chosen {choice}. For this device type you must enter the: Tapo Username, Tapo Password, Device Model")
        else:
            self.creds_frame.pack_forget()

        if choice in ["phue_light", "phue_led_strip"]:
            self.phue_frame.pack(pady=5)
            say(f"You have chosen {choice}. For this device type you must enter the: phue id of your device")
        else:
            self.phue_frame.pack_forget()

        if choice == "shelly":
            self.shelly_frame.pack(pady=5)
            say(f"You have chosen {choice}. For this device type you must enter the: relay number which the device is connected on.")
        else:
            self.shelly_frame.pack_forget()

        if choice == "broadlink":
            broadlink_learn.App()

        if choice not in ["tapo_light", "tapo_led_strip", "tapo_smart_plug", "phue_light", "phue_led_strip", "shelly"]:
            say(f"You have chosen {choice}.")

    def save_to_json(self):
        room = self.room_entry.get().strip()
        dev_type = self.type_combobox.get()
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()

        if not room or not name or not ip:
            self.show_error("Συμπλήρωσε Room, Name και IP.")
            return

        device_data = {"name": name, "type": dev_type, "ip": ip}

        if dev_type in ["tapo_light", "tapo_led_strip", "tapo_smart_plug"]:
            username = self.user_entry.get().strip()
            password = self.pass_entry.get().strip()
            model = self.model.get().strip()

            if not username or not password:
                self.show_error("Συμπλήρωσε Tapo Username και Password.")
                return

            device_data["username"] = username
            device_data["password"] = password
            device_data["model"] = model

            self.update_env_file("TAPO_USERNAME", username)
            self.update_env_file("TAPO_PASSWORD", password)

        if dev_type in ["phue_light", "phue_led_strip"]:
            phue_id = self.id_entry.get().strip()
            if not phue_id:
                self.show_error("Συμπλήρωσε το ID της συσκευής Phue.")
                return
            device_data["id"] = phue_id

        if dev_type == "shelly":
            rellay_numer = self.rellay_numer_entry.get().strip()

            if not rellay_numer:
                self.show_error("Συμπλήρωσε το Relay Number της συσκευής Shelly.")
                return
            device_data["rellay_numer"] = rellay_numer

        try:
            if dev_type == "lg_tv":
                LG_TV(ip)
            if dev_type in ["phue_light", "phue_led_strip"]:
                Phue(ip)
            if dev_type == "samsung_tv":
                Samsung_TV(ip)
        except Exception as e:
            self.show_error(
                f"Αποτυχία σύνδεσης με τη συσκευή: {e}\n\n"
                "Βεβαιώσου ότι είναι αναμμένη/συνδεδεμένη στο δίκτυο "
                "(για Phue: πάτησε το link button στο bridge πριν πατήσεις Save)."
            )
            return

        file_path = os.path.join(CONFIG_DIR, "devices_config.json")
        data = {"Room": {}}

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass

        if room not in data["Room"]:
            data["Room"][room] = {}
        if dev_type not in data["Room"][room]:
            data["Room"][room][dev_type] = {}

        existing_ids = [int(i) for i in data["Room"][room][dev_type].keys()]
        new_id = str(max(existing_ids, default=0) + 1)

        data["Room"][room][dev_type][new_id] = device_data

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Successfully saved {name} ({dev_type}) in {room}")

        self.room_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.ip_entry.delete(0, "end")
        self.user_entry.delete(0, "end")
        self.pass_entry.delete(0, "end")
        self.model.delete(0, "end")
        self.id_entry.delete(0, "end")


if __name__ == "__main__":
    app = App()
    app.mainloop()