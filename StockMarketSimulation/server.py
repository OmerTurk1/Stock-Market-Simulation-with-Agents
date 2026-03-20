import globals
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Database Manager")

@mcp.tool()
def buy_stock(stock_symbol: str, quantity: int):
    """
    Buys a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to buy.
    quantity (int): The number of shares to buy.
    
    Returns:
    str: A message indicating the result of the purchase.
    """
    try:
        portfolio = globals.read_portfolio()
        market_history = globals.read_market_history()
        curr_day = globals.read_curr_day()

        stocks_today = market_history[curr_day]["stocks_infos"]
        if stock_symbol not in stocks_today:
            return {
                "status": "error",
                "explanation": f"There is no such stock name {stock_symbol}."
            }
        
        price = stocks_today[stock_symbol]["price"]
        total_cost = round(price * quantity,4)

        if total_cost > portfolio["cash"]:
            return {
                "status":"error",
                "explanation":"Insufficient cash in your portfolio."
            }
        
        if stock_symbol not in portfolio["inventory"]:
            portfolio["inventory"][stock_symbol] = {
                "quantity": 0,
                "average_bought_price": price
            }
        
        old_quantity = portfolio["inventory"][stock_symbol]["quantity"]
        old_average = portfolio["inventory"][stock_symbol]["average_bought_price"]
        portfolio["inventory"][stock_symbol]["average_bought_price"] = round(
            (old_quantity*old_average + total_cost) / (quantity+old_quantity),
            4
        )
        portfolio["inventory"][stock_symbol]["quantity"] += quantity
        portfolio["cash"] -= total_cost

        if update_portfolio(curr_day,portfolio,market_history):
            return {
                "status": "success", 
                "explanation": f"Successfully bought {quantity} shares of {stock_symbol}."
            }
        else:
            return {
                "status": "error",
                "explanation": f"An unexpected error occurred: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An unexpected error occurred: {str(e)}"
        }

@mcp.tool()
def sell_stock(stock_symbol: str, quantity: int):
    """
    Sells a specified quantity of a stock.
    
    Parameters:
    stock_symbol (str): The symbol of the stock to sell.
    quantity (int): The number of shares to sell.
    
    Returns:
    str: A message indicating the result of the sale.
    """
    try:
        portfolio = globals.read_portfolio()
        market_history = globals.read_market_history()
        curr_day = globals.read_curr_day()

        stocks_today = market_history[curr_day]["stocks_infos"]
        if stock_symbol not in stocks_today:
            return {
                "status": "error",
                "explanation": f"There is no such stock name {stock_symbol} in market history."
            }
        
        if (stock_symbol not in portfolio["inventory"]) or portfolio["inventory"][stock_symbol]["quantity"] <= 0:
            return {
                "status": "error",
                "explanation": f"You do not own any shares of {stock_symbol}."
            }
        
        current_inventory_qty = portfolio["inventory"][stock_symbol]["quantity"]
        if quantity > current_inventory_qty:
            return {
                "status": "error",
                "explanation": f"Insufficient shares. You only have {current_inventory_qty} shares."
            }
        
        price = stocks_today[stock_symbol]["price"]
        total_revenue = round(price * quantity,4)

        portfolio["inventory"][stock_symbol]["quantity"] -= quantity
        portfolio["cash"] += total_revenue

        if portfolio["inventory"][stock_symbol]["quantity"] == 0:
            del portfolio["inventory"][stock_symbol]
    
        if update_portfolio(curr_day,portfolio,market_history):
            return {
                "status": "success",
                "explanation": f"Successfully sold {quantity} shares of {stock_symbol} at {price} price."
            }
        else:
            return {
                "status": "error",
                "explanation": f"An unexpected error occurred: {str(e)}"
            }

    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An unexpected error occurred: {str(e)}"
        }

@mcp.tool()
def view_portfolio():
    """
    Displays the current portfolio, including cash, inventory, and total value.
    
    Returns:
    str: A message showing the current portfolio status.
    """
    return globals.read_portfolio()

@mcp.tool()
def view_market(last_n_days: int):
    """
    Displays the market status for the current day and the specified 
    number of previous days.
    
    Parameters:
    last_n_days (int): How many days back to look (including today).
    
    Returns:
    dict: A dictionary where keys are day numbers and values are stock infos.
    """
    try:
        market_history = globals.read_market_history()

        market_summary = {}
        current = int(globals.read_curr_day())
        
        lower = max(current-last_n_days+1,1)
        upper = current
        days_to_show = [str(i) for i in range(lower, upper+1)]
        
        for i in days_to_show:
            market_summary[i] = market_history[i]["stocks_infos"]
        
        if not market_summary:
            return {"status": "error", "explanation": f"No market history available for the requested range:{days_to_show}"}
            
        return market_summary

    except Exception as e:
        return {
            "status": "error",
            "explanation": f"An error occurred while fetching market history: {str(e)}"
        }

@mcp.tool()
def finish_day():
    """
    Finalizes the current day, updating the portfolio and market status for the next day.
    
    Returns:
    str: A message indicating the end of the day and any relevant updates.
    """
    try:
        curr_day = globals.read_curr_day()
        portfolio = globals.read_portfolio()
        market_history = globals.read_market_history()

        if update_portfolio(curr_day, portfolio, market_history):
            return {
                "status": "success",
                "explanation": f"Day {curr_day} finished, going to next day."
            }
        else:
            return {
                "status": "error",
                "explanation": f"Failed to finish day {curr_day}: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "explanation": f"Failed to finish day {curr_day}: {str(e)}"
        }

def update_portfolio(curr_day, portfolio, market_history):
    try:
        stocks_today = market_history[curr_day]["stocks_infos"]
        
        cash = portfolio.get("cash", 0)
        inventory_value = 0
        
        for stock_symbol, info in portfolio.get("inventory", {}).items():
            if stock_symbol in stocks_today:
                price = stocks_today[stock_symbol]["price"]
                inventory_value += info["quantity"] * price
        
        total_wealth = cash + inventory_value
        portfolio["total_value"] = total_wealth

        globals.write_portfolio(portfolio)
        return True
    except:
        return False

if __name__ == "__main__":
    start_portfolio = {
        "cash": 10000,
        "inventory": {},
        "total_value": 10000
    }
    globals.write_portfolio(start_portfolio)
    mcp.run()