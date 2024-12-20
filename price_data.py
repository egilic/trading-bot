import sqlite3
from datetime import datetime, timedelta
import logging
from typing import List, Tuple
import requests
from dataclasses import dataclass

# Set up logging
logging.basicConfig(filename='trading.log', level=logging.INFO,
                   format='%(asctime)s %(levelname)s %(message)s')

@dataclass
class PriceData:
    timestamp: datetime
    price: float

class PriceDataManager:
    def __init__(self, db_path: str, api_key: str):
        """
        Initialize price data manager
        db_path: Path to SQLite database
        api_key: API key for real-time price data
        """
        self.db_path = db_path
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.setup_database()

    def setup_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS historical_prices (
                        timestamp DATETIME PRIMARY KEY,
                        symbol TEXT,
                        price REAL
                    )
                ''')
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database setup error: {str(e)}")
            raise

    def get_historical_prices(self, symbol: str, weeks: int) -> List[PriceData]:
        """
        Get historical weekly prices from database
        symbol: Trading symbol
        weeks: Number of weeks of historical data to retrieve
        """
        try:
            start_date = datetime.now() - timedelta(weeks=weeks)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, price
                    FROM historical_prices
                    WHERE symbol = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (symbol, start_date))
                
                results = cursor.fetchall()
                return [
                    PriceData(
                        timestamp=datetime.strptime(ts, '%Y-%m-%d %H:%M:%S'),
                        price=price
                    )
                    for ts, price in results
                ]
        except Exception as e:
            self.logger.error(f"Error fetching historical prices: {str(e)}")
            raise

    def get_real_time_price(self, symbol: str) -> float:
        """
        Get real-time price from API
        symbol: Trading symbol
        """
        try:
            # Replace with actual API endpoint
            api_url = f"https://api.example.com/v1/prices/{symbol}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            current_price = float(data['price'])
            
            self.logger.info(f"Retrieved real-time price for {symbol}: {current_price}")
            return current_price
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            raise
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error parsing API response: {str(e)}")
            raise

    def calculate_weekly_ma(self, symbol: str, weeks: int = 5) -> Tuple[float, float]:
        """
        Calculate weekly moving average and get current price
        Returns: (moving_average, current_price)
        """
        try:
            # Get historical weekly prices
            historical_data = self.get_historical_prices(symbol, weeks)
            
            if len(historical_data) < weeks:
                raise ValueError(f"Insufficient historical data. Need {weeks} weeks, have {len(historical_data)}")
            
            # Calculate MA from historical prices
            ma = sum(data.price for data in historical_data[:weeks]) / weeks
            
            # Get current price
            current_price = self.get_real_time_price(symbol)
            
            self.logger.info(f"{symbol} - MA: {ma:.2f}, Current: {current_price:.2f}")
            return ma, current_price
            
        except Exception as e:
            self.logger.error(f"Error calculating MA: {str(e)}")
            raise

def main():
    # Example usage (for testing)
    try:
        price_manager = PriceDataManager(
            db_path="prices.db",
            api_key="your_api_key_here"
        )
        
        symbol = "AAPL"  # Example symbol
        ma, current_price = price_manager.calculate_weekly_ma(symbol)
        
        logging.info(f"5-week MA: {ma:.2f}")
        logging.info(f"Current Price: {current_price:.2f}")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
