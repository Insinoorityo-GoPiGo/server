import socket
import threading
from time import sleep
from string import ascii_letters
import json
import asyncio
import re

class ClientAPI():
    def __init__(self, host, port, path, quit_flag, location_queue, default_direction="north"):
        
        #Client control stuff
        self.location_queue = location_queue

        self.path = path

        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

        self.cardinal_directions = ["north", "east", "south", "west"]
        self.gopigo_direction = default_direction

        #server stuff
        self.quit_flag = quit_flag

        self.HOST = host
        self.PORT = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.server_socket.listen(1) #Allow only 1 connection
        print("Listening for a connection.")
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Connection established with {self.client_address}")
        
        self.listening = True
        print("__init__() done.")

    def confirm(self, expected, confirmation) -> bool:
        confirmation = re.sub(pattern='"', repl='', string=confirmation)
        return expected == confirmation

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

    async def turn_gopigo(self, where_from, to_where):

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
        
        confirmation = await self.receive_message_from_client()

        if self.confirm(expected="TURN_OK", confirmation=confirmation) : #Receive a confirmation that the client has executed the turning command
            pass
        else:
            print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")

    async def drive_forward(self):
        self.send_command(command="DRIVE_FORWARD") #Send a command for client to drice forward.
        
        confirmation = await self.receive_message_from_client()

        if self.confirm(expected="DRIVE_OK", confirmation=confirmation): #Receive a confirmation from client that it has started driving forward.
            pass
        else:
            print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")

    def update_location(self):
        self.current_node_marker = self.current_node_marker + 1
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]

        if self.next_node_marker <= len(self.path) - 1:
            self.next_node = self.path[self.next_node_marker]

    def send_location_to_map(self):
        self.location_queue.put(self.current_node, block=True) #Vaikka tässä?

    async def logic(self):
        print("In ClientAPI.logic(), before while")
        while self.listening:
            print("First path driving")
            await self.logic_loop()
            print("Second path driving")
            await self.drive_back()
            print("Done driving.")
            self.quit_flag.set()
            self.close_connection()

    async def logic_loop(self):
        if self.current_node_marker == 0:
            self.send_command(command="ARE_YOU_READY") #Send a check to client to make sure it's ready
            print("In logic_loop, after sending the command")

            confirmation = await self.receive_message_from_client() #This is where the error comes from.

            if self.confirm(expected="I_AM_READY", confirmation=confirmation): #Receive a ready confirmation from client
                print("In logic_loop, response has been received")
                pass
            else:
                print("-----\nWrong confirmation received from client.\nIn turn_gopigo\n-----")
            
            print("At first node. GoPiGo started")
        
        for node in self.path:

            if node == self.path[-1]:
                print("Goal reached.")
                break

            cardinal_direction = self.check_next_node() #Where the enxt node is: north (1), east (2), south (3), west (4)

            self.send_location_to_map()
            self.update_location()

            if self.is_gopigo_facing_next_node(cardinal_direction=cardinal_direction):
                print("GoPiGo is facing the next node.")
                await self.drive_forward()
            else:
                await self.turn_gopigo(where_from=self.gopigo_direction, to_where=cardinal_direction)
                await self.drive_forward()

    def reverse_path(self):
        self.path = list(reversed(self.path))

    def reset_node_markers(self):
        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

    async def drive_back(self):
        self.reverse_path()
        self.reset_node_markers()
        await self.logic_loop()

    async def receive_message_from_client(self):
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
        self.stop_listening()
        self.client_socket.close()
        self.server_socket.close()
        print("Server closed.")