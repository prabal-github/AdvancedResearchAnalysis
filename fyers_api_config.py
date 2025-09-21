"""
Fyers API Configuration and Integration System
Handles production data fetching from Fyers API for AWS EC2 deployment
"""

import os
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf  # Fallback for development

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FyersAPIConfig:
    """Configuration management for Fyers API"""
    
    def __init__(self):
        self.base_url = "https://api.fyers.in/data-rest/v2"
        self.is_production = self._detect_production_environment()
        self.config = self._load_config()
        
    def _detect_production_environment(self) -> bool:
        """Detect if running in production AWS EC2 environment"""
        # Check for EC2 metadata service
        try:
            response = requests.get(
                'http://169.254.169.254/latest/meta-data/instance-id',
                timeout=2
            )
            if response.status_code == 200:
                logger.info("🌐 Production AWS EC2 environment detected")
                return True
        except:
            pass
        
        # Check environment variables
        if os.getenv('AWS_EXECUTION_ENV') or os.getenv('DEPLOYMENT_ENV') == 'production':
            logger.info("🌐 Production environment detected via environment variables")
            return True
            
        logger.info("🧪 Development environment detected")
        return False
    
    def _load_config(self) -> Dict:
        """Load Fyers API configuration"""
        return {
            'app_id': os.getenv('FYERS_APP_ID'),
            'secret_key': os.getenv('FYERS_SECRET_KEY'),
            'access_token': os.getenv('FYERS_ACCESS_TOKEN'),
            'redirect_uri': os.getenv('FYERS_REDIRECT_URI', 'https://trade.fyers.in/api-login/redirect-to-app'),
            'enabled': os.getenv('FYERS_API_ENABLED', 'false').lower() == 'true'
        }
    
    def is_configured(self) -> bool:
        """Check if Fyers API is properly configured"""
        required_keys = ['app_id', 'secret_key', 'access_token']
        return all(self.config.get(key) for key in required_keys)
    
    def should_use_fyers(self) -> bool:
        """Determine if Fyers API should be used for data fetching"""
        return self.is_production and self.config.get('enabled', False) and self.is_configured()

class FyersDataService:
    """Service for fetching data from Fyers API"""
    
    def __init__(self, config: FyersAPIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f"Bearer {config.config.get('access_token', '')}",
            'Content-Type': 'application/json'
        })
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get real-time quotes for multiple symbols"""
        if not self.config.should_use_fyers():
            return self._get_yfinance_quotes(symbols)
        
        try:
            # Convert symbols to Fyers format (NSE:SYMBOL-EQ)
            fyers_symbols = [self._convert_to_fyers_symbol(symbol) for symbol in symbols]
            
            url = f"{self.config.base_url}/quotes"
            payload = {"symbols": fyers_symbols}
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get('s') == 'ok':
                return self._process_fyers_quotes(data.get('d', {}), symbols)
            else:
                logger.error(f"Fyers API error: {data.get('message', 'Unknown error')}")
                return self._get_yfinance_quotes(symbols)
                
        except Exception as e:
            logger.error(f"Error fetching Fyers quotes: {e}")
            return self._get_yfinance_quotes(symbols)
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Dict:
        """Get historical data for a symbol"""
        if not self.config.should_use_fyers():
            return self._get_yfinance_historical(symbol, period)
        
        try:
            fyers_symbol = self._convert_to_fyers_symbol(symbol)
            
            # Calculate date range
            end_date = datetime.now()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
                resolution = "1"
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
                resolution = "5"
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
                resolution = "D"
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
                resolution = "D"
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
                resolution = "D"
            else:  # 1y or default
                start_date = end_date - timedelta(days=365)
                resolution = "D"
            
            url = f"{self.config.base_url}/history"
            params = {
                "symbol": fyers_symbol,
                "resolution": resolution,
                "date_format": "1",
                "range_from": start_date.strftime("%Y-%m-%d"),
                "range_to": end_date.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('s') == 'ok':
                return self._process_fyers_historical(data.get('candles', []))
            else:
                logger.error(f"Fyers historical data error: {data.get('message', 'Unknown error')}")
                return self._get_yfinance_historical(symbol, period)
                
        except Exception as e:
            logger.error(f"Error fetching Fyers historical data: {e}")
            return self._get_yfinance_historical(symbol, period)
    
    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth/order book for a symbol"""
        if not self.config.should_use_fyers():
            return {"error": "Market depth not available in development mode"}
        
        try:
            fyers_symbol = self._convert_to_fyers_symbol(symbol)
            
            url = f"{self.config.base_url}/depth"
            params = {"symbol": fyers_symbol, "ohlcv_flag": "1"}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('s') == 'ok':
                return data.get('d', {})
            else:
                logger.error(f"Fyers market depth error: {data.get('message', 'Unknown error')}")
                return {"error": f"Fyers API error: {data.get('message', 'Unknown error')}"}
                
        except Exception as e:
            logger.error(f"Error fetching Fyers market depth: {e}")
            return {"error": str(e)}
    
    def _convert_to_fyers_symbol(self, symbol: str) -> str:
        """Convert symbol to Fyers format"""
        # Remove .NS suffix if present
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        return f"NSE:{clean_symbol}-EQ"
    
    def _process_fyers_quotes(self, fyers_data: Dict, original_symbols: List[str]) -> Dict[str, Dict]:
        """Process Fyers quotes response into standardized format"""
        result = {}
        
        for i, symbol in enumerate(original_symbols):
            fyers_symbol = self._convert_to_fyers_symbol(symbol)
            
            if fyers_symbol in fyers_data:
                quote_data = fyers_data[fyers_symbol]
                result[symbol] = {
                    'symbol': symbol,
                    'ltp': quote_data.get('lp', 0),
                    'open': quote_data.get('o', 0),
                    'high': quote_data.get('h', 0),
                    'low': quote_data.get('l', 0),
                    'close': quote_data.get('prev_close_price', 0),
                    'change': quote_data.get('ch', 0),
                    'change_percent': quote_data.get('chp', 0),
                    'volume': quote_data.get('v', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'fyers'
                }
            else:
                # Fallback to empty data
                result[symbol] = {
                    'symbol': symbol,
                    'ltp': 0,
                    'open': 0,
                    'high': 0,
                    'low': 0,
                    'close': 0,
                    'change': 0,
                    'change_percent': 0,
                    'volume': 0,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'fyers_fallback'
                }
        
        return result
    
    def _process_fyers_historical(self, candles: List) -> Dict:
        """Process Fyers historical data into standardized format"""
        if not candles:
            return {"error": "No historical data available"}
        
        processed_data = {
            'dates': [],
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': [],
            'source': 'fyers'
        }
        
        for candle in candles:
            if len(candle) >= 6:
                processed_data['dates'].append(datetime.fromtimestamp(candle[0]).strftime('%Y-%m-%d'))
                processed_data['open'].append(candle[1])
                processed_data['high'].append(candle[2])
                processed_data['low'].append(candle[3])
                processed_data['close'].append(candle[4])
                processed_data['volume'].append(candle[5])
        
        return processed_data
    
    def _get_yfinance_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fallback to YFinance for development/testing"""
        result = {}
        
        for symbol in symbols:
            try:
                # Add .NS suffix for Indian stocks if not present
                yf_symbol = symbol if symbol.endswith(('.NS', '.BO')) else f"{symbol}.NS"
                ticker = yf.Ticker(yf_symbol)
                info = ticker.history(period="2d")
                
                if not info.empty:
                    latest = info.iloc[-1]
                    prev = info.iloc[-2] if len(info) > 1 else latest
                    
                    result[symbol] = {
                        'symbol': symbol,
                        'ltp': float(latest['Close']),
                        'open': float(latest['Open']),
                        'high': float(latest['High']),
                        'low': float(latest['Low']),
                        'close': float(prev['Close']),
                        'change': float(latest['Close'] - prev['Close']),
                        'change_percent': float((latest['Close'] - prev['Close']) / prev['Close'] * 100),
                        'volume': int(latest['Volume']),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'yfinance'
                    }
                else:
                    result[symbol] = self._get_empty_quote(symbol, 'yfinance_empty')
                    
            except Exception as e:
                logger.error(f"YFinance error for {symbol}: {e}")
                result[symbol] = self._get_empty_quote(symbol, 'yfinance_error')
        
        return result
    
    def _get_yfinance_historical(self, symbol: str, period: str) -> Dict:
        """Fallback to YFinance for historical data"""
        try:
            yf_symbol = symbol if symbol.endswith(('.NS', '.BO')) else f"{symbol}.NS"
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                return {
                    'dates': [date.strftime('%Y-%m-%d') for date in hist.index],
                    'open': hist['Open'].tolist(),
                    'high': hist['High'].tolist(),
                    'low': hist['Low'].tolist(),
                    'close': hist['Close'].tolist(),
                    'volume': hist['Volume'].tolist(),
                    'source': 'yfinance'
                }
            else:
                return {"error": "No historical data available"}
                
        except Exception as e:
            logger.error(f"YFinance historical error for {symbol}: {e}")
            return {"error": str(e)}
    
    def _get_empty_quote(self, symbol: str, source: str) -> Dict:
        """Return empty quote structure"""
        return {
            'symbol': symbol,
            'ltp': 0,
            'open': 0,
            'high': 0,
            'low': 0,
            'close': 0,
            'change': 0,
            'change_percent': 0,
            'volume': 0,
            'timestamp': datetime.now().isoformat(),
            'source': source
        }

# Global instances
fyers_config = FyersAPIConfig()
fyers_data_service = FyersDataService(fyers_config)

def get_data_service() -> FyersDataService:
    """Get the global Fyers data service instance"""
    return fyers_data_service

def is_production_mode() -> bool:
    """Check if running in production mode with Fyers API"""
    return fyers_config.should_use_fyers()