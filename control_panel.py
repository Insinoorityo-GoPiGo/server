from tkinter import *

class Control_Panel:
    def __init__(self):
        self.app = Tk()
        self.app.title("Control Panel")

        # Button 1
        self.b1 = Button(self.app, text="Start Map", command=lambda: self.which_button("MAP"))
        self.b1.grid(padx=10, pady=10)
        # Button 2
        self.b2 = Button(self.app, text="Start GPG1", command=lambda: self.which_button("GPG1"))
        self.b2.grid(padx=10, pady=10)

        # Käynnistä Tkinter-looppi
        self.app.mainloop()