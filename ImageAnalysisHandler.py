import os
from dotenv import load_dotenv
import threading
import base64
import time

from ImageReceiverSocket import ImageReceiverSocket
from OpenaiAPI import OpenaiAPI

load_dotenv()

class ImageAnalysisHander:
    def __init__(self, obstacle_description_queue):
        print("In ImageAnalysisHander init()")
        self.image_receiver_socket = ImageReceiverSocket(host=os.environ.get("IP_ADDRESS"), port=1100)
        self.openai_api = OpenaiAPI(api_key=os.environ.get("API_KEY"))

        self.obstacle_description_queue = obstacle_description_queue
        print("ImageAnalysisHander init() complete.")

    def start(self):
        print("In ImageAnalysisHander start(), before open_connection()")
        self.image_receiver_socket.open_connection()

        threading.Thread(target=self.logic_loop, daemon=True).start()
        
    def logic_loop(self):
        print("In ImageAnalysisHander logic_loop()")
        while True:
            image_as_bytes = self.image_receiver_socket.receive_image()
            if image_as_bytes is None:
                time.sleep(1)
                continue
            else:
                print("image_as_bytes received")

            encoded = base64.b64encode(image_as_bytes).decode('utf-8')

            description = self.openai_api.get_response(image_data=encoded) #description of the object
            print(description)
            self.obstacle_description_queue.put(description)