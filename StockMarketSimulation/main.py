import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent import Agent
import globals

async def run_bot():
    # 1. Server Ayarları
    server_script = os.path.abspath("server.py")
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env=os.environ.copy()
    )

    # 2. Ajan Oluşturma
    MyAgent = Agent(
        system_message=""""
        You are a stock market simulation agent. Manage a virtual portfolio.
        Perform buy/sell transactions. IMPORTANT: When you are done for the day,
        you MUST call the 'finish_day' tool to proceed to the next day.
        Tasks for everyday:
        1) Check the market and portfolio using tools.
        2) Perform buy/sell transactions to maximize wealth.
        3) Call 'finish_day' ONLY when you are completely done with this day.""",
        model="gpt-4.1-mini"
    )

    # 3. Simülasyon Hazırlığı
    globals.initialize()
    days = range(1, 21)

    print("--Simulation is Starting!--")

    # MCP Bağlantısını Başlatıyoruz
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Server'ı başlat ve tool listesini al
            await session.initialize()
            available_tools = await session.list_tools()
            
            # Tool şemalarını LLM'in anlayacağı formata çevir
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

            # --- ANA GÜN DÖNGÜSÜ ---
            for day in days:
                globals.curr_day = str(day)
                print(f"\n--- Day {globals.curr_day} Started ---")

                # O günün başlangıç mesajı
                user_content = f"""
                Current Day: {globals.curr_day}
                """
                
                # Gün içindeki işlem döngüsü (Tool Call Loop)
                while True:
                    response = MyAgent.send_message(user_content, tools=tools_for_llm)
                    message = response.choices[0].message

                    if message.tool_calls:
                        MyAgent.messages.append(message)
                        should_finish_day = False
                        
                        for call in message.tool_calls:
                            tool_name = call.function.name
                            args = json.loads(call.function.arguments)

                            if tool_name == "finish_day":
                                print(f"[*] Agent decided to finish Day {globals.curr_day}.")
                                should_finish_day = True
                                result_text = "Day finished successfully."
                            else:
                                print(f"[*] Tool Call: {tool_name} with {args}")
                                result = await session.call_tool(tool_name, arguments=args)
                                result_text = "\n".join([c.text for c in result.content if hasattr(c, 'text')])

                            MyAgent.messages.append({
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result_text
                            })

                        if should_finish_day:
                            break 
                        
                        user_content = "Please continue with your next action or finish the day."
                    else:
                        print(f"Bot: {message.content}")
                        MyAgent.messages.append(message)
                        break

                # --- GÜN SONU HAFIZA TEMİZLİĞİ (YENİ EKLENEN KISIM) ---
                # Ajanın kafası karışmasın ve token şişmesin diye tool çağrılarını temizliyoruz
                cleaned_history = []
                for msg in MyAgent.messages:
                    # System mesajlarını (talimatları) ve kullanıcı mesajlarını tut
                    if msg.get("role") in ["system", "user"]:
                        cleaned_history.append(msg)
                    # Assistant mesajlarını sadece saf metin varsa tut, tool_calls kısımlarını temizle
                    elif msg.get("role") == "assistant":
                        if msg.get("content"): # Eğer model bir açıklama yazdıysa koru
                            cleaned_history.append({"role": "assistant", "content": msg.get("content")})
                    # 'tool' rolündeki ham verileri tamamen sil
                    elif msg.get("role") == "tool":
                        continue
                
                MyAgent.messages = cleaned_history
                # ---------------------------------------------------

                print(f"--- Day {globals.curr_day} Finished ---")

    # Simülasyonu kapat
    globals.finish_simulation()
    print("--Simulation Completed!--")

if __name__ == "__main__":
    asyncio.run(run_bot())