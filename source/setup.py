import customtkinter as ctk
import subprocess
import threading
import json
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Setup Wizard")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_install_frame()

    def show_install_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="System Setup").pack(pady=10)
        self.install_btn = ctk.CTkButton(self.container, text="Install packages", command=self.install_thread)
        self.install_btn.pack(pady=10)
        
        ctk.CTkButton(self.container, text="Next", command=self.show_devices_frame).pack(pady=10)

    def show_devices_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="Add Device").pack(pady=5)
        
        self.room_entry = ctk.CTkEntry(self.container, placeholder_text="Room Name")
        self.room_entry.pack(pady=5)
        
        self.type_entry = ctk.CTkEntry(self.container, placeholder_text="Type (TV/Router/etc)")
        self.type_entry.pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(self.container, placeholder_text="Device Name")
        self.name_entry.pack(pady=5)
        
        self.ip_entry = ctk.CTkEntry(self.container, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)

        ctk.CTkButton(self.container, text="Save Device", command=self.save_to_json).pack(pady=10)

    def save_to_json(self):
        room = self.room_entry.get()
        dev_type = self.type_entry.get()
        name = self.name_entry.get()
        ip = self.ip_entry.get()

        file_path = "devices_config.json"
        data = {"Room": {}}
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try: data = json.load(f)
                except: pass

        if room not in data["Room"]: data["Room"][room] = {}
        if dev_type not in data["Room"][room]: data["Room"][room][dev_type] = {}
        
        new_id = str(len(data["Room"][room][dev_type]) + 1)
        data["Room"][room][dev_type][new_id] = {"name": name, "type": dev_type, "ip": ip}

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Saved: {name} in {room}")

    def install_thread(self):
        self.install_btn.configure(state="disabled", text="Installing...")
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            self.install_btn.configure(text="Done!", fg_color="green")
        except Exception as e:
            self.install_btn.configure(text="Error", fg_color="red")
        finally:
            self.install_btn.configure(state="normal")

app = App()
app.mainloop()