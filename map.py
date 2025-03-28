import networkx as nx
import matplotlib.pyplot as plt
import time
from queue import Empty
import threading

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Map:
    def __init__(self, queue, quit_flag, master):
        self.queue = queue
        self.quit_flag = quit_flag
        
        #self.window = tk.Toplevel(master=master)
        #self.window.title("map")
        #self.window.geometry("600x500")

        # Määritellään graafi
        self.G = nx.Graph()
        self.points = {
            "A0": (-1, 6), "L2": (0, -1), "L3": (9, 0),
            "A1": (0, 6), "A2": (1, 6), "A3": (2, 6), "A4": (3, 6),
            "A5": (4, 6), "A6": (5, 6), "A7": (6, 6), "A8": (7, 6), "A9": (8, 6),
            "B1": (0, 5), "B3": (2, 5), "B7": (6, 5), "B9": (8, 5),
            "C1": (0, 4), "C2": (1, 4), "C3": (2, 4), "C4": (3, 4),
            "C5": (4, 4), "C6": (5, 4), "C7": (6, 4), "C9": (8, 4),
            "D1": (0, 3), "D3": (2, 3), "D7": (6, 3), "D9": (8, 3),
            "E1": (0, 2), "E3": (2, 2), "E4": (3, 2), "E5": (4, 2),
            "E6": (5, 2), "E7": (6, 2), "E8": (7, 2), "E9": (8, 2),
            "F1": (0, 1), "F3": (2, 1), "F7": (6, 1), "F9": (8, 1),
            "G1": (0, 0), "G2": (1, 0), "G3": (2, 0), "G4": (3, 0),
            "G5": (4, 0), "G6": (5, 0), "G7": (6, 0), "G8": (7, 0), "G9": (8, 0)
        }
        self.edges = [
            ("A0", "A1"), ("L2", "G1"), ("L3", "G9"),
            ("A1", "A2"), ("A1", "B1"), ("A2", "A3"), ("A3", "A4"),
            ("A3", "B3"), ("A4", "A5"), ("A5", "A6"), ("A6", "A7"),
            ("A7", "B7"), ("A7", "A8"), ("A8", "A9"), ("A9", "B9"),
            ("B9", "C9"), ("C9", "D9"), ("D9", "E9"), ("E9", "E8"),
            ("E9", "F9"), ("F9", "G9"), ("G9", "G8"), ("G8", "G7"),
            ("G7", "G6"), ("G7", "F7"), ("F7", "E7"), ("E7", "E8"),
            ("E7", "E6"), ("E7", "D7"), ("D7", "C7"), ("C7", "B7"),
            ("C7", "C6"), ("C6", "C5"), ("C5", "C4"), ("C4", "C3"),
            ("C3", "B3"), ("C3", "C2"), ("C2", "C1"), ("C3", "D3"),
            ("D3", "E3"), ("E3", "E4"), ("E4", "E5"), ("E5", "E6"),
            ("E3", "F3"), ("F3", "G3"), ("G3", "G4"), ("G4", "G5"),
            ("G5", "G6"), ("G3", "G2"), ("G2", "G1"), ("G1", "F1"),
            ("F1", "E1"), ("E1", "D1"), ("D1", "C1"), ("B1", "C1")
        ]
        self.G.add_nodes_from(self.points.keys())
        self.G.add_edges_from(self.edges)

        self.highlight_node_gpg_1 = "A0"
        self.highlight_node_gpg_2 = "G5"
        
        self.fig, self.ax = plt.subplots()
        
        plt.ion()
        self.update_graph()
        print("map init complete")

    def get_location(self) -> dict | None:
        """Hakee sijainnin jonosta, jos se ei ole tyhjä"""
        try:
            location = self.queue.get(block=False)
            print(f" Queue: {location}")
            return location
        except Empty:
            print(" Jono on tyhjä")
            return None

    def update_graph(self):
        self.ax.clear()

        node_colors = [ #highlighted noden värin määrittäminen
            "green" if node == self.highlight_node_gpg_1 else
            "yellow" if node == self.highlight_node_gpg_2
            
            else "red"
            
            for node in self.G.nodes
        ]

        nx.draw(self.G, self.points, node_color=node_colors, node_size=300, edge_color='gray', ax=self.ax)
        nx.draw_networkx_labels(self.G, self.points, font_color="black", font_size=10, ax=self.ax)

        #canvas = FigureCanvasTkAgg(figure=self.fig, master=self.window)
        #canvas.draw()
        #canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True) #Piirtää myös mapiin graafin?

        plt.show(block=False) #Figure 1 avataan
        plt.pause(0.1)

    def set_highlight(self, location: dict):

        if location["node"] in self.G.nodes:
            print(f"Highlight node: {location}")
            
            if location["id"] == "gopigo_1":
                self.highlight_node_gpg_1 = location["node"] #Is the highlighted node
            elif location["id"] == "gopigo_2":
                self.highlight_node_gpg_2 = location["node"]
            
            self.update_graph()
        else:
            print(f" Virhe: Nodea {location} ei löydy.")

    def update_map(self):
        server_input = self.get_location()

        if server_input == None:
            pass

        if server_input:
            self.set_highlight(location=server_input)

        plt.pause(0.1)
        self.fig.canvas.flush_events()

        self.fig.canvas.get_tk_widget().after(500, self.update_map)

    def run(self):
        print("map started")
        try:
            while plt.fignum_exists(self.fig.number):

                #break
                server_input = self.get_location()

                if server_input is None:
                    print("No input from server")
                    time.sleep(0.5)  # Odotetaan, jos jono on tyhjä
                    continue  
                
                if server_input.lower() == "q":
                    print("Quit")
                    plt.close('all')
                    break

                self.set_highlight(server_input)

                if self.quit_flag.is_set():
                    break
        except KeyboardInterrupt:
            plt.close('all')

        plt.ioff()
        plt.show()
        