import threading
import asyncio
import queue

from control_panel import Control_Panel
from get_coordinates_and_edges import get_coordinates_and_edges
from PathFinding import PathFinding



coordinates, edges = get_coordinates_and_edges()
PathFinding.EDGES = edges

quit_flag = threading.Event()
command_queue = queue.Queue()

def run_server(client_api):
    asyncio.run(client_api.open_connection())

def start_thread(client_api):
    print("In start_thread")
    (threading.Thread(target=run_server, args=(client_api,), daemon=True)).start()



def main():
    #path_1 = PathFinding().get_shortest_path(start="A0", end="E5")
    #path_2 = PathFinding().get_shortest_path(start="G5", end="D1")
    #location_map = Map(queue=location_queue, quit_flag=quit_flag)
    
    #IP_ADDRESS = os.getenv("IP_ADDRESS")
    #client_api_1 = ClientAPI(host=IP_ADDRESS, port=1025, path=path_1, quit_flag=quit_flag, command_queue=command_queue, location_queue=location_queue, default_direction="east", bot_id="Bot_1")
    #client_api_2 = ClientAPI(host=IP_ADDRESS, port=1026, path=path_2, quit_flag=quit_flag, command_queue=command_queue, location_queue=location_queue, default_direction="west", bot_id="Bot_2")
    #start_thread(client_api=client_api_1)
    #start_thread(client_api=client_api_2)

    control_panel=Control_Panel(command_queue=command_queue, quit_flag=quit_flag, coordinates=coordinates, edges=edges)

    control_panel.open_control_panel()

if __name__ == "__main__":
    main()