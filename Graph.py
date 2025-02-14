from collections import deque

class Graph:
    def __init__(self, coordinates: dict[str,tuple]):
        self.nodes = set()
        self.adjacency_list = {}
        self.INFINITY = float("inf")
        self.coordinates = coordinates        

    def add_edge(self, from_node, to_node, distance):
        x1, y1 = self.coordinates[from_node]
        x2, y2 = self.coordinates[to_node]

        if (x1 == x2 and abs(y1 - y2) == 1) or (y1 == y2 and abs(x1 - x2) == 1):
            self.nodes.update([from_node, to_node])
            if from_node not in self.adjacency_list:
                self.adjacency_list[from_node] = set()
            if to_node not in self.adjacency_list:
                self.adjacency_list[to_node] = set()
            self.adjacency_list[from_node].add((to_node, distance))
            self.adjacency_list[to_node].add((from_node, distance))

    def shortest_path(self, start_node, end_node):
        unvisited_nodes = self.nodes.copy()
        distance_from_start = {node: (0 if node == start_node else self.INFINITY) for node in self.nodes}
        previous_node = {node: None for node in self.nodes}

        while unvisited_nodes:
            current_node = min(unvisited_nodes, key=lambda node: distance_from_start[node])
            unvisited_nodes.remove(current_node)

            if distance_from_start[current_node] == self.INFINITY:
                break

            for neighbor, distance in self.adjacency_list[current_node]:
                new_path = distance_from_start[current_node] + distance
                if new_path < distance_from_start[neighbor]:
                    distance_from_start[neighbor] = new_path
                    previous_node[neighbor] = current_node

            if current_node == end_node:
                break

        path = deque()
        current_node = end_node
        while previous_node[current_node] is not None:
            path.appendleft(current_node)
            current_node = previous_node[current_node]
        path.appendleft(start_node)

        return list(path), distance_from_start[end_node]