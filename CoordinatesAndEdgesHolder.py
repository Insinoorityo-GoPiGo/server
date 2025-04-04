class CoordinatesAndEdgesHolder:
    def __init__(self, coordinates, edges):
        self.coordinates = coordinates
        self.edges = edges

    def update_edges(self, new_edges):
        self.edges = new_edges

    def get_coordinates(self):
        return self.coordinates
    
    def get_edges(self):
        return self.edges