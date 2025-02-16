from ClientCommands import ClientCommands

from string import ascii_letters

class ClientSocket(ClientCommands):
    def __init__(self, path, default_direction = "north"):
        #ClientCommands.__init__()
        self.path = path

        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

        self.cardinal_directions = ["north", "east", "south", "west"]
        self.gopigo_direction = default_direction

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

        return command
    
    def drive_forward(self):
        print("Drive forward.")

    def update_location(self):
        self.current_node_marker = self.current_node_marker + 1
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]

        if self.next_node_marker <= len(self.path) - 1:
            self.next_node = self.path[self.next_node_marker]

        #print("Location updated.")

    def reverse_path(self):
        self.path = list(reversed(self.path))

    def drive_back(self):

        self.current_node_marker = 0
        self.next_node_marker = self.current_node_marker + 1

        self.current_node = self.path[self.current_node_marker]
        self.next_node = self.path[self.next_node_marker]

        self.drive_path()

    def drive_path(self):
        if self.current_node_marker == 0:
            print("At first node. GoPiGo started")
        
        for node in self.path:
            #print("At the start of the loop.")
            #print("node: ",node)
            #print("-1: ",self.path[-1])
            if node == self.path[-1]:
                print("Goal reached.")
                break

            cardinal_direction = self.check_next_node() #Where the enxt node is: north (1), east (2), south (3), west (4)

            self.update_location()

            if self.is_gopigo_facing_next_node(cardinal_direction=cardinal_direction):
                print("GoPiGo is facing the next node.")
                self.drive_forward()
            else:
                command = self.turn_gopigo(where_from=self.gopigo_direction, to_where=cardinal_direction)
                self.drive_forward()

    def logic(self):
        self.drive_path()
        self.drive_back()