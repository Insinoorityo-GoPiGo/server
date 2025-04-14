import socket
import struct

class ImageReceiverSocket:
    def __init__(self, host="192.168.53.87", port=1100):
        self.HOST = host
        self.PORT = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))

        self.client_socket, self.client_address = None, None

    def open_connection(self):
        self.server_socket.listen(1) #Allow only 1 connection
        print("ImageReceiverSocket is listening")
        self.client_socket, self.client_address = self.server_socket.accept()
        print("ImageReceiverSocket has accepted")
        print("Image socket opened: ",self.client_socket, " ",self.client_address)

    def receive_image(self) -> bytes:
        #Receive 4 bytes indicating the size of the image
        data_len_bytes = self.client_socket.recv(4)

        try:
            if len(data_len_bytes) < 4:
                raise Exception("Failed to receive image length.")
            
            image_len = struct.unpack('>I', data_len_bytes)[0]  # 4-byte big-endian integer
            print("image_len: ",image_len)

            #Receive the full image
            image_data = b''
            while len(image_data) < image_len:
                packet = self.client_socket.recv(4096)
                print("Packet received")
                if not packet:
                    raise Exception("Image data incomplete.")
                image_data += packet
        except Exception("Failed to receive image length.") as e:
            print("Error in receive_image: ",e)
            return None
        except Exception("Image data incomplete.") as e:
            print("Error in receive_image: ",e)
            return None
        except:
            print("Error in receive_image.")


        print("image_data: ", image_data)

        return image_data  #in bytes