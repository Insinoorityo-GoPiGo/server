from control_panel import Control_Panel
from get_coordinates_and_edges import get_coordinates_and_edges
from PathFinding import PathFinding



def main():
    #Openai ja kuvankäsittely -threadin käynnistys

    PathFinding.COORDINATES, PathFinding.EDGES = get_coordinates_and_edges()

    Control_Panel().open_control_panel()

if __name__ == "__main__":
    main()