import customtkinter as ctk
import subprocess
import threading
import json
import os
import webbrowser

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x450")
        self.title("Setup Wizard - Final")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_install_frame()

    def show_install_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="System Setup", font=("Arial", 20, "bold")).pack(pady=10)
        
        self.install_btn = ctk.CTkButton(self.container, text="Install packages", command=self.install_thread)
        self.install_btn.pack(pady=5)
        
        self.model_btn = ctk.CTkButton(self.container, text="Download AI Model (Phi3)", command=self.model_thread)
        self.model_btn.pack(pady=5)
        
        ctk.CTkButton(self.container, text="Next: Add Devices", command=self.show_devices_frame).pack(pady=20)

    def show_devices_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="Add Device", font=("Arial", 16)).pack(pady=5)
        
        self.room_entry = ctk.CTkEntry(self.container, placeholder_text="Room Name")
        self.room_entry.pack(pady=5)
        
        self.type_entry = ctk.CTkEntry(self.container, placeholder_text="Type (TV/light)")
        self.type_entry.pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(self.container, placeholder_text="Device Name")
        self.name_entry.pack(pady=5)
        
        self.ip_entry = ctk.CTkEntry(self.container, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)

        ctk.CTkButton(self.container, text="Save Device", command=self.save_to_json).pack(pady=10)
        ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_install_frame).pack(pady=5)

    def save_to_json(self):
        room, dev_type, name, ip = self.room_entry.get(), self.type_entry.get(), self.name_entry.get(), self.ip_entry.get()
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

    def model_thread(self):
        self.model_btn.configure(state="disabled", text="Downloading model...")
        threading.Thread(target=self.download_model, daemon=True).start()

    def run_install(self):
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            self.install_btn.configure(text="Packages Installed!", fg_color="green")
        except Exception:
            self.install_btn.configure(text="Error", fg_color="red")
        finally:
            self.install_btn.configure(state="normal")

    def download_model(self):
        try:
            subprocess.run(["ollama", "pull", "phi3"], check=True)
            self.model_btn.configure(text="Model Ready!", fg_color="green")
        except Exception:
            self.model_btn.configure(text="Error downloading", fg_color="red")
        finally:
            self.model_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()