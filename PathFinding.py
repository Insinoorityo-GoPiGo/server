from typing import Union

from Graph import Graph

class PathFinding:
    EDGES = list()
    removed_edges = list()
    COORDINATES = dict()

    def __init__(self):
        pass

    def parse_graph(self):
        graph = Graph(coordinates=self.COORDINATES)

        for from_node, to_node, distance in self.EDGES:
            graph.add_edge(from_node, to_node, distance)

        return graph
    
    def get_shortest_path(self, start: Union[str,None], end: Union[str,None]) -> list:
        
        if start == None:
            start = input("Enter the start node: ")
        else:
            start = start
        
        if end == None:
            end = input("Enter the end node: ")
        else:
            end = end

        graph = self.parse_graph()

        if start not in graph.nodes or end not in graph.nodes:
            print("Invalid start or end node.")
            return

        path, distance = graph.shortest_path(start, end)

        return path