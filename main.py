from PathFinding import PathFinding
from ClientAPI import ClientAPI

def main():
    path = PathFinding().get_shortest_path(start="A1", end="F9")
    client_api = ClientAPI(host="127.0.0.1", port=1025, path=path)

if __name__ == "__main__":
    main()