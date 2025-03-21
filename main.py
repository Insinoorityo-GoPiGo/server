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
    (threading.Thread(target=run_server, args=(client_api,))).start()



def main():
    path = PathFinding().get_shortest_path(start="A0", end="E5")
    map = Map(queue=location_queue, quit_flag=quit_flag)
    
    print(os.getenv("IP_ADDRESS"))
    client_api = ClientAPI(host="127.0.0.1", port=1025, path=path, quit_flag=quit_flag, location_queue=location_queue)
    start_thread(client_api=client_api)

    print("before map.run()")
    #map.run()

if __name__ == "__main__":
    main()