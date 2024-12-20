from price_data import PriceDataManager
from exchange import ExchangeAPI
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import time

# Set up logging
logging.basicConfig(filename='trading.log', level=logging.INFO,
                   format='%(asctime)s %(levelname)s %(message)s')

@dataclass
class Position:
    """Track current trading position"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime

class MAStrategy:
    def __init__(self, 
                 symbol: str,
                 db_path: str,
                 api_key: str,
                 position_size: float = 1.0,
                 ma_weeks: int = 5,
                 buy_threshold: float = 0.95,  # 5% below MA
                 sell_threshold: float = 1.40): # 40% above MA
        """
        Initialize MA Strategy
        symbol: Trading symbol
        db_path: Path to price database
        api_key: API key for real-time data
        position_size: Size of each position
        ma_weeks: Number of weeks for MA calculation
        buy_threshold: Price must be this fraction of MA to trigger buy
        sell_threshold: Price must be this fraction of MA to trigger sell
        """
        self.symbol = symbol
        self.position_size = position_size
        self.ma_weeks = ma_weeks
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        
        self.price_manager = PriceDataManager(db_path, api_key)
        self.exchange = ExchangeAPI()
        self.current_position: Optional[Position] = None
        self.logger = logging.getLogger(__name__)

    def check_buy_signal(self, current_price: float, ma: float) -> bool:
        """Check if current price triggers a buy signal"""
        buy_price = ma * self.buy_threshold
        should_buy = current_price < buy_price
        
        if should_buy:
            self.logger.info(f"Buy signal: Price {current_price:.2f} < {buy_price:.2f} "
                           f"({self.buy_threshold:.2%} of MA {ma:.2f})")
        
        return should_buy

    def check_sell_signal(self, current_price: float, ma: float) -> bool:
        """Check if current price triggers a sell signal"""
        sell_price = ma * self.sell_threshold
        should_sell = current_price > sell_price
        
        if should_sell:
            self.logger.info(f"Sell signal: Price {current_price:.2f} > {sell_price:.2f} "
                           f"({self.sell_threshold:.2%} of MA {ma:.2f})")
        
        return should_sell

    def execute_buy(self, price: float) -> None:
        """Execute buy order"""
        try:
            self.exchange.buy(self.symbol, self.position_size)
            self.current_position = Position(
                symbol=self.symbol,
                entry_price=price,
                quantity=self.position_size,
                entry_time=datetime.now()
            )
            self.logger.info(f"Executed BUY: {self.position_size} {self.symbol} at {price:.2f}")
        except Exception as e:
            self.logger.error(f"Buy execution error: {str(e)}")
            raise

    def execute_sell(self, price: float) -> None:
        """Execute sell order"""
        try:
            self.exchange.sell(self.symbol, self.position_size)
            
            if self.current_position:
                hold_time = datetime.now() - self.current_position.entry_time
                profit = (price - self.current_position.entry_price) * self.position_size
                roi = (price / self.current_position.entry_price - 1) * 100
                
                self.logger.info(
                    f"Executed SELL: {self.position_size} {self.symbol} at {price:.2f}\n"
                    f"Hold Time: {hold_time}\n"
                    f"Profit: ${profit:.2f}\n"
                    f"ROI: {roi:.2f}%"
                )
            
            self.current_position = None
            
        except Exception as e:
            self.logger.error(f"Sell execution error: {str(e)}")
            raise

    def check_and_trade(self) -> None:
        """Check signals and execute trades if needed"""
        try:
            # Get current MA and price
            ma, current_price = self.price_manager.calculate_weekly_ma(
                self.symbol, self.ma_weeks
            )
            
            # Check signals and execute trades
            if not self.current_position and self.check_buy_signal(current_price, ma):
                self.execute_buy(current_price)
                
            elif self.current_position and self.check_sell_signal(current_price, ma):
                self.execute_sell(current_price)
                
            else:
                self.logger.info(f"No action taken. Price: {current_price:.2f}, MA: {ma:.2f}")
                
        except Exception as e:
            self.logger.error(f"Trading error: {str(e)}")
            raise

def main():
    # Example usage
    try:
        strategy = MAStrategy(
            symbol="BTC/USD",
            db_path="prices.db",
            api_key="your_api_key_here",
            position_size=1.0
        )
        
        # Run one iteration of the strategy
        strategy.check_and_trade()
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
