
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EquityDataManager:
    """Unified data manager for yfinance and Fyers API"""
    
    def __init__(self):
        self.yf_symbols = {
            'RELIANCE.NS': 'NSE:RELIANCE',
            'TCS.NS': 'NSE:TCS',
            'INFY.NS': 'NSE:INFY',
            'HDFCBANK.NS': 'NSE:HDFCBANK',
            'ICICIBANK.NS': 'NSE:ICICIBANK',
            'BHARTIARTL.NS': 'NSE:BHARTIARTL',
            'ITC.NS': 'NSE:ITC',
            'KOTAKBANK.NS': 'NSE:KOTAKBANK',
            'LT.NS': 'NSE:LT',
            'ASIANPAINT.NS': 'NSE:ASIANPAINT'
            # Add more symbols as needed
        }
        
    def get_stock_data(self, symbol, period="1y", interval="1d"):
        """Get stock data with fallback mechanism"""
        try:
            # Try yfinance first
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                print(f"Success: Data fetched for {symbol} via yfinance")
                return self._process_data(data, symbol)
            else:
                print(f"Warning: No yfinance data for {symbol}, trying Fyers...")
                return self._get_fyers_data(symbol, period, interval)
                
        except Exception as e:
            print(f"Error: yfinance error for {symbol}: {e}")
            return self._get_fyers_data(symbol, period, interval)
    
    def _get_fyers_data(self, symbol, period, interval):
        """Fallback to Fyers API"""
        try:
            # Convert yfinance symbol to Fyers format
            fyers_symbol = self.yf_symbols.get(symbol, symbol)
            
            # TODO: Implement Fyers API integration
            # This would require Fyers API credentials and SDK
            print(f"Info: Fyers API integration for {fyers_symbol} - placeholder")
            
            # Return sample data structure for now
            dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
            sample_data = pd.DataFrame({
                'Open': np.random.normal(100, 10, 100),
                'High': np.random.normal(105, 10, 100),
                'Low': np.random.normal(95, 10, 100),
                'Close': np.random.normal(100, 10, 100),
                'Volume': np.random.randint(1000000, 10000000, 100)
            }, index=dates)
            
            return self._process_data(sample_data, symbol)
            
        except Exception as e:
            print(f"Error: Fyers API error for {symbol}: {e}")
            return None
    
    def _process_data(self, data, symbol):
        """Process and standardize data"""
        if data is None or data.empty:
            return None
            
        # Add technical indicators
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['RSI'] = self._calculate_rsi(data['Close'])
        data['MACD'] = self._calculate_macd(data['Close'])
        
        # Add metadata
        data.attrs['symbol'] = symbol
        data.attrs['last_updated'] = datetime.now()
        
        return data
    
    def _calculate_rsi(self, prices, window=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices, fast=12, slow=26):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        return ema_fast - ema_slow
    
    def get_multiple_stocks(self, symbols, period="6m"):
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            print(f"Info: Fetching data for {symbol}...")
            data = self.get_stock_data(symbol, period=period)
            if data is not None:
                results[symbol] = data
        return results

# Example usage
if __name__ == "__main__":
    manager = EquityDataManager()
    
    # Test with a few major stocks
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    data = manager.get_multiple_stocks(test_symbols)
    
    print(f"\nSuccess: Successfully fetched data for {len(data)} stocks")
    for symbol, df in data.items():
        if df is not None:
            print(f"   • {symbol}: {len(df)} days, Last Price: Rs{df['Close'].iloc[-1]:.2f}")
