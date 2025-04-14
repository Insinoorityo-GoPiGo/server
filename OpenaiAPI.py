from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenaiAPI:
    def __init__(self, api_key):
        self.openai = OpenAI(
            api_key=api_key #API_KEY variable in .env
        )

    def prompt_openai(self, image_data) -> str:
        response = self.openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who describes an image that is received from a storage room autonomouos sorting robot. The robot takes an image that you receive. If you see an obstacle in the image, you provide a description consisting of 3 to 6 words for the obstacle."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here's the image that you need to analyze. Remember: 3 to 6 words."
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
            max_tokens=50
        )
        
        return response.choices[0].message.content

    def get_response(self, image_data) -> str:
        return self.prompt_openai(image_data=image_data)