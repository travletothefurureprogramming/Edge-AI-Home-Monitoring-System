import json
import os
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, SystemControl, InputControl

STORE_FILE = "lg_store.json"

def your_custom_storage_is_empty():
    return not os.path.exists(STORE_FILE)

def load_from_your_custom_storage():
    with open(STORE_FILE, "r") as f:
        return json.load(f)

def persist_to_your_custom_storage(store):
    with open(STORE_FILE, "w") as f:
        json.dump(store, f)

store = load_from_your_custom_storage() if not your_custom_storage_is_empty() else {}

client = WebOSClient("192.168.1.3",secure=True)  
client.connect()

for status in client.register(store):
    if status == WebOSClient.PROMPTED:
        print("Please accept the connect on the TV!")
    elif status == WebOSClient.REGISTERED:
        print("Registration successful!")

persist_to_your_custom_storage(store)

# Controls
media = MediaControl(client)
system = SystemControl(client)
inputc = InputControl(client)

media.volume_up()          
media.volume_down()        
media.get_volume()         
                          
media.set_volume(25)   

cur_media_output_source = media.get_audio_output()   
audio_outputs = media.list_audio_output_sources()    
print(cur_media_output_source,audio_outputs)