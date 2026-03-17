from openai import OpenAI
from globals import portfolio
import os

class Agent:
    def __init__(self, system_message: str, model: str = "gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_message = system_message
        self.model = model

    def send_message(self, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()

    def update_total_balance(self):
        cash = portfolio.get("cash", 0)
        inventory = portfolio.get("inventory", {})
        current_total_stock_value = sum(
            item.get("current_price", 0) * item.get("quantity", 0) 
            for item in inventory.values()
        )
        portfolio["total_value"] = cash + current_total_stock_value