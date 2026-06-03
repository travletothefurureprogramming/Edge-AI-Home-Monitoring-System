from android_tv_rc.android_tv_controller import AndroidTVController
import utils
import asyncio
from tapo import ApiClient
import os
from dotenv import load_dotenv, dotenv_values 

load_dotenv()

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


class Led_strip:
    def __init__(self):
     self.tapo_username = os.getenv("TAPO_USERNAME")
     self.tapo_password = os.getenv("TAPO_PASSWORD")

     data = utils.read_json_file("source/files/devices.json")
     ip = data["Room"]["Gregorys_Bedroom"]["lights"]["1"]["ip"]

     self.ip_address = ip

     self.client = ApiClient(self.tapo_username, self.tapo_password)
    
    async def async_connect(self):
        self.device = await self.client.l900(self.ip_address)

    async def async_command(self,command):
        match command:
            case "on": await self.device.on()
            case "off": await self.device.off()
    
    def connect(self):
        asyncio.run(self.async_connect())
    
    def command(self,command):
        asyncio.run(self.async_command(command))

        

