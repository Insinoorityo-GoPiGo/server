import socket
import struct

class ImageReceiverSocket:
    def __init__(self, host="127.0.0.1", port=1100):
        self.HOST = host
        self.PORT = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.client_socket, self.client_address = None, None

    def open_connection(self):
        self.server_socket.listen(1) #Allow only 1 connection
        self.client_socket, self.client_address = self.server_socket.accept()

    def receive_image(self) -> bytes:
        #Receive 4 bytes indicating the size of the image
        data_len_bytes = self.client_socket.recv(4)
        if len(data_len_bytes) < 4:
            raise ConnectionError("Failed to receive image length.")

        image_len = struct.unpack('>I', data_len_bytes)[0]  # 4-byte big-endian integer

        #Receive the full image
        image_data = b''
        while len(image_data) < image_len:
            packet = self.client_socket.recv(4096)
            if not packet:
                raise ConnectionError("Image data incomplete.")
            image_data += packet

        return image_data  #in bytes