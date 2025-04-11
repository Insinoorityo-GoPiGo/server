from tkinter import *
import threading
from tkinter.ttk import Combobox
import asyncio
import queue
import paramiko
import os
from dotenv import load_dotenv

from map import Map
from PathFinding import PathFinding
from ClientAPI import ClientAPI
from get_coordinates_and_edges import get_coordinates_and_edges

load_dotenv()

class Control_Panel:
    def __init__(self):
        
        self.rerouting_check = {
            "gopigo_1": {
                "event": threading.Event()
            },
            "gopigo_2": {
                "event": threading.Event()
            },
        }

        self.socket_logic_execution_pause = {
            "gopigo_1": {
                "event": threading.Event()
            },
            "gopigo_2": {
                "event": threading.Event()
            },
        }

        self.map_quit_flag = threading.Event() #When control panel is closed, map also closes.

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
        
        self.options_gpg = ["GoPiGo 1", "GoPiGo 2", "Both"]

        self.path: None|list = None
        self.location_map: None|Map = None

        self.highlighted_edge_for_map = None

        self.chosen_client_id = None

        self.gpg_1_start_node: str|None = None #For start node that's displayed on map
        self.gpg_2_start_node: str|None = None
    
        self.app = Tk()
        self.app.title("Control Panel")
        self.app.geometry("800x600")

        self.b1 = Button(self.app, text="Start GPG1",command=self.start_gpg1_and_ssh,)
        self.b1.grid(row=3, column=0, padx=10, pady=10)

        self.b2 = Button(self.app, text="Start GPG2", command=self.start_gpg2_and_ssh)
        self.b2.grid(row=62, column=0, padx=10, pady=10)
        
        
        self.button_open_map = Button(self.app, text="Open map", command=lambda: self.handle_button_press("open_map"))
        self.button_open_map.grid(row=0, column=1, padx=10, pady=10)
        map_label = Label(self.app, text='Start Map', font=('Arial', 10))
        map_label.grid(row=0, column=0, padx=10, pady=5)

        self.gpg_pause_selection = StringVar()
        self.gpg_continue_selection = StringVar()
        
        self.start_node_var_1 = StringVar()
        self.start_node_var_1.trace_add("write", self.force_uppercase)
        self.end_node_var_1 = StringVar()
        self.end_node_var_1.trace_add("write", self.force_uppercase)
        
        self.start_node_var_2 = StringVar()
        self.start_node_var_2.trace_add("write", self.force_uppercase)
        self.end_node_var_2 = StringVar()
        self.end_node_var_2.trace_add("write", self.force_uppercase)
        
        self.remove_edge_1 = StringVar()
        self.remove_edge_1.trace_add("write", self.force_uppercase)
        self.remove_edge_2 = StringVar()
        self.remove_edge_2.trace_add("write", self.force_uppercase)
        
        self.create_node_fields_gpg1()
        self.create_node_fields_gpg2()
        self.create_edge_remover_handler()
        self.gopigo_state_handelr()
        self.image_analysis_field()
        
        self.app.bind("<Escape>", self.close_app)

    def ssh_start_script_on_gopigo(self, bot_ip, username, password, remote_path):
        try:
            print(f"[SSH] Connecting to {bot_ip}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=bot_ip,
                username=username,
                password=password
            )

            command = f"python3 {remote_path}"
            print(f"[SSH] Running command: {command}")
            stdin, stdout, stderr = ssh.exec_command(command)

            # Optional: Print output
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                print(f"[SSH] Output:\n{output}")
            if error:
                print(f"[SSH] Error:\n{error}")

            ssh.close()
            print("[SSH] Connection closed.")

        except Exception as e:
            print(f"[SSH] Failed to connect or run command: {e}")

    def start_gpg1_and_ssh(self):
        threading.Thread(
            target=self.ssh_start_script_on_gopigo,
            args=(
                os.getenv("GPG1_IP"),
                os.getenv("GPG1_USER"),
                os.getenv("GPG1_PASS"),
                "/home/pi/GoPiGo/22222/main.py"
            ),
            daemon=True
        ).start()

        self.handle_button_press("GPG1")

    def start_gpg2_and_ssh(self):
        threading.Thread(
            target=self.ssh_start_script_on_gopigo,
            args=(
                os.getenv("GPG2_IP"),
                os.getenv("GPG2_USER"),
                os.getenv("GPG2_PASS"),
                "/home/pi/GoPiGo/22222/main.py"
            ),
            daemon=True
        ).start()

        self.handle_button_press("GPG2")

    def force_uppercase(self, *args):
        self.start_node_var_1.set(self.start_node_var_1.get().upper())
        self.end_node_var_1.set(self.end_node_var_1.get().upper())
        self.start_node_var_2.set(self.start_node_var_2.get().upper())
        self.end_node_var_2.set(self.end_node_var_2.get().upper())
        self.remove_edge_1.set(self.remove_edge_1.get().upper())
        self.remove_edge_2.set(self.remove_edge_2.get().upper())

    def close_app(self, event):
        if self.location_map is not None:
            self.map_quit_flag.set()

        self.app.destroy() #Close the control panel window
     
    def create_node_fields_gpg1(self):
        GPG1_label = Label(self.app, text="GoPiGo 1 Control", font=('Arial', 10, 'bold'))
        GPG1_label.grid(row=2, column=0, padx=10, pady=5)
        
        aloitus_label_1 = Label(self.app, text='Start 1', font=('Arial', 10))
        aloitus_label_1.grid(row=3, column=1, padx=10, pady=5)
        
        aloitus_syöttö_1 = Combobox(self.app, textvariable=self.start_node_var_1, values=self.valid_inputs, width=5)
        aloitus_syöttö_1.grid(row=3, column=2, padx=10, pady=5)

        lopetus_label_1 = Label(self.app, text='End 1', font=('Arial', 10))
        lopetus_label_1.grid(row=4, column=1, padx=10, pady=5)
        
        lopetus_syöttö_1 = Combobox(self.app, textvariable=self.end_node_var_1, values=self.valid_inputs, width=5)
        lopetus_syöttö_1.grid(row=4, column=2, padx=10, pady=5)

        sub_btn_1 = Button(self.app, text='Get Path', command=self.submit_gpg1)
        sub_btn_1.grid(row=4, column=3, pady=7)
  
        self.separator = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator.grid(row=1, column=0, columnspan=14, padx=10, pady=10, sticky="ew") 
        self.separator1 = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator1.grid(row=5, column=0, columnspan=14, padx=10, pady=10, sticky="ew")
        
    def create_node_fields_gpg2(self):
        GPG2_label = Label(self.app, text="GoPiGo 2 Control", font=('Arial', 10, 'bold'))
        GPG2_label.grid(row=61, column=0, padx=10, pady=5)
        
        aloitus_label_2 = Label(self.app, text='Start 2', font=('Arial', 10))
        aloitus_label_2.grid(row=62, column=1, padx=10, pady=5)
        
        aloitus_syöttö_2 = Combobox(self.app, textvariable=self.start_node_var_2, values=self.valid_inputs, width=5)
        aloitus_syöttö_2.grid(row=62, column=2, padx=10, pady=5)

        lopetus_label_2 = Label(self.app, text='End 2', font=('Arial', 10))
        lopetus_label_2.grid(row=63, column=1, padx=10, pady=5)
        
        lopetus_syöttö_2 = Combobox(self.app, textvariable=self.end_node_var_2, values=self.valid_inputs, width=5)
        lopetus_syöttö_2.grid(row=63, column=2, padx=10, pady=5)

        sub_btn_2 = Button(self.app, text='Get Path', command=self.submit_gpg2)
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

        
        self.sub_btn_3 = Button(self.app, text='Remove Edge', command=self.submit_remove_edge, state="disabled")
        self.sub_btn_3.grid(row=66, column=2, pady=7)
        
        self.sub_btn_4 = Button(self.app, text='Restore edge', command=self.restore_edges, state="disable")
        self.sub_btn_4.grid(row=66, column=3, pady=7)
        
    def submit_remove_edge(self):
        Node1 = self.remove_edge_1.get()
        Node2 = self.remove_edge_2.get()
        self.remove_edge(target_edge=(Node1,Node2))
        
    def gopigo_state_handelr(self):
        self.separator = Frame(self.app, height=2, bd=1, relief=SUNKEN, bg="black")
        self.separator.grid(row=68, column=0, columnspan=14, padx=10, pady=10, sticky="ew")
        
        Pause_GPG = Label(self.app, text='Pause selected GPG', font=('Arial', 10))
        Pause_GPG.grid(row=69, column=0, padx=10, pady=5) 
        Pause_GPG = Combobox(self.app, values=self.options_gpg, width=5, textvariable=self.gpg_pause_selection, state="readonly")
        Pause_GPG.grid(row=69, column=1, padx=10, pady=5)
        self.sub_btn_5 = Button(self.app, text='Pause', command=self.pause_gpg)
        self.sub_btn_5.grid(row=69, column=2, pady=7)
        
        
        Continue_GPG = Label(self.app, text='Continue GPG', font=('Arial', 10))
        Continue_GPG.grid(row=70, column=0, padx=10, pady=5) 
        Continue_GPG = Combobox(self.app, values=self.options_gpg, width=5, textvariable=self.gpg_continue_selection, state="readonly")
        Continue_GPG.grid(row=70, column=1, padx=10, pady=5)
        self.sub_btn_6 = Button(self.app, text='Continue', command=self.continue_gpg )
        self.sub_btn_6.grid(row=70, column=2, pady=7)
        
    def image_analysis_field(self):
        GPG_detection_analysis = Label(self.app, text='AI analysis from picture taken by GoPiGo', font=('Arial', 10))
        GPG_detection_analysis.grid(row=0, column=3, padx=10, pady=5)
        GPG_detection_analysis = Text(self.app, height=3, width=20, font=('Arial', 10), state="disabled")
        GPG_detection_analysis.grid(row=0, column=4, padx=10, pady=5)
    
     
    def pause_gpg(self):
        match self.gpg_pause_selection:
            case "GoPiGo 1":
                self.socket_logic_execution_pause["gopigo_1"]["event"].clear()
            case "GoPiGo 2":
                self.socket_logic_execution_pause["gopigo_2"]["event"].clear()
            case "Both":
                self.socket_logic_execution_pause["gopigo_1"]["event"].clear()
                self.socket_logic_execution_pause["gopigo_2"]["event"].clear()
            case "":
                print("In pause_gpg, no command was given.")
        
    def continue_gpg(self):
        match self.gpg_continue_selection:
            case "GoPiGo 1":
                self.socket_logic_execution_pause["gopigo_1"]["event"].set()
            case "GoPiGo 2":
                self.socket_logic_execution_pause["gopigo_2"]["event"].set()
            case "Both":
                self.socket_logic_execution_pause["gopigo_1"]["event"].set()
                self.socket_logic_execution_pause["gopigo_2"]["event"].set()
            case "":
                print("In continue_gpg, no command was given.")
       
    def submit_gpg1(self):
        Aloitus1 = self.start_node_var_1.get()
        Lopetus1 = self.end_node_var_1.get()

        self.gpg_1_start_node = Aloitus1 #For highlighted node in map

        if self.location_map is not None:
            self.location_map.highlight_node_gpg_1 = self.gpg_1_start_node

        print(f"Start Node GPG1: {Aloitus1}")
        print(f"End Node GPG1: {Lopetus1}")
        
        self.path = PathFinding().get_shortest_path(start=Aloitus1, end=Lopetus1)

        self.end_node_var_1.set("")
        
    def submit_gpg2(self):
        Aloitus2 = self.start_node_var_2.get()
        Lopetus2 = self.end_node_var_2.get()

        self.gpg_2_start_node = Aloitus2

        if self.location_map is not None:
            self.location_map.highlight_node_gpg_2 = self.gpg_2_start_node

        print(f"Start Node GPG2: {Aloitus2}")
        print(f"Node Node GPG2: {Lopetus2}")

        self.path = PathFinding().get_shortest_path(start=Aloitus2, end=Lopetus2)
        
        self.end_node_var_2.set("")

    def open_control_panel(self):
        self.app.mainloop()

    def open_map(self):
        self.sub_btn_3.config(state="normal")
        self.sub_btn_4.config(state="normal")
        self.location_map = Map(location_queue_1=self.location_queue_1, location_queue_2=self.location_queue_2, quit_flag=self.map_quit_flag, highlighted_edge=self.highlighted_edge_for_map, highlighted_start_node_gpg_1=self.gpg_1_start_node, highlighted_start_node_gpg_2=self.gpg_2_start_node)
        self.location_map.run()

    def open_and_run_socket(self, port, the_id):
        location_queue = self.location_queue_1 if the_id == "gopigo_1" else self.location_queue_2
        
        client_api = ClientAPI(host=os.getenv("IP_ADDRESS"), port=port, path=self.path, location_queue=location_queue, default_direction="east", bot_id=the_id, rerouting_check=self.rerouting_check, stop_pause_event=self.socket_logic_execution_pause)
        run_server = lambda client_api: asyncio.run(client_api.open_connection())
        (threading.Thread(target=run_server, args=(client_api,), daemon=True)).start()

    def remove_edge(self, target_edge: tuple):
        #Pysäytetään socketin toiminta
        
        #for socket in self.rerouting_check:
        #    socket["event"].set()

        #Poistetaan edge
        node_1, node_2 = target_edge

        _, edges = get_coordinates_and_edges()
        edges = [(coord_1, coord_2) for coord_1, coord_2, weight in edges]

        for edge in edges:
            if edge == (node_1, node_2) or edge == (node_2, node_1):

                #Remove the edge for rerouting in the sockets
                PathFinding.removed_edges.append(edge)
                
                node_1, node_2 = edge
                weight = 2

                PathFinding.EDGES.remove((node_1, node_2, weight))

                #Highlight the removed edge on the map
                if self.location_map == None:
                    self.highlighted_edge_for_map = edge
                else:
                    self.location_map.highlight_edge = edge

                break
        
    def restore_edges(self):
        while PathFinding.removed_edges:
            edge = PathFinding.removed_edges.pop()
            node_1, node_2 = edge
            weight = 2  

            self.location_map.edges.append(edge)  
            PathFinding.EDGES.append((node_1, node_2, weight))  
            self.location_map.highlight_edge = None  

    def handle_button_press(self, command):
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
            print("In handle_button_press, no command was given.")