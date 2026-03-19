import json
import os

def read_market_history():
    with open("market_history.json", "r", encoding="utf-8") as f:
        return json.load(f)

def read_portfolio():
    with open("portfolio.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_portfolio(new_portfolio):
    with open("portfolio.json", "w", encoding="utf-8") as f:
        json.dump(new_portfolio, f, indent=4, ensure_ascii=False)

def read_curr_day():
    with open("curr_day.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["curr_day"]
    
def write_curr_day(new_day):
    with open("curr_day.json", "w", encoding="utf-8") as f:
        json.dump({"curr_day": new_day}, f, indent=4, ensure_ascii=False)