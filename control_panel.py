from tkinter import *

class Control_Panel:
    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.chosen_client_id = None

        self.app = Tk()
        self.app.title("Control Panel")

        # Button 1
        self.b1 = Button(self.app, text="Start Map", command=lambda: self.handle_button_press())
        self.b1.grid(padx=10, pady=10)
        # Button 2
        self.b2 = Button(self.app, text="Start GPG1", command=lambda: self.handle_button_press())
        self.b2.grid(padx=10, pady=10)

        # Käynnistä Tkinter-looppi
        self.app.mainloop()

    def handle_button_press(self, command):
        if command != None or command != "":

            self.command_queue.put(
                {
                    "id": self.chosen_client_id,
                    "command": command
                }
            )