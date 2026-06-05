import customtkinter as ctk
import subprocess
import threading
import json
import os
import socket  # Χρησιμοποιείται για να βρούμε την IP του μηχανήματος
from control import LG_TV

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x600")  # Μικρή αύξηση στο ύψος για άνεση στα frames
        self.title("Edge AI Setup Wizard")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_install_frame()

    def get_local_ip(self):
        """Επιστρέφει την τοπική IP διεύθυνση αυτού του μηχανήματος."""
        try:
            # Δημιουργούμε ένα ψεύτικο UDP socket για να βρούμε το primary interface IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def update_env_file(self, key, value):
        """Ενημερώνει ή προσθέτει ένα key-value pair στο .env αρχείο χωρίς να διαγράφει τα υπόλοιπα."""
        env_path = ".env"

        # Δημιουργεί φάκελο ΜΟΝΟ αν υπάρχει directory στο path
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

    def update_install_frame(self):
        """Εμφανίζει ή κρύβει το Entry ανάλογα με το Checkbox, διατηρώντας τη σειρά."""
        if self.tailscale_var.get():
            # Κρύβουμε προσωρινά το Next για να μπει το Entry από πάνω του
            self.next_btn.pack_forget()
            self.tailscale_entry.pack(pady=10)
            self.next_btn.pack(pady=10)
        else:
            self.tailscale_entry.pack_forget()

    def show_install_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="System Setup", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.install_btn = ctk.CTkButton(self.container, text="Install Dependencies", command=self.install_thread)
        self.install_btn.pack(pady=10)
        
        self.model_btn = ctk.CTkButton(self.container, text="Download AI Model (Phi3)", command=self.model_thread)
        self.model_btn.pack(pady=10)
        
        # --- Checkbox για τον Server ---
        self.is_server_var = ctk.BooleanVar(value=False)
        self.server_chk = ctk.CTkCheckBox(
            self.container, 
            text="Is this machine the Server?", 
            variable=self.is_server_var
        )
        self.server_chk.pack(pady=20)
        # --------------------------------
        
        self.tailscale_var = ctk.BooleanVar(value=False)
        self.tailscale_chk = ctk.CTkCheckBox(
            self.container, 
            text="Do you have tailscale?", 
            variable=self.tailscale_var,
            command=self.update_install_frame
        )
        self.tailscale_chk.pack(pady=20)

        # ΔΙΟΡΘΩΣΗ: Αλλαγή parent από self σε self.container και προσθήκη placeholder
        self.tailscale_entry = ctk.CTkEntry(self.container, placeholder_text="Enter Tailscale IP", width=200)

        # ΔΙΟΡΘΩΣΗ: Μετατροπή σε self.next_btn για πρόσβαση από την update_install_frame
        self.next_btn = ctk.CTkButton(
            self.container, 
            text="Next: Telegram Setup", 
            fg_color="teal", 
            command=self.handle_next_step
        )
        self.next_btn.pack(pady=10)

    def handle_next_step(self):
        """Αποθηκεύει την IP αν επιλέχθηκε ως server και προχωράει στο Telegram frame."""
        if self.is_server_var.get():
            server_ip = self.get_local_ip()
            self.update_env_file("SERVER_IP", server_ip)
            print(f"Saved Server IP ({server_ip}) to .env")
        
        elif self.tailscale_var.get():
            server_ip = self.tailscale_entry.get().strip()
            self.update_env_file("SERVER_IP", server_ip)
            print(f"Saved Server IP ({server_ip}) to .env")
        
        self.show_telegram_frame()

    def show_telegram_frame(self):
        """Νέο Step για την εισαγωγή των Telegram Credentials."""
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

        back_btn = ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_install_frame)
        back_btn.pack(pady=5)

    def save_telegram_and_continue(self):
        """Αποθηκεύει τα Telegram tokens στο .env και συνεχίζει στις συσκευές."""
        token = self.telegram_token_entry.get().strip()
        chat_id = self.telegram_chat_id_entry.get().strip()

        if token:
            self.update_env_file("TELEGRAM_TOKEN", token)
        if chat_id:
            self.update_env_file("TELEGRAM_CHAT_ID", chat_id)

        print("Telegram configuration saved to .env")
        self.show_devices_frame()

    def show_devices_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.container, text="Register New Device", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(self.container, text="*In type light and ledstrip refers to tapo see more on our github readme", font=("Arial", 12)).pack()
        
        self.room_entry = ctk.CTkEntry(self.container, placeholder_text="Room Name")
        self.room_entry.pack(pady=5)
        
        self.type_combobox = ctk.CTkComboBox(self.container, values=["android_tv", "light", "led_strip", "lg_tv"], command=self.on_type_change)
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
        
        # Το Back επιστρέφει πλέον στο Telegram Setup
        ctk.CTkButton(self.container, text="Back", fg_color="gray", command=self.show_telegram_frame).pack(pady=5)

    def on_type_change(self, choice):
        if choice == "light" or choice == "led_strip":
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

            self.update_env_file("TAPO_USERNAME", device_data["username"])
            self.update_env_file("TAPO_PASSWORD", device_data["password"])

        if dev_type == "lg_tv":
            lg_tv = LG_TV(ip)

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