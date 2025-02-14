from PathFinding import PathFinding
from ClientController import ClientController

def main():
    path_finding = PathFinding()
    path = path_finding.get_shortest_path()

    client_controller = ClientController(path=path)
    client_controller.add_client(client_id=1)
    client_controller.begin_client(client_id=1)

if __name__ == "__main__":
    main()