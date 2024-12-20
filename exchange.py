import time
import logging
from typing import Tuple
import os
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Load environment variables from .env 
load_dotenv()

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
paper = True

trading_stream_client = TradingStream(api_key=api_key, secret_key=secret_key, paper=paper)

async def trade_updates_handler(data):
    print(data)

trading_stream_client.subscribe_trade_updates(trade_updates_handler)
trading_stream_client.run()

# Set up logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

class ExchangeAPI:
    def __init__(self):
        # TODO: add api keys
        pass

    def get_price(self, symbol: str) -> float:
        """
        Fetch the current price (mid-price, last traded price, etc.) for the given symbol.
        Return a float or raise an exception if data is unavailable.
        """
        # TODO: Implement API call to exchange and return current price
        pass

    def buy(self, symbol: str, amount: float):
        """
        Place a buy order on this exchange.
        """
        # TODO: Implement buy order logic
        pass

    def sell(self, symbol: str, amount: float):
        """
        Place a sell order on this exchange.
        """
        # TODO: Implement sell order logic
        pass

def detect_arbitrage(price_a: float, price_b: float, threshold: float = 0.5) -> Tuple[bool, float]:
    """
    Check for arbitrage opportunities.
    Returns a tuple (arbitrage_found, profit_per_unit).
    """
    # Simple logic: If Exchange A is cheaper than Exchange B by 'threshold', buy on A and sell on B.
    if price_b - price_a > threshold:
        return True, (price_b - price_a)
    return False, 0.0

def main():
    # Config
    symbol = ""
    amount = 0 

    # Initialize your exchange APIs with keys

    # Main loop
    while True:
        # Fetch prices
        price_a = 0
        price_b = 0

        # Check for arbitrage (e.g., buy on A, sell on B)
        arb_found, profit_per_unit = detect_arbitrage(price_a, price_b, threshold=0.5)
        if arb_found:
            logging.info(f"Arbitrage found! Buy at {price_a}, Sell at {price_b}, Profit: {profit_per_unit * amount} per unit.")
            # Execute trades via API calls
        else:
            logging.info("No arbitrage opportunity found.")

        # Sleep before next iteration
        time.sleep(5)

if __name__ == "__main__":
    main()
