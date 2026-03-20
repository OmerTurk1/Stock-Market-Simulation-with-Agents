import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from client import send_to_model
import globals

async def run_bot():
    # Server Settings
    server_script = os.path.abspath("server.py")
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env=os.environ.copy()
    )

    # initialize messages
    messages = [
        {"role": "system", "content": """
        You are a stock market simulation agent. Manage a virtual portfolio.
        Perform buy/sell transactions until you gain more than %1 profit per day.
        Tasks for everyday:
        1) Check the market and portfolio using tools.
        2) Perform buy/sell transactions to maximize wealth.
        3) Call 'finish_day' ONLY when you are completely done with this day.
         4) You are not allowed to talk, just use tools"""}
    ]

    # simulation preparing
    days = range(1, 21)

    print("--Simulation is Starting!--")

    # MCP connection
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            available_tools = await session.list_tools()
            
            # Tool schemas
            tools_for_llm = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in available_tools.tools
            ]

            # Days loop
            for day in days:
                globals.write_curr_day(str(day))
                print(f"\nDay {globals.read_curr_day()} Started")

                # start message of the day
                user_content = f"""
                Current Day: {globals.read_curr_day()}. No talk allowed, just use tools.
                """
                messages.append({"role":"user","content":user_content})
                
                # Tool call loop
                while True:
                    response = send_to_model(messages, tools=tools_for_llm)
                    message = response.choices[0].message

                    if message.tool_calls:
                        messages.append(message)
                        should_finish_day = False
                        
                        for call in message.tool_calls:
                            tool_name = call.function.name
                            args = json.loads(call.function.arguments)
                            print(f"[*] Tool Call: {tool_name} with {args}")
                            result = await session.call_tool(tool_name, arguments=args)

                            if tool_name == "finish_day":
                                # print("tool output:",result)
                                print(f"[*] Agent decided to finish Day {globals.read_curr_day()}.")
                                should_finish_day = True
                                result_text = "Day finished successfully."
                            else:
                                result_text = "\n".join([c.text for c in result.content if hasattr(c, 'text')])

                            messages.append({
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result_text
                            })

                        if should_finish_day:
                            break 
                        
                        user_content = "Please continue with your next action or finish the day."
                    else:
                        print(f"Bot: {message.content}")
                        messages.append(message)
                        break

                # clean tool calls in order to reduce spent token
                cleaned_history = []
                for msg in messages:
                    role = msg.role if hasattr(msg, 'role') else msg.get("role")
                    content = msg.content if hasattr(msg, 'content') else msg.get("content")
                    if role in ["system", "user"]:
                        cleaned_history.append({"role": role, "content": content})
                    elif role == "assistant" and content:
                        cleaned_history.append({"role": "assistant", "content": content})
                    elif role == "tool":
                        continue
                
                messages = cleaned_history

                print(f"Day {globals.read_curr_day()} Finished.")

    # close simulation
    print("--Simulation Completed!--")

if __name__ == "__main__":
    asyncio.run(run_bot())