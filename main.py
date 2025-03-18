import threading
from time import sleep
import asyncio
import queue 
from map import Map


from PathFinding import PathFinding
from ClientAPI import ClientAPI

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
    
    
def start_map_thread(map):
    (threading.Thread(target=map.run, args=(location_queue,))).start()
    
    

def main():
    path = PathFinding().get_shortest_path(start="A1", end="F9")
    map = Map(queue=location_queue, stop_loop_event=quit_flag)
    client_api = ClientAPI(host="127.0.0.1", port=1025, path=path, quit_flag=quit_flag, location_queue=location_queue)



    #loop.run_until_complete(future=client_api.logic())
    print("Before await client_api.logic()")
    start_thread(client_api=client_api)
    print("After await client_api.logic()")
    
    start_map_thread(map=map)

    while True:
        sleep(0.5)
        if quit_flag.is_set():
            break

if __name__ == "__main__":
    main()