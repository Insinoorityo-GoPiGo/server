import threading
import queue

from control_panel import Control_Panel
from get_coordinates_and_edges import get_coordinates_and_edges
from PathFinding import PathFinding



PathFinding.COORDINATES, PathFinding.EDGES = get_coordinates_and_edges()

map_quit_flag = threading.Event()
client_quit_flag = threading.Event()
command_queue = queue.Queue()



def main():
    control_panel=Control_Panel(command_queue=command_queue, map_quit_flag=map_quit_flag, client_quit_flag=client_quit_flag)
    control_panel.open_control_panel()



if __name__ == "__main__":
    main()