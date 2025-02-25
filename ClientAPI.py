import socket
import threading
from time import sleep
from string import ascii_letters

from ClientControl import ClientControl

class ClientAPI():
    def __init__(self, host, port, path, default_direction="north"):
        
        #server stuff
        self.HOST = host
        self.PORT = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))

        self.server_socket.listen(1) #Allow only 1 connection
        self.client_socket, self.client_address = self.server_socket.accept()

        print(f"Connection established with {self.client_address}")

        #GoPiGo control stuff
        self.path = path

        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

        self.cardinal_directions = ["north", "east", "south", "west"]
        self.gopigo_direction = default_direction

        #server stuff
        self.listening = True
        self.listener_thread = threading.Thread(target=self.logic, daemon=True)
        self.listener_thread.start()

    def check_next_node(self):
        print(self.current_node)
        print(self.next_node)

        cardinal_direction = ""

        current_letter = self.current_node[0]
        current_number = self.current_node[1]

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
                command = "turn right"
            if to_where == "south":
                command = "turn twice right"
            if to_where == "west":
                command = "turn left"

        if where_from == "east":
            if to_where == "north":
                command = "turn left"
            if to_where == "south":
                command = "turn right"
            if to_where == "west":
                command = "turn twice right"

        if where_from == "south":
            if to_where == "east":
                command = "turn left"
            if to_where == "west":
                command = "turn right"
            if to_where == "north":
                command = "turn twice right"

        if where_from == "west":
            if to_where == "north":
                command = "turn right"
            if to_where == "east":
                command = "turn twice right"
            if to_where == "south":
                command = "turn left"

        #Update where gopigo is facing.
        self.gopigo_direction = to_where

        print(command)
        #TODO: Send a command to client to turn in the desired direction
        #TODO: Receive a confirmation that the client has executed the turning command
    

    def drive_forward(self):
        #TODO: Send a command for client to drice forward.
        #TODO: Receive a confirmation from client that it has started driving forward.
        pass

    def update_location(self):
        self.current_node_marker = self.current_node_marker + 1
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]

        if self.next_node_marker <= len(self.path) - 1:
            self.next_node = self.path[self.next_node_marker]

    def logic(self):
        while self.listening:
            self.logic_loop()
            self.drive_back()

    def logic_loop(self):
        if self.current_node_marker == 0:
            #TODO: Send a check to GoPiGo to make sure it's ready
            #TODO: Receive a ready confirmation
            print("At first node. GoPiGo started")
        
        for node in self.path:

            if node == self.path[-1]:
                print("Goal reached.")
                break

            cardinal_direction = self.check_next_node() #Where the enxt node is: north (1), east (2), south (3), west (4)

            self.update_location()

            if self.is_gopigo_facing_next_node(cardinal_direction=cardinal_direction):
                print("GoPiGo is facing the next node.")
                self.drive_forward()
            else:
                self.turn_gopigo(where_from=self.gopigo_direction, to_where=cardinal_direction)
                self.drive_forward()

    def reverse_path(self):
        self.path = list(reversed(self.path))

    def reset_node_markers(self):
        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

    def drive_back(self):
        self.reverse_path()
        self.reset_node_markers()
        self.logic_loop()

    def receive_message_from_client(self):
        try:
            if self.listening:
                message = self.client_socket.recv(1024).decode()
                print(f"Client: {message}")

                if not message: #Stop if client disconnects, make better: client_disconnected() listening = False
                    return "error"
                else:
                    return message

        except Exception as e:
            print(f"Error: {e}")
            return "error"

    def send_command(self, command):
        """Sends a command to the client."""
        try:
            self.client_socket.sendall(command.encode())
        except Exception as e:
            print(f"Error sending command: {e}")

    def stop_listening(self):
        self.listening = False

    def close_connection(self):
        self.stop_listening()
        self.client_socket.close()
        self.server_socket.close()
        print("Server closed.")