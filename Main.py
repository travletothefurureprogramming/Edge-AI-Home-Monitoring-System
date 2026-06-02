import backend
from android_tv_rc.logger import Logger
import threading

def run():
 backend.server.run("0.0.0.0",8080,debug=True)

try:
 run()

except:
 Logger.error("An error has occured on the server!")
