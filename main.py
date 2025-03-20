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

async def run_logic(client_api):
    print("In run_logic")
    await client_api.logic()

def run_function(client_api):
    print("In run_function")
    asyncio.run(run_logic(client_api=client_api))

def start_thread(client_api):
    print("In startt_thread")
    (threading.Thread(target=run_function, args=(client_api,))).start()

def main():
    path = PathFinding().get_shortest_path(start="A1", end="C3")
    map = Map(queue=location_queue, stop_loop_event=quit_flag)
    
    
    client_api = ClientAPI(host=os.getenv("IP_ADDRESS"), port=1025, path=path, quit_flag=quit_flag, location_queue=location_queue)
    start_thread(client_api=client_api)

    
    map.run()

    while True:
        sleep(0.5)
        if quit_flag.is_set():
            break

if __name__ == "__main__":
    main()