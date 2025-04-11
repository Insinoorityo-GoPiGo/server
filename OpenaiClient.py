from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenaiClient:
    def __init__(self):
        self.openai = OpenAI(
            api_key=os.environ.get("API_KEY") #API_KEY variable in .env
        )

    def prompt_openai(self, image_data) -> str:
        response = self.openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who analyzes an image that is received from a storage room autonomouos sorting robot. The robot takes an image that you receive. You call the function, if you see an obstacle in the image. You provide a 2-3 word description of the obstacle as the obstacle parameter for the function."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here's the image that you need to analyze."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                },
            ],
            n=1,
            max_tokens=200
        )
        
        return response["choices"][0]["message"]["content"]

    def get_response(self, image_data) -> str:
        return self.prompt_openai(image_data=image_data)