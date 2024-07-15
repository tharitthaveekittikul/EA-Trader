# trading.py

import MetaTrader5 as mt5

from config import BUY_ACTION, SELL_ACTION, SCALPING, DAY_TRADE, SWING_TRADE
from strategy import determine_trade_type

TRADING_STYLES = {
    SCALPING: {"sl_factor": 1, "tp_factor": 2},
    DAY_TRADE: {"sl_factor": 2, "tp_factor": 4},
    SWING_TRADE: {"sl_factor": 3, "tp_factor": 4},
}


def is_valid_volume(symbol, volume):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return False

    min_volume = symbol_info.volume_min
    max_volume = symbol_info.volume_max
    volume_step = symbol_info.volume_step

    if volume < min_volume or volume > max_volume or (volume % volume_step != 0):
        print(f"Volume {volume} is not valid for {symbol}. Min: {min_volume}, Max: {max_volume}, Step: {volume_step}")
        return False

    return True


def get_valid_stops(symbol, price, atr, is_buy):
    symbol_info = mt5.symbol_info(symbol)
    min_distance = symbol_info.trade_stops_level * symbol_info.point
    if min_distance == 0:
        # TODO: Must update this minimum distance of should adjust myself following SYMBOL
        # Set a default minimum distance if broker doesn't provide one
        min_distance = 1000 * symbol_info.point

    sl_pips = atr * 1.5  # Initial guess for SL based on ATR
    tp_pips = atr * 3  # Initial guess for TP based on ATR
    trade_type = determine_trade_type(sl_pips, tp_pips, atr)

    sl_pips = TRADING_STYLES[trade_type]['sl_factor'] * atr
    tp_pips = TRADING_STYLES[trade_type]['tp_factor'] * atr

    if is_buy:
        sl = price - sl_pips * symbol_info.point
        tp = price + tp_pips * symbol_info.point
        if (price - sl) < min_distance:
            sl = price - min_distance
        if (tp - price) < min_distance:
            tp = price + min_distance
    else:
        sl = price + sl_pips * symbol_info.point
        tp = price - tp_pips * symbol_info.point
        if (sl - price) < min_distance:
            sl = price + min_distance
        if (price - tp) < min_distance:
            tp = price - min_distance

    print(f"Price: {price}, SL: {sl}, TP: {tp}, Min Distance: {min_distance}")
    return sl, tp


def buy(symbol, lot, atr):
    if not is_valid_volume(symbol, lot):
        return
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return

    price = mt5.symbol_info_tick(symbol).ask
    sl, tp = get_valid_stops(symbol, price, atr, is_buy=True)
    if sl is None or tp is None:
        print("Invalid SL/TP levels")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    print(f"Buy Order: {symbol}, SL: {sl}, TP: {tp}, Price: {price}")  # Added debug information
    return result


def sell(symbol, lot, atr):
    if not is_valid_volume(symbol, lot):
        return
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return

    price = mt5.symbol_info_tick(symbol).bid
    sl, tp = get_valid_stops(symbol, price, atr, is_buy=False)
    if sl is None or tp is None:
        print("Invalid SL/TP levels")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    print(f"Sell Order: {symbol}, SL: {sl}, TP: {tp}, Price: {price}")  # Added debug information
    return result


def execute_trade(signal, symbol, lot, atr):
    if signal == BUY_ACTION:
        result = buy(symbol, lot, atr)
    elif signal == SELL_ACTION:
        result = sell(symbol, lot, atr)
    else:
        result = None
    return result
