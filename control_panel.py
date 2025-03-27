from tkinter import *
import threading

from map import Map

class Control_Panel:
    def __init__(self, command_queue, location_queue, quit_flag):
        self.command_queue = command_queue

        self.location_queue = location_queue
        self.quit_flag = quit_flag

        self.chosen_client_id = None

        self.location_map: None|Map = None

        self.app = Tk()
        self.app.title("Control Panel")
        self.app.geometry("600x400")

        # Button 1
        self.b1 = Button(self.app, text="Start Map", command=lambda: self.handle_button_press())
        self.b1.grid(padx=10, pady=10)
        # Button 2
        self.b2 = Button(self.app, text="Start GPG1", command=lambda: self.handle_button_press())
        self.b2.grid(padx=10, pady=10)

        self.button_open_map = Button(self.app, text="Open map", command=lambda: self.handle_button_press("open_map"))
        self.button_open_map.grid(padx=10, pady=10)
        
        self.start_node_var = StringVar()
        self.end_node_var = StringVar()
        
        self.start_node_var.trace_add("write", self.force_uppercase)
        self.end_node_var.trace_add("write", self.force_uppercase)
        
        self.create_node_fields()

        self.app.bind("<Escape>", self.close_app)

    def close_app(self, event):
        
        self.app.destroy() #Close the control panel window

    def create_node_fields(self):
     
        aloitus_label = Label(self.app, text='Aloitus', font=('calibre', 10, 'bold'))
        aloitus_label.grid(row=0, column=10, padx=10, pady=5)
        
        aloitus_syöttö = Entry(self.app, textvariable=self.start_node_var, font=('calibre', 10, 'normal'), width=5)
        aloitus_syöttö.grid(row=0, column=11, padx=10, pady=5)

        lopetus_label = Label(self.app, text='Lopetus', font=('calibre', 10, 'bold'))
        lopetus_label.grid(row=1, column=10, padx=10, pady=5)
        
        lopetus_syöttö = Entry(self.app, textvariable=self.end_node_var, font=('calibre', 10, 'normal'), width=5)
        lopetus_syöttö.grid(row=1, column=11, padx=10, pady=5)

        sub_btn = Button(self.app, text='Hae Reitti', command=self.submit)
        sub_btn.grid(row=1, column=12, pady=7)
        
    def submit(self):
        Aloitus = self.start_node_var.get()
        Lopetus = self.end_node_var.get()

        print(f"Aloitus Node: {Aloitus}")
        print(f"Lopetus Node: {Lopetus}")
        
        self.start_node_var.set("")
        self.end_node_var.set("")
        
    def force_uppercase(self, *args):
   
        self.start_node_var.set(self.start_node_var.get().upper())
        self.end_node_var.set(self.end_node_var.get().upper())


    def open_control_panel(self):
        self.app.mainloop()

    def open_map(self):
        print("Open map button pressed.")
        self.location_map = Map(queue=self.location_queue, quit_flag=self.quit_flag, master=self.app)
        (threading.Thread(target=self.location_map.run, daemon=True)).start()

    def handle_button_press(self, command):
        print(command)
        if command == None or command == "":
            print("No command received")

            self.command_queue.put(
                {
                    "id": self.chosen_client_id,
                    "command": command
                }
            )
        elif command == "open_map":
            print("open_map command received.")
            self.open_map()