import threading

from ClientSocket import ClientSocket

class ClientController:
    def __init__(self, path):
        self.threads = [] #client-yhteyksiä

        self.client_socket = ClientSocket(path=path, default_direction="north")

    def add_thread(self, client_id):

        client = {
            "client_id": str(client_id),
            "thread": threading.Thread(target=self.client_socket.logic)
        }
        
        self.threads.append(client)

    def add_client(self, client_id: str):
        self.add_thread(client_id=client_id)

    def begin_client(self, client_id):
        
        index = int()
        for client in self.threads:
            if client["client_id"] == str(client_id):
                index = self.threads.index(client)
                break
        
        self.threads[index]["thread"].run()

    #def logic(self):
    #    self.begin_client()

    def stop_client(self):
        pass

    def continue_client(self):
        pass

    def return_client(self):
        pass