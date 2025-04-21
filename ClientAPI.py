import socket
from string import ascii_letters
import json
import re
import threading

from PathFinding import PathFinding

class ClientAPI():
    def __init__(self, host, port, path, location_queue, rerouting_check, stop_pause_event, default_direction="east", bot_id="gopigo_1"):     
        #Client control stuff
        self.rerouting_check: dict[str,dict[str,threading.Event]] = rerouting_check
        self.client_stop_pause_event: dict[str,dict[str,threading.Event]] = stop_pause_event

        self.location_queue = location_queue

        self.ID = bot_id

        self.path = path
        self.home_node = path[0]

        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = {
            "id": self.ID,
            "node": self.path[self.current_node_marker]
        }
        self.next_node = self.path[self.next_node_marker]

        self.cardinal_directions = ["north", "east", "south", "west"]
        self.gopigo_direction = default_direction

        self.bot_id = bot_id

        self.state: str|None = None
        self.new_route_for_returning_due_to_reroute: bool = False

        #server stuff
        self.HOST = host
        self.PORT = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.client_socket, self.client_address = None, None
        print("__init__() done.")

    async def open_connection(self):
        self.server_socket.listen(1) #Allow only 1 connection
        print(f"[{self.bot_id}]Listening for a connection.")
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"[{self.bot_id}]Connection established with {self.client_address}")
        
        self.listening = True
        print("Connection opened.")
        
        self.logic()

    def confirm(self, expected, confirmation) -> bool:
        confirmation = re.sub(pattern='"', repl='', string=confirmation)
        return expected == confirmation

    def check_next_node(self):
        print(self.current_node)
        print(self.next_node)

        cardinal_direction = ""

        current_letter = self.current_node["node"][0]
        current_number = self.current_node["node"][1]

        next_letter = self.next_node[0]
        next_number = self.next_node[1]

        #west or east
        if current_number != next_number:
            if current_number < next_number:
                cardinal_direction = "east"
            else:
                cardinal_direction = "west"
        else:
            if ascii_letters.index(current_letter) < ascii_letters.index(next_letter):
                cardinal_direction = "south"
            else:
                cardinal_direction = "north"

        return cardinal_direction

    def is_gopigo_facing_next_node(self, cardinal_direction):
        return self.gopigo_direction == cardinal_direction

    def turn_gopigo(self, where_from, to_where):

        if where_from == "north":
            if to_where == "east":
                command = "TURN_RIGHT"
            if to_where == "south":
                command = "TURN_TWICE_RIGHT"
            if to_where == "west":
                command = "TURN_LEFT"

        if where_from == "east":
            if to_where == "north":
                command = "TURN_LEFT"
            if to_where == "south":
                command = "TURN_RIGHT"
            if to_where == "west":
                command = "TURN_TWICE_RIGHT"

        if where_from == "south":
            if to_where == "east":
                command = "TURN_LEFT"
            if to_where == "west":
                command = "TURN_RIGHT"
            if to_where == "north":
                command = "TURN_TWICE_RIGHT"

        if where_from == "west":
            if to_where == "north":
                command = "TURN_RIGHT"
            if to_where == "east":
                command = "TURN_TWICE_RIGHT"
            if to_where == "south":
                command = "TURN_LEFT"

        self.gopigo_direction = to_where #Update where gopigo is facing.
        
        self.send_command(command=command) #Send a command to client to turn in the desired direction
        
        confirmation = self.receive_message_from_client()

        if self.confirm(expected="TURN_OK", confirmation=confirmation) : #Receive a confirmation that the client has executed the turning command
            pass
        else:
            print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")

    def drive_forward(self):
        self.send_command(command="DRIVE_FORWARD") #Send a command for client to drice forward.
        
        confirmation = self.receive_message_from_client()

        if self.confirm(expected="DRIVE_OK", confirmation=confirmation): #Receive a confirmation from client that it has started driving forward.
            pass
        else:
            print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")

    def update_location(self):
        self.current_node_marker = self.current_node_marker + 1
        self.next_node_marker = self.current_node_marker + 1

        self.current_node["node"] = self.path[self.current_node_marker]

        if self.next_node_marker <= len(self.path) - 1:
            self.next_node = self.path[self.next_node_marker]

    def send_location_to_map(self):
        #print("current Location:", self.current_node)
        print("Sending location to map: ", self.current_node)
        self.location_queue.put(self.current_node, block=True) #Laittaa dictionaryn

    def logic(self):
        self.state = "STARTED"
        
        while self.listening:

            if self.state == "REROUTED_FROM_CURRENT_TO_DESTINATION":
                self.reroute_from_current_to_end()
                self.new_route_for_returning_due_to_reroute = True
                self.state = "STARTED"
            
            if self.state == "STARTED":
                self.logic_loop()
            
            if self.state == "DRIVE_BACK":
                self.drive_back()
            
            if self.state == "RETURNED_HOME":
                self.send_command(command="TURN_TWICE_RIGHT") #Turn GoPiGo back to its default direction
                confirmation = self.receive_message_from_client()
                self.confirm(expected="TURN_OK", confirmation=confirmation)

                self.close_connection()

    def logic_loop(self):
        if self.current_node_marker == 0:
            self.send_command(command="ARE_YOU_READY") #Send a check to client to make sure it's ready
            print("In logic_loop, after sending the command")

            confirmation = self.receive_message_from_client()

            ###

            if self.confirm(expected="I_AM_READY", confirmation=confirmation): #Receive a ready confirmation from client
                print("In logic_loop, response has been received")
                pass
            else:
                print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")

            print("At first node. GoPiGo started")
        
        for node in self.path:
            self.send_location_to_map() #laitetaan dictionary, jossa on bot_id ja current_node mapiin

            if node == self.path[-1]:
                break #Goal reached

            cardinal_direction = self.check_next_node() #Where the next node is: north (1), east (2), south (3), west (4)

            if self.is_gopigo_facing_next_node(cardinal_direction=cardinal_direction):
                self.drive_forward()
            else:
                self.turn_gopigo(where_from=self.gopigo_direction, to_where=cardinal_direction)
                self.drive_forward()
            
            self.update_location() #Markereita yks pykälä eteen päin

            if self.rerouting_check[self.ID]["event"].is_set():
                self.rerouting_check[self.ID]["event"].clear()

                break_from_logic_loop = False
                
                for i in range(len(self.path) - 1):
                    edge = (self.path[i], self.path[i + 1])
                    reversed_edge = (self.path[i + 1], self.path[i])

                    if edge in PathFinding.removed_edges or reversed_edge in PathFinding.removed_edges:
                        break_from_logic_loop = True

                        self.state = "REROUTED_FROM_CURRENT_TO_DESTINATION"
                        break
                if break_from_logic_loop == True:
                    break

            self.client_stop_pause_event[self.ID]["event"].wait() #if is set, this doesn't wait

        if self.state == "STARTED":
            self.state = "DRIVE_BACK"
        elif self.state == "DRIVE_BACK":
            self.state = "RETURNED_HOME"

    def reroute_from_current_to_end(self):
        self.path = PathFinding().get_shortest_path(start=self.current_node["node"], end=self.path[-1])
        self.reset_node_markers()

    def reverse_path(self):
        self.path = list(reversed(self.path))

    def reroute_back_home(self):
        self.path = PathFinding().get_shortest_path(start=self.current_node["node"], end=self.home_node)

    def reset_node_markers(self):
        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node["node"] = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

    def drive_back(self):
        if self.new_route_for_returning_due_to_reroute == True:
            self.reroute_back_home()
        else:
            self.reverse_path()
        
        self.new_route_for_returning_due_to_reroute = False
        self.state = "DRIVE_BACK"

        self.reset_node_markers()
        self.logic_loop()

    def receive_message_from_client(self):
        print("In receive_message_from_client, before try")
        try:
            if self.listening:
                message = self.client_socket.recv(1024).decode()
                print("In receive_message_from_client, after receiving message from client")
                print(f"Client: {message}")

                if not message: #Stop if client disconnects, make better: client_disconnected() listening = False
                    return "error"
                else:
                    return message

        except Exception as e:
            print(f"Error: {e}")
            return "error"

    def send_command(self, command: str):
        command_type = None

        print("In send_command, the command: ", command)

        if command == "TURN_RIGHT" or command == "TURN_TWICE_RIGHT" or command == "TURN_LEFT" or command == "DRIVE_FORWARD":
            command_type = "COMMAND"
        elif command == "ARE_YOU_READY":
            command_type = "CHECK"

        command_json = json.dumps(
            {
                "type": command_type,
                "command": command
            }
        )

        try:
            print("In try")
            self.client_socket.sendall(command_json.encode())
        except Exception as e:
            print(f"Error sending command: {e}") #Maybe some error handling here

    def stop_listening(self):
        self.listening = False

    def close_connection(self):
        self.send_command(command="SHUTDOWN")
        #Return to start location, if not in start location?
        self.stop_listening()
        self.client_socket.close()
        self.server_socket.close()
        print("Server closed.")