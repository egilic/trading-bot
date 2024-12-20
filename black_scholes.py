import numpy as np
from scipy.stats import norm
import logging
from dataclasses import dataclass
from typing import Tuple, Literal
from math import log, sqrt, exp

# Set up logging
logging.basicConfig(filename='options_trading.log', level=logging.INFO,
                   format='%(asctime)s %(levelname)s %(message)s')

@dataclass
class OptionData:
    """Data structure for option parameters"""
    stock_price: float      # Current stock price (S₀)
    strike_price: float     # Strike price (K)
    time_to_expiry: float  # Time to expiration in years (T)
    risk_free_rate: float  # Risk-free interest rate (r)
    volatility: float      # Stock price volatility (σ)
    option_type: Literal['call', 'put']

class BlackScholes:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_d1_d2(self, data: OptionData) -> Tuple[float, float]:
        """Calculate d1 and d2 parameters for Black-Scholes formula"""
        try:
            d1 = (log(data.stock_price / data.strike_price) + 
                  (data.risk_free_rate + 0.5 * data.volatility ** 2) * data.time_to_expiry) / \
                 (data.volatility * sqrt(data.time_to_expiry))
            
            d2 = d1 - data.volatility * sqrt(data.time_to_expiry)
            return d1, d2
        except Exception as e:
            self.logger.error(f"Error calculating d1 and d2: {str(e)}")
            raise

    def calculate_option_price(self, data: OptionData) -> float:
        """Calculate theoretical option price using Black-Scholes model"""
        try:
            d1, d2 = self.calculate_d1_d2(data)
            
            if data.option_type == 'call':
                option_price = (data.stock_price * norm.cdf(d1) - 
                              data.strike_price * exp(-data.risk_free_rate * data.time_to_expiry) * 
                              norm.cdf(d2))
            else:  # put option
                option_price = (data.strike_price * exp(-data.risk_free_rate * data.time_to_expiry) * 
                              norm.cdf(-d2) - data.stock_price * norm.cdf(-d1))
            
            return option_price
        except Exception as e:
            self.logger.error(f"Error calculating option price: {str(e)}")
            raise

    def calculate_greeks(self, data: OptionData) -> dict:
        """Calculate option Greeks for risk management"""
        try:
            d1, d2 = self.calculate_d1_d2(data)
            
            # Delta
            if data.option_type == 'call':
                delta = norm.cdf(d1)
            else:
                delta = norm.cdf(d1) - 1

            # Gamma (same for calls and puts)
            gamma = norm.pdf(d1) / (data.stock_price * data.volatility * sqrt(data.time_to_expiry))

            # Theta
            theta_component = -(data.stock_price * norm.pdf(d1) * data.volatility) / \
                            (2 * sqrt(data.time_to_expiry))
            if data.option_type == 'call':
                theta = theta_component - data.risk_free_rate * data.strike_price * \
                       exp(-data.risk_free_rate * data.time_to_expiry) * norm.cdf(d2)
            else:
                theta = theta_component + data.risk_free_rate * data.strike_price * \
                       exp(-data.risk_free_rate * data.time_to_expiry) * norm.cdf(-d2)

            # Vega (same for calls and puts)
            vega = data.stock_price * sqrt(data.time_to_expiry) * norm.pdf(d1)

            return {
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega
            }
        except Exception as e:
            self.logger.error(f"Error calculating Greeks: {str(e)}")
            raise

class OptionsTrader:
    def __init__(self, threshold_percent: float = 0.05):
        """
        Initialize OptionsTrader with a threshold percentage for trading decisions
        threshold_percent: minimum difference between market and theoretical price to trigger trade
        """
        self.bs_model = BlackScholes()
        self.threshold_percent = threshold_percent
        self.logger = logging.getLogger(__name__)

    def analyze_opportunity(self, 
                          market_price: float, 
                          option_data: OptionData) -> Tuple[bool, str, float]:
        """
        Analyze if there's a trading opportunity based on market price vs theoretical price
        Returns: (should_trade, action, expected_profit)
        """
        try:
            # Calculate theoretical price
            theoretical_price = self.bs_model.calculate_option_price(option_data)
            
            # Calculate price difference percentage
            price_diff_percent = (market_price - theoretical_price) / theoretical_price
            
            # Get Greeks for risk assessment
            greeks = self.bs_model.calculate_greeks(option_data)
            
            # Log analysis
            self.logger.info(f"Analysis - Market Price: {market_price:.2f}, "
                           f"Theoretical Price: {theoretical_price:.2f}, "
                           f"Difference: {price_diff_percent:.2%}")
            self.logger.info(f"Greeks - Delta: {greeks['delta']:.4f}, "
                           f"Gamma: {greeks['gamma']:.4f}, "
                           f"Theta: {greeks['theta']:.4f}, "
                           f"Vega: {greeks['vega']:.4f}")

            # Decision logic
            if abs(price_diff_percent) > self.threshold_percent:
                if market_price < theoretical_price:
                    return True, "BUY", theoretical_price - market_price
                else:
                    return True, "SELL", market_price - theoretical_price
            
            return False, "HOLD", 0.0

        except Exception as e:
            self.logger.error(f"Error analyzing opportunity: {str(e)}")
            raise

def main():
    # Example usage
    trader = OptionsTrader(threshold_percent=0.05)
    
    # Sample option data (would come from API in production)
    option_data = OptionData(
        stock_price=100.0,      # Current stock price
        strike_price=100.0,     # Strike price
        time_to_expiry=0.5,     # 6 months
        risk_free_rate=0.05,    # 5% risk-free rate
        volatility=0.2,         # 20% volatility
        option_type='call'
    )
    
    # Sample market price (would come from API in production)
    market_price = 10.0
    
    try:
        should_trade, action, expected_profit = trader.analyze_opportunity(
            market_price, option_data
        )
        
        if should_trade:
            logging.info(f"Trading opportunity found! Action: {action}, "
                        f"Expected Profit: ${expected_profit:.2f}")
        else:
            logging.info("No trading opportunity found")
            
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
