from ta.momentum import RSIIndicator
from ta.trend import MACD
import pandas as pd

from config import BUY_ACTION, SELL_ACTION, HOLD_ACTION, SCALPING, SWING_TRADE, DAY_TRADE


def generate_signal(rates_frame):
    macd = MACD(close=rates_frame['close'])
    rates_frame['macd'] = macd.macd()
    rates_frame['macd_signal'] = macd.macd_signal()
    rates_frame['macd_diff'] = macd.macd_diff()

    # Calculate RSI
    rsi = RSIIndicator(close=rates_frame['close'], window=14)
    rates_frame['rsi'] = rsi.rsi()

    # Generate signals
    if rates_frame['macd'].iloc[-1] > rates_frame['macd_signal'].iloc[-1] and rates_frame['rsi'].iloc[-1] < 70:
        return BUY_ACTION
    elif rates_frame['macd'].iloc[-1] < rates_frame['macd_signal'].iloc[-1] and rates_frame['rsi'].iloc[-1] > 30:
        return SELL_ACTION
    return HOLD_ACTION

def calculate_atr(data, period = 14):
    # Average True Range
    data['H-L'] = data['high'] - data['low']
    data['H-PC'] = abs(data['high'] - data['close'].shift(1))
    data['L-PC'] = abs(data['low'] - data['close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    return data['ATR']

def determine_trade_type(sl, tp, atr):
    if sl <= 1.5 * atr and tp <= 3 * atr:
        print("Scalping")
        return SCALPING
    elif sl <= 3 * atr and tp <= 6 * atr:
        print("Day Trade")
        return DAY_TRADE
    else:
        print("Swing Trade")
        return SWING_TRADE