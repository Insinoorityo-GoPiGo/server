import os
from dotenv import load_dotenv

from ImageReceiverSocket import ImageReceiverSocket
from OpenaiAPI import OpenaiAPI

load_dotenv()

class ImageAnalysisHander:
    def __init__(self, ):
        self.image_receiver_socket = ImageReceiverSocket(host=os.environ.get("IP_ADDRESS"), port=1100)
        self.openai_api = OpenaiAPI(api_key=os.environ.get("API_KEY"))

    def start(self):
        self.image_receiver_socket.open_connection()

    def logic(self):
        image_as_bytes = self.image_receiver_socket.receive_image()
        description = self.openai_api.get_response(image_data=image_as_bytes) #description of the object
        #Here send the description to a queue