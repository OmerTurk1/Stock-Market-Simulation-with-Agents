import globals
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Database Manager")

@mcp.tool()
def buy_stock(stock_symbol: str, quantity: int) -> str:
    """
    Buys a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to buy.
    quantity (int): The number of shares to buy.
    
    Returns:
    str: A message indicating the result of the purchase.
    """
    try:
        stocks_today = globals.market_history[globals.curr_day]["stocks_infos"]
        if stock_symbol not in stocks_today:
            return {
                "status": "error",
                "explanation": f"There is no such stock name {stock_symbol}."
            }
        
        price = stocks_today[stock_symbol]["price"]
        total_cost = price * quantity

        if total_cost > globals.portfolio["cash"]:
            return {
                "status":"error",
                "explanation":"Insufficient cash in your portfolio."
            }
        
        if stock_symbol not in globals.portfolio["inventory"]:
            globals.portfolio["inventory"][stock_symbol] = {
                "quantity": 0,
                "average_bought_price": price
            }
        
        old_quantity = globals.portfolio["inventory"][stock_symbol]["quantity"]
        old_average = globals.portfolio["inventory"][stock_symbol]["average_bought_price"]
        globals.portfolio["inventory"][stock_symbol]["average_bought_price"] = (old_quantity*old_average + total_cost) / (quantity+old_quantity)
        globals.portfolio["inventory"][stock_symbol]["quantity"] += quantity
        globals.portfolio["cash"] -= total_cost

        return {
            "status": "success", 
            "explanation": f"Successfully bought {quantity} shares of {stock_symbol}."
        }

    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An unexpected error occurred: {str(e)}"
        }

@mcp.tool()
def sell_stock(stock_symbol: str, quantity: int) -> str:
    """
    Sells a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to sell.
    quantity (int): The number of shares to sell.
    
    Returns:
    str: A message indicating the result of the sale.
    """
    try:
        stocks_today = globals.market_history[globals.curr_day]["stocks_infos"]
        if stock_symbol not in stocks_today:
            return {
                "status": "error",
                "explanation": f"There is no such stock name {stock_symbol} in market history."
            }
        
        if (stock_symbol not in globals.portfolio["inventory"]) or globals.portfolio["inventory"][stock_symbol]["quantity"] <= 0:
            return {
                "status": "error",
                "explanation": f"You do not own any shares of {stock_symbol}."
            }
        
        current_inventory_qty = globals.portfolio["inventory"][stock_symbol]["quantity"]
        if quantity > current_inventory_qty:
            return {
                "status": "error",
                "explanation": f"Insufficient shares. You only have {current_inventory_qty} shares."
            }
        
        price = stocks_today[stock_symbol]["price"]
        total_revenue = price * quantity

        globals.portfolio["inventory"][stock_symbol]["quantity"] -= quantity
        globals.portfolio["cash"] += total_revenue

        if globals.portfolio["inventory"][stock_symbol]["quantity"] == 0:
            del globals.portfolio["inventory"][stock_symbol]

        return {
            "status": "success",
            "explanation": f"Successfully sold {quantity} shares of {stock_symbol} at {price} price."
        }

    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An unexpected error occurred: {str(e)}"
        }

@mcp.tool()
def view_portfolio() -> str:
    """
    Displays the current portfolio, including cash, inventory, and total value.
    
    Returns:
    str: A message showing the current portfolio status.
    """
    return globals.portfolio

@mcp.tool()
def view_market(last_n_days: int) -> dict:
    """
    Displays the market status for the current day and the specified 
    number of previous days.
    
    Parameters:
    last_n_days (int): How many days back to look (including today).
    
    Returns:
    dict: A dictionary where keys are day numbers and values are stock infos.
    """
    try:
        market_summary = {}
        current = int(globals.curr_day)
        
        days_to_show = max(1, last_n_days)
        
        for i in range(days_to_show):
            target_day = current - i
            
            if target_day < 1:
                break
                
            day_key = str(target_day)
            
            if day_key in globals.market_history:
                market_summary[day_key] = globals.market_history[day_key]["stocks_infos"]
        
        if not market_summary:
            return {"status": "error", "explanation": "No market history available for the requested range."}
            
        return market_summary

    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An error occurred while fetching market history: {str(e)}"
        }

@mcp.tool()
def finish_day() -> str:
    """
    Finalizes the current day, updating the portfolio and market status for the next day.
    
    Returns:
    str: A message indicating the end of the day and any relevant updates.
    """
    return {
        "status": "success",
        "explanation": f"Day {globals.curr_day} finished, going to next day."
    }

if __name__ == "__main__":
    mcp.run()