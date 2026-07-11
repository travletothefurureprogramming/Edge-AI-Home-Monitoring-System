import broadlink
import customtkinter as ctk
from tkinter import messagebox
import pyttsx4
import json
import os
import time
import threading  
import ctypes  

engine = pyttsx4.init()


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

JSON_FILE = "broadlink_codes.json"
CONFIG_FILE = "devices_config.json"  

class App:
    def __init__(self):
        self.device = None
        self.device_ip = "Unknown"  

        self.app = ctk.CTk()
        self.app.title("ROADLINK LEARN")
        self.app.geometry("350x450") 

        self.title_label = ctk.CTkLabel(self.app, text="BROADLINK LEARN", font=("Arial", 25))
        self.title_label.pack(pady=10)

        self.ip_entry = ctk.CTkEntry(self.app, placeholder_text="Enter device ip")
        self.ip_entry.pack(pady=5)



        self.device_name_entry = ctk.CTkEntry(self.app, placeholder_text="Device Name")
        self.device_name_entry.pack(pady=5)

        self.room_name_entry = ctk.CTkEntry(self.app, placeholder_text="Room Name")
        self.room_name_entry.pack(pady=5)

        self.dev_type = ctk.CTkComboBox(
            self.app, 
            values=["Select Device Type", "TV", "AC", "Decoder"],
            command=self.update_commands
        )
        self.dev_type.pack(pady=5)

        self.command_entry = ctk.CTkComboBox(self.app, values=["Select Command"])
        self.command_entry.pack(pady=5)

        self.connect_button = ctk.CTkButton(self.app, text="Connect with Broadlink device", command=self.connect)
        self.connect_button.pack(pady=5)

        self.learn_button = ctk.CTkButton(self.app, text="Learn & Save Command", fg_color="green", hover_color="darkgreen", command=self.enter_learning_mode)
        self.learn_button.pack(pady=15)

        self.app.after(500, lambda: say("Hello. First, enter the ip adress and press connect with Broadlink device. Then, select the device type and command you want to learn. Finally, press the Learn and Save Command button."))

        self.app.mainloop()

    def update_commands(self, selected_type):
        commands = self.get_command_values(selected_type)
        if commands:
            self.command_entry.configure(values=commands)
            self.command_entry.set(commands[0]) 
        else:
            self.command_entry.configure(values=["Select Command"])
            self.command_entry.set("Select Command")

    def get_command_values(self, dev_type):
        if dev_type == "TV":
            return [
                "on", "off", "channel_up", "channel_down", 
                "volume_up", "volume_down", "mute",
                "up", "down", "left", "right", "ok", 
                "back", "exit", "menu", "home"
            ]
        elif dev_type == "AC":
            return ["on", "off", "increase_temperature", "decrease_temperature"]
        elif dev_type == "Decoder":
            return [
                "on", "off", "channel_up", "channel_down", 
                "volume_up", "volume_down", "mute",
                "up", "down", "left", "right", "ok", 
                "back", "exit", "menu", "home"
            ]
        else:
            return []
        
    def connect(self):
        self.device_ip = self.ip_entry.get()
        self.device = broadlink.hello(self.device_ip)
        self.device.auth()
       
        
        messagebox.showinfo("Success", f"Connected to {self.device.get_type()} ({self.device_ip})!")
    
    def enter_learning_mode(self):
        if not self.device:
            messagebox.showwarning("Warning", "Please connect to a Broadlink device first!")
            return
        
        room = self.room_name_entry.get().strip()
        device_name = self.device_name_entry.get().strip()
        dev_type_selected = self.dev_type.get()
        command = self.command_entry.get()

        if not room or not device_name or dev_type_selected == "Select Device Type" or command == "Select Command":
            messagebox.showwarning("Warning", "Please fill all fields correctly!")
            return

        self.device.enter_learning()
        
        say("The device has entered learning mode.")
        say("When the LED blinks, point the remote at the Broadlink device and press the button you want to learn.")
        
        time.sleep(5)

        try:
            packet = self.device.check_data()
            hex_packet = packet.hex()

            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}

            if room not in data:
                data[room] = {}
            if device_name not in data[room]:
                data[room][device_name] = {}
            
            data[room][device_name][command] = hex_packet

            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)


            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            else:
                config_data = {"Room": {}}

            if "Room" not in config_data:
                config_data["Room"] = {}
            if room not in config_data["Room"]:
                config_data["Room"][room] = {}
            
            device_key = device_name.lower().replace(" ", "_")
            if device_key not in config_data["Room"][room]:
                config_data["Room"][room][device_key] = {}

            devices = config_data["Room"][room][device_key]

            index = 1
            while str(index) in devices:
                index += 1

            devices[str(index)] = {
                "name": device_name,
                "type": dev_type_selected.lower(),
                "ip": self.device_ip,
                "is_broadlink_device": True
            }

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Saved", f"Command saved! Configuration updated in {CONFIG_FILE}!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = App()