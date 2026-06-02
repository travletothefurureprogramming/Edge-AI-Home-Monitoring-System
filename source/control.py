from android_tv_rc.android_tv_controller import AndroidTVController
import utils


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