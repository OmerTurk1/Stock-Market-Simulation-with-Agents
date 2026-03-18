import json

market_history = {}
portfolio = {}
curr_day = "0"

def initialize():
    with open("portfolio.json", "r", encoding="utf-8") as f:
        global portfolio
        portfolio = json.load(f)
    
    with open("market_history.json", "r", encoding="utf-8") as f:
        global market_history
        market_history = json.load(f)

def finish_simulation():
    with open("portfolio.json", "r", encoding="utf-8") as f:
        json.dump(portfolio)