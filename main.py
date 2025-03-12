from threading import Event
from time import sleep
import asyncio

from PathFinding import PathFinding
from ClientAPI import ClientAPI

quit_flag = Event()

async def main():
    path = PathFinding().get_shortest_path(start="A1", end="F9")
    client_api = ClientAPI(host="127.0.0.1", port=1025, path=path, quit_flag=quit_flag)

    #loop.run_until_complete(future=client_api.logic())
    print("Before await client_api.logic()")
    await client_api.logic()
    print("After await client_api.logic()")

    while True:
        sleep(0.5)
        if quit_flag.is_set():
            break

if __name__ == "__main__":
    asyncio.run(main())