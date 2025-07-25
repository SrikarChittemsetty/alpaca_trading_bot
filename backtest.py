import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

def backtest_strategy(data, short_window=10, long_window=30, initial_cash=10000):
    data = data.copy()
    
    # Calculate moving averages
    data['SMA_short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['close'].rolling(window=long_window).mean()
    
    # Initialize portfolio tracking
    data['position'] = 0  # 1 means holding stock, 0 means no position
    data['cash'] = initial_cash
    data['holdings'] = 0
    data['total'] = initial_cash
    data['signal'] = 0  # 1 buy, -1 sell, 0 hold
    
    position = 0
    cash = initial_cash
    
    for i in range(1, len(data)):
        if pd.isna(data.loc[data.index[i], 'SMA_short']) or pd.isna(data.loc[data.index[i], 'SMA_long']):
            data.at[data.index[i], 'position'] = position
            data.at[data.index[i], 'cash'] = cash
            data.at[data.index[i], 'holdings'] = position * data.loc[data.index[i], 'close']
            data.at[data.index[i], 'total'] = cash + position * data.loc[data.index[i], 'close']
            continue
        
        if data.loc[data.index[i], 'SMA_short'] > data.loc[data.index[i], 'SMA_long'] and position == 0:
            position = 1
            cash -= data.loc[data.index[i], 'close']  # buy 1 share
            data.at[data.index[i], 'signal'] = 1
        elif data.loc[data.index[i], 'SMA_short'] < data.loc[data.index[i], 'SMA_long'] and position == 1:
            position = 0
            cash += data.loc[data.index[i], 'close']  # sell 1 share
            data.at[data.index[i], 'signal'] = -1
        else:
            data.at[data.index[i], 'signal'] = 0
        
        data.at[data.index[i], 'position'] = position
        data.at[data.index[i], 'cash'] = cash
        data.at[data.index[i], 'holdings'] = position * data.loc[data.index[i], 'close']
        data.at[data.index[i], 'total'] = cash + position * data.loc[data.index[i], 'close']
    
    return data

if __name__ == "__main__":
    data = api.get_bars("AAPL", "1Day", limit=100).df
    data.index = pd.to_datetime(data.index)
    data = data.sort_index()

    backtest_result = backtest_strategy(data, short_window=10, long_window=30)
    
    print(backtest_result[['close', 'SMA_short', 'SMA_long', 'signal', 'position', 'total']].tail())
    
    backtest_result['total'].plot(title="Portfolio Value Over Time")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    plt.show()
