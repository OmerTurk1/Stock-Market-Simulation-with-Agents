from openai import OpenAI
from globals import portfolio
import os

class Agent:
    def __init__(self, system_message: str, model: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_message = system_message
        self.model = model

    def send_to_model(self, messages, tools=None):
        params = {
            "model": self.model,
            "messages": [
                {"role":"system","message":self.system_message},
                {"role":"user","message":messages}
            ]
        }
        if tools:
            params["tools"] = tools
            
        return self.client.chat.completions.create(**params)