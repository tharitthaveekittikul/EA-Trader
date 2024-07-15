import logging

logging.basicConfig(filename="trading-bot.log", level=logging.INFO)

def log_trade(action, result):
    logging.info(f"{action}: {result}")