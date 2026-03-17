import json

# market history
market_history = {}
with open("market_history.json", "r", encoding="utf-8") as f:
    market_history = json.load(f)

# portfolio
portfolio = {}
with open("portfolio.json", "r", encoding="utf-8") as f:
    portfolio = json.load(f)