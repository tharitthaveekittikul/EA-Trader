import datetime
import time

import MetaTrader5 as mt5
import pandas as pd

from config import MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER, SYMBOL, TP, SL, LOT, SCALPING, DAY_TRADE
from strategy import generate_signal, calculate_atr
from trading import execute_trade
from utils import log_trade


def connect_mt5(account, password, server):
    if not mt5.initialize(login=account, server=server, password=password):
        print("Initialize failed, error code =", mt5.last_error())
        mt5.shutdown()
        return False

    if not mt5.login(account, password=password, server=server):
        print(f"Failed to connect at account #{account}, error code: {mt5.last_error()}")
        mt5.shutdown()
        return False
    print(mt5.account_info())
    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print(f"  {prop} = {account_info_dict[prop]}")
    return True

def fetch_data(symbol, timeframe, start, end):
    rates = mt5.copy_rates_range(symbol, timeframe, start, end)
    if rates is None or len(rates) == 0:
        print("No data retrieved.")
        return pd.DataFrame()

    rates_frame = pd.DataFrame(rates)
    if 'time' not in rates_frame.columns:
        print(f"Available columns in rates_frame: {rates_frame.columns}")
        raise KeyError("The 'time' column is missing in the data returned by mt5.copy_rates_range")

    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    return rates_frame

def main():
    # Connect to the account
    account = MT5_ACCOUNT
    password = MT5_PASSWORD
    server = MT5_SERVER
    if not connect_mt5(account, password, server):
        return

    start_time = datetime.datetime.now()
    last_execution_time = start_time
    while True:
        current_time = datetime.datetime.now()
        if (current_time - last_execution_time).seconds >= 600:
            utc_from = current_time - datetime.timedelta(days=5)
            utc_to = current_time
            rates_frame = fetch_data(SYMBOL, mt5.TIMEFRAME_M1, utc_from, utc_to)
            if rates_frame.empty:
                print("Skipping iteration due to no data.")
                time.sleep(1)
                continue

            atr = calculate_atr(rates_frame).iloc[-1]
            signal = generate_signal(rates_frame)
            result = execute_trade(signal, SYMBOL, LOT, atr)
            print(f"{current_time}: {result}")
            log_trade(signal, result)
            last_execution_time = current_time

        if (current_time - start_time).seconds >= 60:
            print(f"{current_time}: Program is still running and waiting for the next signal...")
            start_time = current_time
            time.sleep(1)

if __name__ == "__main__":
    # https://chatgpt.com/c/699ff565-d3d1-479a-adc6-f33b40bd8c9c
    main()

