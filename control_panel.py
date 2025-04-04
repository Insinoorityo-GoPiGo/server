from tkinter import *
import threading
from tkinter.ttk import Combobox
import asyncio
import queue
import os
from dotenv import load_dotenv

from map import Map
from PathFinding import PathFinding
from ClientAPI import ClientAPI

load_dotenv()

map_logic_execution_pause = threading.Event()
map_has_been_paused = threading.Condition()

class Control_Panel:
    def __init__(self, command_queue, quit_flag, coordinates, edges):
        self.coordinates = coordinates
        self.edges = edges

        self.command_queue = command_queue
        self.quit_flag = quit_flag

        self.location_queue_1 = queue.Queue()
        self.location_queue_2 = queue.Queue()
        
        self.valid_inputs = [
            "A0", "A1", "A2", "A3", "A4",
            "A5", "A6", "A7", "A8", "A9",
            "B1", "B3", "B7", "B9",
            "C1", "C2", "C3", "C4",
            "C5", "C6", "C7", "C9",
            "D1", "D3", "D7", "D9",
            "E1", "E3", "E4", "E5",
            "E6", "E7", "E8", "E9",
            "F1", "F3", "F7", "F9",
            "G1", "G2", "G3", "G4",
            "G5", "G6", "G7", "G8", "G9", "G10"
        ]

        self.path: None|list = None
        self.location_map: None|Map = None

        self.chosen_client_id = None
    
        self.app = Tk()
        self.app.title("Control Panel")
        self.app.geometry("600x500")

        self.b1 = Button(self.app, text="Start GPG1", command=lambda: self.handle_button_press("GPG1"))
        self.b1.grid(row=3, column=0, padx=10, pady=10)

        self.b2 = Button(self.app, text="Start GPG2", command=lambda: self.handle_button_press("GPG2"))
        self.b2.grid(row=62, column=0, padx=10, pady=10)
        
        
        self.button_open_map = Button(self.app, text="Open map", command=lambda: self.handle_button_press("open_map"))
        self.button_open_map.grid(row=0, column=1, padx=10, pady=10)
        map_label = Label(self.app, text='Käynnistä Kartta', font=('Arial', 10))
        map_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.start_node_var_1 = StringVar(value="A0")
        self.end_node_var_1 = StringVar()
        self.end_node_var_1.trace_add("write", self.force_uppercase)
        
        self.start_node_var_2 = StringVar(value="G3")
        self.end_node_var_2 = StringVar()
        self.end_node_var_2.trace_add("write", self.force_uppercase)
        
        self.remove_edge_1 = StringVar()
        self.remove_edge_1.trace_add("write", self.force_uppercase)
        self.remove_edge_2 = StringVar()
        self.remove_edge_2.trace_add("write", self.force_uppercase)
        
        self.create_node_fields_gpg1()
        self.create_node_fields_gpg2()
        self.create_edge_remover_handler()
        
        self.app.bind("<Escape>", self.close_app)
        
    def force_uppercase(self, *args):
        self.end_node_var_1.set(self.end_node_var_1.get().upper())
        self.end_node_var_2.set(self.end_node_var_2.get().upper())
        self.remove_edge_1.set(self.remove_edge_1.get().upper())
        self.remove_edge_2.set(self.remove_edge_2.get().upper())

    def close_app(self, event):
        self.app.destroy() #Close the control panel window
     
    def create_node_fields_gpg1(self):
        GPG1_label = Label(self.app, text="GoPiGo 1 Ohjaus", font=('Arial', 10, 'bold'))
        GPG1_label.grid(row=2, column=0, padx=10, pady=5)
        
        aloitus_label_1 = Label(self.app, text='Aloitus 1', font=('Arial', 10))
        aloitus_label_1.grid(row=3, column=1, padx=10, pady=5)
        
        aloitus_syöttö_1 = Entry(self.app, textvariable=self.start_node_var_1, font=('Arial', 10), width=5, state="readonly")
        aloitus_syöttö_1.grid(row=3, column=2, padx=10, pady=5)

        lopetus_label_1 = Label(self.app, text='Lopetus 1', font=('Arial', 10))
        lopetus_label_1.grid(row=4, column=1, padx=10, pady=5)
        
        lopetus_syöttö_1 = Combobox(self.app, textvariable=self.end_node_var_1, values=self.valid_inputs, width=5)
        lopetus_syöttö_1.grid(row=4, column=2, padx=10, pady=5)

        sub_btn_1 = Button(self.app, text='Hae Reitti', command=self.submit_gpg1)
        sub_btn_1.grid(row=4, column=3, pady=7)
  
        self.separator = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator.grid(row=1, column=0, columnspan=14, padx=10, pady=10, sticky="ew") 
        self.separator1 = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator1.grid(row=5, column=0, columnspan=14, padx=10, pady=10, sticky="ew")  
        
    def create_node_fields_gpg2(self):
        GPG2_label = Label(self.app, text="GoPiGo 2 Ohjaus", font=('Arial', 10, 'bold'))
        GPG2_label.grid(row=61, column=0, padx=10, pady=5)
        
        aloitus_label_2 = Label(self.app, text='Aloitus 2', font=('Arial', 10))
        aloitus_label_2.grid(row=62, column=1, padx=10, pady=5)
        
        aloitus_syöttö_2 = Entry(self.app, textvariable=self.start_node_var_2, font=('Arial', 10), width=5, state="readonly")
        aloitus_syöttö_2.grid(row=62, column=2, padx=10, pady=5)

        lopetus_label_2 = Label(self.app, text='Lopetus 2', font=('Arial', 10))
        lopetus_label_2.grid(row=63, column=1, padx=10, pady=5)
        
        lopetus_syöttö_2 = Combobox(self.app, textvariable=self.end_node_var_2, values=self.valid_inputs, width=5)
        lopetus_syöttö_2.grid(row=63, column=2, padx=10, pady=5)

        sub_btn_2 = Button(self.app, text='Hae Reitti', command=self.submit_gpg2)
        sub_btn_2.grid(row=63, column=3, pady=7)
        
        self.separator = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator.grid(row=64, column=0, columnspan=14, padx=10, pady=10, sticky="ew")
  
    def create_edge_remover_handler(self): 
        node_in_edge_1 = Label(self.app, text='Node 1', font=('Arial', 10))
        node_in_edge_1.grid(row=65, column=0, padx=10, pady=5) 
        node_in_edge_1 = Combobox(self.app, textvariable=self.remove_edge_1, values=self.valid_inputs, width=5)
        node_in_edge_1.grid(row=65, column=1, padx=10, pady=5)
        
        node_in_edge_2 = Label(self.app, text='Node 2', font=('Arial', 10))
        node_in_edge_2.grid(row=66, column=0, padx=10, pady=5) 
        node_in_edge_2 = Combobox(self.app, textvariable=self.remove_edge_2, values=self.valid_inputs, width=5)
        node_in_edge_2.grid(row=66, column=1, padx=10, pady=5)
           
        sub_btn_3 = Button(self.app, text='Poista Edge', command=self.submit_remove_edge)
        sub_btn_3.grid(row=66, column=2, pady=7)
        
        sub_btn_4 = Button(self.app, text='Palauta edge', command=self.restore_edges)
        sub_btn_4.grid(row=66, column=3, pady=7)
        
    def submit_remove_edge(self):
        Node1 = self.remove_edge_1.get()
        Node2 = self.remove_edge_2.get()
        print("In submit_remove_edge, node1: ",Node1," node2: ",Node2)
        self.remove_edge(target_edge=(Node1,Node2))
       
    def submit_gpg1(self):
        Aloitus1 = self.start_node_var_1.get()
        Lopetus1 = self.end_node_var_1.get()

        print(f"Aloitus Node GPG1: {Aloitus1}")
        print(f"Lopetus Node GPG1: {Lopetus1}")
        
        self.path = PathFinding(coordinates=self.coordinates).get_shortest_path(start=Aloitus1, end=Lopetus1)
        print("path: ",self.path)

        self.end_node_var_1.set("")
        
    def submit_gpg2(self):
        Aloitus2 = self.start_node_var_2.get()
        Lopetus2 = self.end_node_var_2.get()

        print(f"Aloitus Node GPG2: {Aloitus2}")
        print(f"Lopetus Node GPG2: {Lopetus2}")

        self.path = PathFinding(coordinates=self.coordinates, edges=self.edges).get_shortest_path(start=Aloitus2, end=Lopetus2)
        
        self.end_node_var_2.set("")

    def open_control_panel(self):
        self.app.mainloop()

    def open_map(self):
        print("Open map button pressed.")
        self.location_map = Map(location_queue_1 = self.location_queue_1, location_queue_2 = self.location_queue_2, quit_flag=self.quit_flag, coordinates=self.coordinates, edges=self.edges, map_logic_execution_pause=map_logic_execution_pause, map_has_been_paused=map_has_been_paused)
        self.location_map.run()

    def open_and_run_socket(self, port, the_id):
        location_queue = self.location_queue_1 if the_id == "gopigo_1" else self.location_queue_2
        
        client_api = ClientAPI(host=os.getenv("IP_ADDRESS"), port=port, path=self.path, quit_flag=self.quit_flag, command_queue=self.command_queue, location_queue=location_queue, default_direction="east", bot_id=the_id)
        run_server = lambda client_api: asyncio.run(client_api.open_connection())
        (threading.Thread(target=run_server, args=(client_api,), daemon=True)).start()

    def remove_edge(self, target_edge: tuple):
        #Pysäytetään socketin toiminta

        #Poistetaan edge
        node_1, node_2 = target_edge
        for edge in self.location_map.edges:
            if edge == (node_1, node_2) or edge == (node_2, node_1):
                PathFinding.removed_edges.append(edge)
                
                node_1, node_2 = edge
                weight = 2

                PathFinding.EDGES.remove((node_1, node_2, weight))

                self.location_map.highlight_edge = edge

                break

        #Jatketaan socketin toimintaa
        
    def restore_edges(self):
    
        while PathFinding.removed_edges:
            edge = PathFinding.removed_edges.pop()
            node_1, node_2 = edge
            weight = 2  

            self.location_map.edges.append(edge)  
            PathFinding.EDGES.append((node_1, node_2, weight))  
            self.location_map.highlight_edge = None  
            print(f"Node {node_1} and node {node_2} edge is restored")
            

    def handle_button_press(self, command):
        print(f"Button clicked: {command}")
       
        if command is None or command == "":
            print("No command received")
            pass
        elif command == "open_map":
            print("open_map command received.")
            self.open_map()
        elif command == "GPG1": 
            if self.path is None:
                print(f"Some Nodes are Missing from: {command}")
                return  
            else: 
                self.open_and_run_socket(port=1025, the_id="gopigo_1") 
                self.b1.config(bg="green")
                    
        elif command == "GPG2":
            if self.path is None:
                print(f"Some Nodes are Missing from: {command}")
                return
            else: 
                self.open_and_run_socket(port=1026, the_id="gopigo_2")
                self.b2.config(bg="green")        
        
        else:
            self.command_queue.put(
                {
                    "id": self.chosen_client_id,
                    "command": command
                }
            )