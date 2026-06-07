from android_tv_rc.android_tv_controller import AndroidTVController
import utils
import asyncio
from tapo import ApiClient
import os
from dotenv import load_dotenv, dotenv_values 
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, SystemControl, InputControl
import json

load_dotenv(".env")

tv_registry = {}

def get_tv_controller(ip):
    global tv_registry
    if ip not in tv_registry:
        print(f"Δημιουργία νέου connection για {ip}...")
        controller = AndroidTVController(ip)
        if controller.connect():
            tv_registry[ip] = controller
            utils.send_to_server({"module": "TV", "type": "connection", "error": None, "action": "reset"})
        else:
            utils.send_to_server({"module": "TV", "type": "connection", "error": f"Failed {ip}"})
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

class Tapo_Smart_Plugs:
    def __init__(self,ip,device):
     self.tapo_username = os.getenv("TAPO_USERNAME")
     self.tapo_password = os.getenv("TAPO_PASSWORD")

     self.ip_address = ip
     self.device = device

     self.client = ApiClient(self.tapo_username, self.tapo_password)

    async def async_connect(self):
        if self.device == "p100":
         self.device = await self.client.p100(self.ip_address)
        elif self.device == "p105":
         self.device = await self.client.p105(self.ip_address)  
        elif self.device == "p115":
         self.device = await self.client.p115(self.ip_address)
        elif self.device == "p110":
         self.device = await self.client.p110(self.ip_address)
        elif self.device == "P300":
         self.device = await self.client.p300(self.ip_address)
        elif self.device == "p306":
         self.device = await self.client.p306(self.ip_address)
        elif self.device == "p304":
         self.device = await self.client.p304(self.ip_address)
        
        

    async def async_execute_command(self, command):
        device = await self.client.l900(self.ip_address)
        match command:
            case "on": await device.on()
            case "off": await device.off()
    
    def connect(self):
        asyncio.run(self.async_connect())
    
    def command(self,command):
        asyncio.run(self.async_execute_command(command))


        
        

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
        self.STORE_FILE = os.path.join(os.path.dirname(__file__), "lg_store.json")

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
