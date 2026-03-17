import yfinance as yf
import json
import pandas as pd

# Stocks
stock_symbols = [
    "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS", 
    "BRYAT.IS", "FROTO.IS", "GARAN.IS", "HALKB.IS", "ISCTR.IS", 
    "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", 
    "TAVHL.IS", "THYAO.IS", "TOASO.IS", "TUPRS.IS", "YKBNK.IS",
]

def generate_market_history():
    print("Extracting Data...")
    df = yf.download(stock_symbols, period="20d", interval="1d")
    
    market_history = {}
    
    for i in range(len(df)):
        day_index = str(i + 1)
        stocks_infos = {}
        
        for symbol in stock_symbols:
            try:
                # Extracting Close and Volume values
                price = df['Close'][symbol].iloc[i]
                volume = df['Volume'][symbol].iloc[i]
                
                # Control NaN (empty) data (stock market holidays, etc.)
                if not (pd.isna(price) or pd.isna(volume)):
                    stocks_infos[symbol] = {
                        "price": round(float(price), 2),
                        "volume": int(volume)
                    }
            except Exception:
                continue # In case of an error (e.g., invalid symbol or missing data), skip to the next symbol

        # If data for that day could be taken, add it to the main dictionary
        if stocks_infos:
            market_history[day_index] = {
                "dayNumber": int(day_index),
                "stocks_infos": stocks_infos
            }

    # Saving the data to a file
    with open("market_history.json", "w", encoding="utf-8") as f:
        json.dump(market_history, f, ensure_ascii=False, indent=4)
    
    print(f"Extraction completed! {len(market_history)} days of data saved to 'market_history.json'.")

if __name__ == "__main__":
    generate_market_history()