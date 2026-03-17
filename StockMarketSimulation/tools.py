import json
from globals import portfolio, market_history

def buy_stock(stock_symbol: str, quantity: int) -> str:
    """
    Buys a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to buy.
    quantity (int): The number of shares to buy.
    
    Returns:
    str: A message indicating the result of the purchase.
    """
    pass

def sell_stock(stock_symbol: str, quantity: int) -> str:
    """
    Sells a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to sell.
    quantity (int): The number of shares to sell.
    
    Returns:
    str: A message indicating the result of the sale.
    """
    pass
def view_portfolio() -> str:
    """
    Displays the current portfolio, including cash, inventory, and total value.
    
    Returns:
    str: A message showing the current portfolio status.
    """
    with open("portfolio.json", "r", encoding="utf-8") as f:
        portfolio = json.load(f)
    return portfolio
def view_market() -> str:
    """
    Displays the current market status, including stock prices and trends.
    
    Returns:
    str: A message showing the current market status.
    """
    pass

def finish_day() -> str:
    """
    Finalizes the current day, updating the portfolio and market status for the next day.
    
    Returns:
    str: A message indicating the end of the day and any relevant updates.
    """
    pass