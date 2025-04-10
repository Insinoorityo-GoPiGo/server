from control_panel import Control_Panel
from get_coordinates_and_edges import get_coordinates_and_edges
from PathFinding import PathFinding



def main():
    PathFinding.COORDINATES, PathFinding.EDGES = get_coordinates_and_edges()
    
    control_panel=Control_Panel()
    control_panel.open_control_panel()

if __name__ == "__main__":
    main()