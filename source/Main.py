import backend
from android_tv_rc.logger import Logger
import threading
import os
import bot

def run_server():
    try:
        backend.server.run("0.0.0.0", 8080, debug=True)
    except Exception as e:
        Logger.error(f"An error has occurred on the server: {e}")

if __name__ == "__main__":
    threading.Thread(target=bot.main_bot_loop).start()
    run_server()
