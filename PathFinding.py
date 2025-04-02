from typing import Union

from Graph import Graph

class PathFinding:
    def __init__(self):
        self.COORDINATES = {
            "A0": (-1, 6), "G10": (9, 0),
            "A1": (0, 6), "A2": (1, 6), "A3": (2, 6), "A4": (3, 6), "A5": (4, 6), "A6": (5, 6), "A7": (6, 6), "A8": (7, 6), "A9": (8, 6),
            "B1": (0, 5), "B3": (2, 5), "B7": (6, 5), "B9": (8, 5),
            "C1": (0, 4), "C2": (1, 4), "C3": (2, 4), "C4": (3, 4), "C5": (4, 4), "C6": (5, 4), "C7": (6, 4), "C9": (8, 4),
            "D1": (0, 3), "D3": (2, 3), "D7": (6, 3), "D9": (8, 3),
            "E1": (0, 2), "E3": (2, 2), "E4": (3, 2), "E5": (4, 2), "E6": (5, 2), "E7": (6, 2), "E8": (7, 2), "E9": (8, 2),
            "F1": (0, 1), "F3": (2, 1), "F7": (6, 1), "F9": (8, 1),
            "G1": (0, 0), "G2": (1, 0), "G3": (2, 0), "G4": (3, 0), "G5": (4, 0), "G6": (5, 0), "G7": (6, 0), "G8": (7, 0), "G9": (8, 0)
        }

    def parse_graph(self):
        graph = Graph(coordinates=self.COORDINATES)

        # Add graph edges
        edges = [
            ("A0", "A1", 2), ("G10", "G9", 2), 
            ("A1", "A2", 2), ("A1", "B1", 2), ("A2", "A3", 2), ("A3", "A4", 2),
            ("A3", "B3", 2), ("A4", "A5", 2), ("A5", "A6", 2), ("A6", "A7", 2),
            ("A7", "B7", 2), ("A7", "A8", 2), ("A8", "A9", 2), ("A9", "B9", 2),
            ("B9", "C9", 2), ("C9", "D9", 2), ("D9", "E9", 2), ("E9", "E8", 2),
            ("E9", "F9", 2), ("F9", "G9", 2), ("G9", "G8", 2), ("G8", "G7", 2),
            ("G7", "G6", 2), ("G7", "F7", 2), ("F7", "E7", 2), ("E7", "E8", 2),
            ("E7", "E6", 2), ("E7", "D7", 2), ("D7", "C7", 2), ("C7", "B7", 2),
            ("C7", "C6", 2), ("C6", "C5", 2), ("C5", "C4", 2), ("C4", "C3", 2),
            ("C3", "B3", 2), ("C3", "C2", 2), ("C2", "C1", 2), ("C3", "D3", 2),
            ("D3", "E3", 2), ("E3", "E4", 2), ("E4", "E5", 2), ("E5", "E6", 2),
            ("E3", "F3", 2), ("F3", "G3", 2), ("G3", "G4", 2), ("G4", "G5", 2),
            ("G5", "G6", 2), ("G3", "G2", 2), ("G2", "G1", 2), ("G1", "F1", 2),
            ("F1", "E1", 2), ("E1", "D1", 2), ("D1", "C1", 2), ("B1", "C1", 2)
        
        ]

        for from_node, to_node, distance in edges:
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