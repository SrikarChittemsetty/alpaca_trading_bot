import os
import time
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

# Alpaca API setup
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

# Trading parameters
SYMBOL = "AAPL"
TIMEFRAME = "5Min"
QTY = 1
SHORT_WINDOW = 10
LONG_WINDOW = 30

def get_moving_averages():
    """Fetches historical bars and calculates short and long moving averages."""
    try:
        bars = api.get_bars(SYMBOL, TIMEFRAME, limit=LONG_WINDOW + 1).df
        if SYMBOL not in bars['symbol'].values:
            print("[ERROR] Symbol not found in returned data.")
            return None, None
        bars = bars[bars['symbol'] == SYMBOL]
        close_prices = bars['close']
        short_ma = close_prices.rolling(window=SHORT_WINDOW).mean().iloc[-1]
        long_ma = close_prices.rolling(window=LONG_WINDOW).mean().iloc[-1]
        return short_ma, long_ma
    except Exception as e:
        print(f"[DATA ERROR] {e}")
        return None, None

def check_positions():
    """Checks if there is currently a position in the SYMBOL."""
    try:
        positions = api.list_positions()
        for position in positions:
            if position.symbol == SYMBOL:
                return True
        return False
    except Exception as e:
        print(f"[POSITION CHECK ERROR] {e}")
        return False

def execute_trade(signal):
    """Executes buy or sell order based on signal."""
    has_position = check_positions()
    try:
        if signal == "buy" and not has_position:
            print("Placing BUY order...")
            order = api.submit_order(
                symbol=SYMBOL,
                qty=QTY,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
            print(f"[ORDER SUBMITTED] Buy order: {order}")
        elif signal == "sell" and has_position:
            print("Placing SELL order...")
            order = api.submit_order(
                symbol=SYMBOL,
                qty=QTY,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
            print(f"[ORDER SUBMITTED] Sell order: {order}")
        else:
            print("[NO TRADE] No action taken.")
    except Exception as e:
        print(f"[ORDER ERROR] {e}")

def main():
    print("🚀 Starting Moving Average Crossover Bot...")
    while True:
        short_ma, long_ma = get_moving_averages()
        if short_ma is None or long_ma is None:
            print("[SKIP] Could not calculate MAs. Retrying in 60 seconds.")
            time.sleep(60)
            continue

        print(f"[MAs] Short MA: {short_ma:.2f} | Long MA: {long_ma:.2f}")

        if short_ma > long_ma:
            print("[SIGNAL] Buy signal detected.")
            execute_trade("buy")
        elif short_ma < long_ma:
            print("[SIGNAL] Sell signal detected.")
            execute_trade("sell")
        else:
            print("[SIGNAL] No clear signal. Holding position.")

        time.sleep(60 * 5)  # Wait 5 minutes

if __name__ == "__main__":
    main()
