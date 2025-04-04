import networkx as nx
import matplotlib.pyplot as plt
from queue import Empty
import copy

from get_coordinates_and_edges import get_coordinates_and_edges

class Map:
    def __init__(self, quit_flag, location_queue_1, location_queue_2, highlighted_edge):
        self.quit_flag = quit_flag

        self.location_queue_1 = location_queue_1
        self.location_queue_2 = location_queue_2

        # Määritellään graafi
        self.G = nx.Graph()

        coordinates, edges = get_coordinates_and_edges()
        self.points = copy.deepcopy(coordinates)
        self.edges = copy.deepcopy([(coord_1, coord_2) for coord_1, coord_2, weight in edges])
        del coordinates
        del edges

        self.G.add_nodes_from(self.points.keys())
        self.G.add_edges_from(self.edges)

        self.highlight_node_gpg_1 = "A0"
        self.highlight_node_gpg_2 = "G5"

        self.highlight_edge = highlighted_edge
        
        self.fig, self.ax = plt.subplots()
        
        plt.ion()
        self.update_graph()

    def update_graph(self):
        self.ax.clear()

        node_colors = [ #highlighted noden värin määrittäminen
            "green" if node == self.highlight_node_gpg_1 
            else "yellow" if node == self.highlight_node_gpg_2
            else "red"
            
            for node in self.G.nodes
        ]

        edge_colors = [
            "red" if edge == self.highlight_edge or edge[::-1] == self.highlight_edge 
            else "gray"
            for edge in self.G.edges
        ]

        nx.draw(self.G, self.points, node_color=node_colors, node_size=300, edge_color=edge_colors, ax=self.ax)
        nx.draw_networkx_labels(self.G, self.points, font_color="black", font_size=10, ax=self.ax)

        plt.show(block=False) #Figure 1 avataan
        plt.pause(0.1)

    def set_highlight(self, client_locations: tuple[dict]):
        for location in client_locations:
            
            if location["node"] in self.G.nodes:
                print(f"Highlight node: {location}")
                
                if location["id"] == "gopigo_1":
                    self.highlight_node_gpg_1 = location["node"] #Is the highlighted node
                elif location["id"] == "gopigo_2":
                    self.highlight_node_gpg_2 = location["node"]
                
        self.update_graph()

    def get_location(self, queue) -> dict|None:
        location = object()

        try:
            location = queue.get(block=False)
        except Empty:
            #print("Jono on tyhjä")
            location = None

        return location

    def run(self):
        print("map started")
        try:
            while plt.fignum_exists(self.fig.number) and not self.quit_flag.is_set():
                client_locations = (
                    location 
                    for location 
                    in (
                        self.get_location(queue=self.location_queue_1), 
                        self.get_location(queue=self.location_queue_2)
                    ) 
                    if location != None
                )

                self.set_highlight(client_locations=client_locations)
                
        except KeyboardInterrupt:
            plt.close('all')
        except Exception as e:
            print("An exception has occured in map.py run() function: ",e)
        finally:
            print("map.py has closed")
            plt.close(self.fig)

        plt.ioff()
        plt.show()
        







#Unused as of now
    def update_map(self):
        server_input = self.get_location(queue=self.location_queue_1)

        if server_input:
            self.set_highlight(location=server_input)

        plt.pause(0.1)
        self.fig.canvas.flush_events()

        self.fig.canvas.get_tk_widget().after(500, self.update_map)