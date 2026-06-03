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


       prompt = {"prompt":message}

       response = utils.send_ai(prompt)["response"]

       self.awnser_box.insert(ctk.END,response['message']['content'])



app = App()
app.mainloop()