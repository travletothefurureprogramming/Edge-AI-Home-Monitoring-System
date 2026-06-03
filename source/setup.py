import customtkinter as ctk
import subprocess
import threading
import json
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x550")
        self.title("Edge AI Setup Wizard")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_install_frame()

    def show_install_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="System Setup", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.install_btn = ctk.CTkButton(self.container, text="Install Dependencies", command=self.install_thread)
        self.install_btn.pack(pady=10)
        
        self.model_btn = ctk.CTkButton(self.container, text="Download AI Model (Phi3)", command=self.model_thread)
        self.model_btn.pack(pady=10)
        
        ctk.CTkButton(self.container, text="Next: Add Devices", fg_color="teal", command=self.show_devices_frame).pack(pady=20)

    def show_devices_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="Register New Device", font=("Arial", 16)).pack(pady=10)
        
        self.room_entry = ctk.CTkEntry(self.container, placeholder_text="Room Name")
        self.room_entry.pack(pady=5)
        
        self.type_combobox = ctk.CTkComboBox(self.container, values=["TV", "light"], command=self.on_type_change)
        self.type_combobox.pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(self.container, placeholder_text="Device Name")
        self.name_entry.pack(pady=5)
        
        self.ip_entry = ctk.CTkEntry(self.container, placeholder_text="IP Address")
        self.ip_entry.pack(pady=5)

        # Container για credentials (εμφανίζεται μόνο για lights)
        self.creds_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.user_entry = ctk.CTkEntry(self.creds_frame, placeholder_text="Tapo Username")
        self.user_entry.pack(pady=2)
        self.pass_entry = ctk.CTkEntry(self.creds_frame, placeholder_text="Tapo Password", show="*")
        self.pass_entry.pack(pady=2)

        ctk.CTkButton(self.container, text="Save Device", command=self.save_to_json).pack(pady=15)
        ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_install_frame).pack(pady=5)

    def on_type_change(self, choice):
        if choice == "light":
            self.creds_frame.pack(pady=5)
        else:
            self.creds_frame.pack_forget()

    def save_to_json(self):
        room = self.room_entry.get()
        dev_type = self.type_combobox.get()
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        
        device_data = {"name": name, "type": dev_type, "ip": ip}
        
        if dev_type == "light":
            device_data["username"] = self.user_entry.get()
            device_data["password"] = self.pass_entry.get()

            with open("source/files/.env","w") as f:
                f.write('TAPO_USERNAME='+f'"{device_data["username"]}"'+'\n'+'TAPO_PASSWORD='+f'"{device_data["password"]}"')
            f.close()

        file_path = "devices_config.json"
        data = {"Room": {}}
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try: data = json.load(f)
                except: pass

        if room not in data["Room"]: data["Room"][room] = {}
        if dev_type not in data["Room"][room]: data["Room"][room][dev_type] = {}
        
        new_id = str(len(data["Room"][room][dev_type]) + 1)
        data["Room"][room][dev_type][new_id] = device_data

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Successfully saved {name} ({dev_type}) in {room}")

    def install_thread(self):
        self.install_btn.configure(state="disabled", text="Installing...")
        threading.Thread(target=self.run_install, daemon=True).start()

    def model_thread(self):
        self.model_btn.configure(state="disabled", text="Downloading model...")
        threading.Thread(target=self.download_model, daemon=True).start()

    def run_install(self):
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            self.install_btn.configure(text="Packages Ready!", fg_color="green")
        except Exception:
            self.install_btn.configure(text="Install Error", fg_color="red")
        finally:
            self.install_btn.configure(state="normal")

    def download_model(self):
        try:
            subprocess.run(["ollama", "pull", "phi3"], check=True)
            self.model_btn.configure(text="Model Ready!", fg_color="green")
        except Exception:
            self.model_btn.configure(text="Model Error", fg_color="red")
        finally:
            self.model_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()