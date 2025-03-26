from tkinter import *

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

        # Button 1
        self.b1 = Button(self.app, text="Start Map", command=lambda: self.handle_button_press())
        self.b1.grid(padx=10, pady=10)
        # Button 2
        self.b2 = Button(self.app, text="Start GPG1", command=lambda: self.handle_button_press())
        self.b2.grid(padx=10, pady=10)

        self.button_open_map = Button(self.app, text="Open map", command=lambda: self.handle_button_press("open_map"))
        self.button_open_map.grid(padx=10, pady=10)

    def open_control_panel(self):
        self.app.mainloop()

    def open_map(self):
        print("Open map button pressed.")
        self.location_map = Map(queue=self.location_queue, quit_flag=self.quit_flag, master=self.app)
        #self.location_map.run()

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