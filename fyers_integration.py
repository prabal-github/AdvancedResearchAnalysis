"""
Fyers API Integration Helper
Provisions for future Fyers API key integration
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

class FyersAPIHelper:
    """Helper class for Fyers API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('FYERS_API_KEY')
        self.access_token = os.getenv('FYERS_ACCESS_TOKEN')
        self.client_id = os.getenv('FYERS_CLIENT_ID')
        self.is_configured = bool(self.api_key and self.access_token)
        
        if not self.is_configured:
            logging.info("Fyers API not configured. Using yfinance as primary data source.")
    
    def is_api_available(self) -> bool:
        """Check if Fyers API is available and configured"""
        return self.is_configured
    
    def get_market_data(self, symbol: str, timeframe: str = '1D', days: int = 30) -> Optional[Dict]:
        """
        Get market data from Fyers API
        
        Args:
            symbol: Fyers symbol (e.g., 'NSE:RELIANCE-EQ')
            timeframe: Data timeframe ('1m', '5m', '15m', '1H', '1D')
            days: Number of days of historical data
            
        Returns:
            Dictionary with OHLCV data or None if not available
        """
        if not self.is_configured:
            logging.warning("Fyers API not configured. Cannot fetch market data.")
            return None
        
        try:
            # TODO: Implement actual Fyers API call when API key is available
            # Example implementation:
            # from fyers_apiv3 import fyersModel
            # fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.access_token)
            # 
            # data = {
            #     "symbol": symbol,
            #     "resolution": timeframe,
            #     "date_format": "1",
            #     "range_from": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            #     "range_to": datetime.now().strftime('%Y-%m-%d'),
            #     "cont_flag": "1"
            # }
            # 
            # response = fyers.history(data=data)
            # return response
            
            logging.info(f"Fyers API call would be made for {symbol} with {timeframe} timeframe")
            return None
            
        except Exception as e:
            logging.error(f"Error fetching Fyers data for {symbol}: {e}")
            return None
    
    def get_nifty50_symbols(self) -> List[str]:
        """Get Fyers format symbols for NIFTY 50 stocks"""
        from nifty50_stocks import NIFTY_50_STOCKS
        
        fyers_symbols = []
        for yf_symbol, data in NIFTY_50_STOCKS.items():
            fyers_symbols.append(data['fyers'])
        
        return fyers_symbols
    
    def convert_yfinance_to_fyers(self, yf_symbol: str) -> Optional[str]:
        """Convert yfinance symbol to Fyers format"""
        try:
            from nifty50_stocks import NIFTY_50_STOCKS
            if yf_symbol in NIFTY_50_STOCKS:
                return NIFTY_50_STOCKS[yf_symbol]['fyers']
        except ImportError:
            pass
        
        # Fallback conversion logic
        if yf_symbol.endswith('.NS'):
            base_symbol = yf_symbol.replace('.NS', '')
            return f"NSE:{base_symbol}"
        
        return None
    
    def get_live_quotes(self, symbols: List[str]) -> Optional[Dict]:
        """
        Get live quotes for multiple symbols
        
        Args:
            symbols: List of Fyers symbols
            
        Returns:
            Dictionary with live quote data
        """
        if not self.is_configured:
            logging.warning("Fyers API not configured. Cannot fetch live quotes.")
            return None
        
        try:
            # TODO: Implement actual Fyers API call
            # from fyers_apiv3 import fyersModel
            # fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.access_token)
            # 
            # data = {
            #     "symbols": ",".join(symbols),
            #     "ohlcv_flag": "1"
            # }
            # 
            # response = fyers.quotes(data=data)
            # return response
            
            logging.info(f"Fyers live quotes would be fetched for {len(symbols)} symbols")
            return None
            
        except Exception as e:
            logging.error(f"Error fetching Fyers live quotes: {e}")
            return None
    
    def place_order(self, symbol: str, qty: int, side: str, type: str = "MARKET") -> Optional[Dict]:
        """
        Place order through Fyers API (for future implementation)
        
        Args:
            symbol: Fyers symbol
            qty: Quantity
            side: 1 for BUY, -1 for SELL
            type: Order type (MARKET, LIMIT, etc.)
            
        Returns:
            Order response dictionary
        """
        if not self.is_configured:
            logging.warning("Fyers API not configured. Cannot place orders.")
            return None
        
        logging.info(f"Order placement provision: {side} {qty} shares of {symbol}")
        
        # TODO: Implement actual order placement when API is configured
        # This is just a placeholder for future implementation
        return {
            'status': 'simulated',
            'message': 'Order placement provision ready for Fyers API integration',
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type
        }
    
    def get_portfolio(self) -> Optional[Dict]:
        """Get portfolio holdings from Fyers"""
        if not self.is_configured:
            return None
        
        # TODO: Implement portfolio fetching
        logging.info("Portfolio fetch provision ready for Fyers API")
        return None
    
    def get_funds(self) -> Optional[Dict]:
        """Get available funds from Fyers"""
        if not self.is_configured:
            return None
        
        # TODO: Implement funds fetching
        logging.info("Funds fetch provision ready for Fyers API")
        return None

# Global instance for easy access
fyers_helper = FyersAPIHelper()

def get_enhanced_market_data(yf_symbol: str, use_fyers: bool = True) -> Dict:
    """
    Get enhanced market data using both yfinance and Fyers (when available)
    
    Args:
        yf_symbol: yfinance symbol (e.g., 'RELIANCE.NS')
        use_fyers: Whether to try Fyers API first
        
    Returns:
        Dictionary with enhanced market data
    """
    result = {
        'symbol': yf_symbol,
        'source': 'yfinance',
        'data': None,
        'fyers_available': fyers_helper.is_api_available()
    }
    
    # Try Fyers API first if configured and requested
    if use_fyers and fyers_helper.is_api_available():
        fyers_symbol = fyers_helper.convert_yfinance_to_fyers(yf_symbol)
        if fyers_symbol:
            fyers_data = fyers_helper.get_market_data(fyers_symbol)
            if fyers_data:
                result['source'] = 'fyers'
                result['data'] = fyers_data
                return result
    
    # Fallback to yfinance
    try:
        import yfinance as yf
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period='30d')
        
        if not data.empty:
            result['data'] = {
                'current_price': float(data['Close'].iloc[-1]),
                'volume': int(data['Volume'].iloc[-1]) if 'Volume' in data else 0,
                'high': float(data['High'].iloc[-1]),
                'low': float(data['Low'].iloc[-1]),
                'open': float(data['Open'].iloc[-1]),
                'prev_close': float(data['Close'].iloc[-2]) if len(data) > 1 else float(data['Close'].iloc[-1]),
                'change_pct': ((float(data['Close'].iloc[-1]) - float(data['Close'].iloc[-2])) / float(data['Close'].iloc[-2]) * 100) if len(data) > 1 else 0
            }
    
    except Exception as e:
        logging.error(f"Error fetching data for {yf_symbol}: {e}")
        result['error'] = str(e)
    
    return result

def setup_fyers_api(api_key: str, access_token: str, client_id: str) -> bool:
    """
    Setup Fyers API credentials (to be called when user provides API key)
    
    Args:
        api_key: Fyers API key
        access_token: Fyers access token
        client_id: Fyers client ID
        
    Returns:
        True if setup successful
    """
    try:
        os.environ['FYERS_API_KEY'] = api_key
        os.environ['FYERS_ACCESS_TOKEN'] = access_token
        os.environ['FYERS_CLIENT_ID'] = client_id
        
        # Reinitialize the helper
        global fyers_helper
        fyers_helper = FyersAPIHelper()
        
        logging.info("Fyers API credentials configured successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error setting up Fyers API: {e}")
        return False
