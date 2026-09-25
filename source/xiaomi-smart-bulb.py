from miio import Yeelight, LightBulb
from miio.exceptions import DeviceException

class XiaomiBulbController:
    """Έλεγχος Xiaomi / Yeelight Smart Bulbs & Lamps."""

    def __init__(self, ip: str, token: str = None):
        self.ip = ip
        self.token = token
        self.bulb = Yeelight(ip=self.ip, token=self.token)

    def turn_on(self):
        try:
            self.bulb.on()
            return True
        except DeviceException as e:
            print(f"[Xiaomi Bulb Error]: {e}")
            return False

    def turn_off(self):
        try:
            self.bulb.off()
            return True
        except DeviceException as e:
            print(f"[Xiaomi Bulb Error]: {e}")
            return False

    def set_brightness(self, level: int):
        """Ρύθμιση φωτεινότητας (1 έως 100)."""
        try:
            level = max(1, min(100, level))  # Clamping μεταξύ 1-100
            self.bulb.set_brightness(level)
            return True
        except DeviceException as e:
            print(f"[Xiaomi Bulb Error]: {e}")
            return False

    def set_rgb_color(self, red: int, green: int, blue: int):
        """Ρύθμιση χρώματος RGB (0-255 για κάθε κανάλι)."""
        try:
            self.bulb.set_rgb((red, green, blue))
            return True
        except DeviceException as e:
            print(f"[Xiaomi Bulb Error]: {e}")
            return False

    def set_color_temp(self, kelvin: int):
        """Ρύθμιση θερμοκρασίας λευκού (π.χ. 2700K θερμό - 6500K ψυχρό)."""
        try:
            self.bulb.set_color_temp(kelvin)
            return True
        except DeviceException as e:
            print(f"[Xiaomi Bulb Error]: {e}")
            return False