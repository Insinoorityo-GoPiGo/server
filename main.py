import threading
from time import sleep
import asyncio
import queue
from dotenv import load_dotenv
import os

from map import Map
from PathFinding import PathFinding
from ClientAPI import ClientAPI

load_dotenv()

quit_flag = threading.Event()
location_queue = queue.Queue()

def run_server(client_api):
    asyncio.run(client_api.open_connection())

def start_thread(client_api):
    print("In start_thread")
    (threading.Thread(target=run_server, args=(client_api,), daemon=True)).start()



def main():
    path1 = PathFinding().get_shortest_path(start="A0", end="E5")
    path2 = PathFinding().get_shortest_path(start="G5", end="D1")
    map = Map(queue=location_queue, quit_flag=quit_flag)
    
    client_api_1 = ClientAPI(host="127.0.0.1", port=1025, path=path1, quit_flag=quit_flag, location_queue=location_queue, bot_id="Bot_1")
    client_api_2 = ClientAPI(host="127.0.0.1", port=1026, path=path2, quit_flag=quit_flag, location_queue=location_queue, bot_id="Bot_2")
    start_thread(client_api=client_api_1)
    start_thread(client_api=client_api_2)

    print("before map.run()")
    map.run()

if __name__ == "__main__":
    main()