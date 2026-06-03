import ollama
import customtkinter as ctk
import utils
import threading

class App(ctk.CTk):
   def __init__(self, fg_color = None, **kwargs):
       super().__init__(fg_color, **kwargs)

       self.geometry("850x600")


       self.title("AI HOME SYSTEM")

       self.main_label = ctk.CTkLabel(self,text="AI HOME SYSTEM", font=('Times New Roman', 25))
       self.main_label.pack(side='top', anchor='center')

       self.command_entry = ctk.CTkEntry(self,width=160)
       self.command_entry.pack(side='top', anchor='center')
       
       self.button_send = ctk.CTkButton(self,text="Send",command=self.safe_send)
       self.button_send.pack(side='top', anchor='center')

       self.awnser_box = ctk.CTkTextbox(self,width=700,height=500)
       self.awnser_box.pack(side='top', anchor='center')

   def safe_send(self):
      threading.Thread(target=self.send).start()

   def send(self):
       message = self.command_entry.get()

       self.awnser_box.delete('1.0', ctk.END)

       if "tv" in message.lower():
           if "on" in message.lower():
               if "maria" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will turn on maria's TV")
                 utils.send_tv({
                    "device":"Maria_TV",
                    "room":"Maria_Room",
                    "number":"1",
                    "type":"TV",
                    "command":"on"
                 })
               elif "tv box" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will turn on tv box")
                 utils.send_tv({
                    "device":"Bedrooms_TV",
                    "room":"Main_Bedroom",
                    "number":"1",
                    "type":"TV",
                    "command":"on"
                 })

           elif "off" in message.lower():
              if "maria" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will turn off maria's TV")
                 utils.send_tv({
                    "device":"Maria_TV",
                    "room":"Maria_Room",
                    "number":"1",
                    "type":"TV",
                    "command":"off"
                 })
              elif "tv box" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will turn off tv box")
                 utils.send_tv({
                    "device":"Bedrooms_TV",
                    "room":"Main_Bedroom",
                    "number":"1",
                    "type":"TV",
                    "command":"on"
                 })

           elif "channel up" in message.lower():
              if "maria" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will change channel on maria's TV")
                 utils.send_tv({
                    "device":"Maria_TV",
                    "room":"Maria_Room",
                    "number":"1",
                    "type":"TV",
                    "command":"channel_up"
                 })
              elif "tv box" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will change channel on tv box")
                 utils.send_tv({
                    "device":"Bedrooms_TV",
                    "room":"Main_Bedroom",
                    "number":"1",
                    "type":"TV",
                    "command":"channel_up"
                 })

           elif "channel down" in message.lower():
              if "maria" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will change channel on maria's TV")
                 utils.send_tv({
                    "device":"Maria_TV",
                    "room":"Maria_Room",
                    "number":"1",
                    "type":"TV",
                    "command":"channel_down"
                 })
              elif "tv box" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will change channel on tv box")
                 utils.send_tv({
                    "device":"Bedrooms_TV",
                    "room":"Main_Bedroom",
                    "number":"1",
                    "type":"TV",
                    "command":"channel_down"
                 })

              elif "led strip" in message.lower():
               if "on" in message.lower():
                 self.awnser_box.insert(ctk.END,"Okay I will turn on led strip")
                 utils.send_tv({
                    "device":"tapo_led_strip",
                    "room":"Gregorys_Bedroom",
                    "number":"1",
                    "type":"lights",
                    "command":"on"
                 })
              
               elif "off" in message.lower():
                  self.awnser_box.insert(ctk.END,"Okay I will turn off led strip")
                  utils.send_tv({
                    "device":"tapo_led_strip",
                    "room":"Gregorys_Bedroom",
                    "number":"1",
                    "type":"lights",
                    "command":"off"
                 })


       else:       
        prompt = {"prompt":message}

        response = utils.send_ai(prompt)["response"]

        self.awnser_box.insert(ctk.END,response['message']['content'])



app = App()
app.mainloop()