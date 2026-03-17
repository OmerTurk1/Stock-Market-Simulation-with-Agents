from agent import Agent
from globals import market_history

MyAgent = Agent(
    system_message="You are a stock market simulation agent. Your task is to manage a virtual portfolio by making buy and sell decisions based on the provided market data. You will receive daily market information, including stock prices and volumes, and you must decide which stocks to buy or sell to maximize the total value of your portfolio. Always consider the current cash balance and the inventory of stocks you hold before making any decisions. Your goal is to achieve the highest possible return on investment over the simulation period."
)

days = range(1, 31)
for day in days:
    # get market data for the current day
    current_market_data = market_history.get(str(day), {})

    # send market data to the agent and get the response
    responses = MyAgent.send_message(current_market_data)

    # make tool calls based on the agent's response
    if responses.tool_calls:
        for tool_call in responses.tool_calls:
            tool_name = tool_call.name
            tool_args = tool_call.args
            if tool_name == "finish_day":
                print(f"Day {day}: Finished the day. Updating portfolio and market status for the next day.")
                break
            if tool_name in MyAgent.TOOLS:
                result = MyAgent.TOOLS[tool_name](**tool_args)
                print(f"Day {day}: Executed {tool_name} with args {tool_args}. Result: {result}")

    # make portfolio changes