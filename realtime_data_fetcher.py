"""
Real-time Stock Symbol Mapping and Data Fetcher
Integrates Fyers API with YFinance fallback
Enhanced with Top 100 stocks support
"""

import pandas as pd
import yfinance as yf
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import os

class StockSymbolMapper:
    """Maps between Fyers symbols and Yahoo Finance symbols"""
    
    def __init__(self, mapping_file_path: Optional[str] = None):
        self.mapping_df = None
        self.fyers_to_yf = {}
        self.yf_to_fyers = {}
        
        # Load mapping from CSV if provided
        if mapping_file_path and os.path.exists(mapping_file_path):
            self.load_mapping_from_csv(mapping_file_path)
        else:
            # Create enhanced mapping for top 100 stocks
            self._create_enhanced_mapping()
    
    def _create_enhanced_mapping(self):
        """Create enhanced mapping for top 100 Indian stocks"""
        # Import the enhanced mapping
        try:
            from top100_stocks_mapping import ENHANCED_FYERS_YFINANCE_MAPPING
            
            # Convert to DataFrame format
            enhanced_mapping = []
            for yf_symbol, data in ENHANCED_FYERS_YFINANCE_MAPPING.items():
                enhanced_mapping.append({
                    'fyers_symbol': data['fyers'],
                    'yfinance_symbol': yf_symbol,
                    'name': data['name']
                })
            
            self.mapping_df = pd.DataFrame(enhanced_mapping)
            self._build_mapping_dicts()
            
        except ImportError:
            # Fallback to original default mapping if import fails
            self._create_original_default_mapping()
    
    def _create_original_default_mapping(self):
        """Create default mapping for common Indian stocks (fallback)"""
        default_mapping = [
            {'fyers_symbol': 'NSE:RELIANCE-EQ', 'yfinance_symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Ltd'},
            {'fyers_symbol': 'NSE:TCS-EQ', 'yfinance_symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Ltd'},
            {'fyers_symbol': 'NSE:HDFCBANK-EQ', 'yfinance_symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Ltd'},
            {'fyers_symbol': 'NSE:INFY-EQ', 'yfinance_symbol': 'INFY.NS', 'name': 'Infosys Ltd'},
            {'fyers_symbol': 'NSE:HINDUNILVR-EQ', 'yfinance_symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Ltd'},
            {'fyers_symbol': 'NSE:ICICIBANK-EQ', 'yfinance_symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Ltd'},
            {'fyers_symbol': 'NSE:KOTAKBANK-EQ', 'yfinance_symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Ltd'},
            {'fyers_symbol': 'NSE:BHARTIARTL-EQ', 'yfinance_symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Ltd'},
            {'fyers_symbol': 'NSE:ITC-EQ', 'yfinance_symbol': 'ITC.NS', 'name': 'ITC Ltd'},
            {'fyers_symbol': 'NSE:SBIN-EQ', 'yfinance_symbol': 'SBIN.NS', 'name': 'State Bank of India'},
            {'fyers_symbol': 'NSE:LT-EQ', 'yfinance_symbol': 'LT.NS', 'name': 'Larsen & Toubro Ltd'},
            {'fyers_symbol': 'NSE:HCLTECH-EQ', 'yfinance_symbol': 'HCLTECH.NS', 'name': 'HCL Technologies Ltd'},
            {'fyers_symbol': 'NSE:ASIANPAINT-EQ', 'yfinance_symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints Ltd'},
            {'fyers_symbol': 'NSE:AXISBANK-EQ', 'yfinance_symbol': 'AXISBANK.NS', 'name': 'Axis Bank Ltd'},
            {'fyers_symbol': 'NSE:MARUTI-EQ', 'yfinance_symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki India Ltd'},
            {'fyers_symbol': 'NSE:SUNPHARMA-EQ', 'yfinance_symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical Industries Ltd'},
            {'fyers_symbol': 'NSE:ULTRACEMCO-EQ', 'yfinance_symbol': 'ULTRACEMCO.NS', 'name': 'UltraTech Cement Ltd'},
            {'fyers_symbol': 'NSE:BAJFINANCE-EQ', 'yfinance_symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance Ltd'},
            {'fyers_symbol': 'NSE:NESTLEIND-EQ', 'yfinance_symbol': 'NESTLEIND.NS', 'name': 'Nestle India Ltd'},
            {'fyers_symbol': 'NSE:BAJAJFINSV-EQ', 'yfinance_symbol': 'BAJAJFINSV.NS', 'name': 'Bajaj Finserv Ltd'},
            {'fyers_symbol': 'NSE:WIPRO-EQ', 'yfinance_symbol': 'WIPRO.NS', 'name': 'Wipro Ltd'},
            {'fyers_symbol': 'NSE:ONGC-EQ', 'yfinance_symbol': 'ONGC.NS', 'name': 'Oil & Natural Gas Corporation Ltd'},
            {'fyers_symbol': 'NSE:TATASTEEL-EQ', 'yfinance_symbol': 'TATASTEEL.NS', 'name': 'Tata Steel Ltd'},
            {'fyers_symbol': 'NSE:TECHM-EQ', 'yfinance_symbol': 'TECHM.NS', 'name': 'Tech Mahindra Ltd'},
            {'fyers_symbol': 'NSE:NTPC-EQ', 'yfinance_symbol': 'NTPC.NS', 'name': 'NTPC Ltd'},
            {'fyers_symbol': 'NSE:POWERGRID-EQ', 'yfinance_symbol': 'POWERGRID.NS', 'name': 'Power Grid Corporation of India Ltd'},
            {'fyers_symbol': 'NSE:TITAN-EQ', 'yfinance_symbol': 'TITAN.NS', 'name': 'Titan Company Ltd'},
            {'fyers_symbol': 'NSE:DIVISLAB-EQ', 'yfinance_symbol': 'DIVISLAB.NS', 'name': 'Divi\'s Laboratories Ltd'},
            {'fyers_symbol': 'NSE:INDUSINDBK-EQ', 'yfinance_symbol': 'INDUSINDBK.NS', 'name': 'IndusInd Bank Ltd'},
            {'fyers_symbol': 'NSE:COALINDIA-EQ', 'yfinance_symbol': 'COALINDIA.NS', 'name': 'Coal India Ltd'},
            {'fyers_symbol': 'NSE:JSWSTEEL-EQ', 'yfinance_symbol': 'JSWSTEEL.NS', 'name': 'JSW Steel Ltd'},
            {'fyers_symbol': 'NSE:TATAMOTORS-EQ', 'yfinance_symbol': 'TATAMOTORS.NS', 'name': 'Tata Motors Ltd'},
            {'fyers_symbol': 'NSE:GRASIM-EQ', 'yfinance_symbol': 'GRASIM.NS', 'name': 'Grasim Industries Ltd'},
            {'fyers_symbol': 'NSE:BRITANNIA-EQ', 'yfinance_symbol': 'BRITANNIA.NS', 'name': 'Britannia Industries Ltd'},
            {'fyers_symbol': 'NSE:DRREDDY-EQ', 'yfinance_symbol': 'DRREDDY.NS', 'name': 'Dr. Reddy\'s Laboratories Ltd'},
            {'fyers_symbol': 'NSE:HINDALCO-EQ', 'yfinance_symbol': 'HINDALCO.NS', 'name': 'Hindalco Industries Ltd'},
            {'fyers_symbol': 'NSE:BPCL-EQ', 'yfinance_symbol': 'BPCL.NS', 'name': 'Bharat Petroleum Corporation Ltd'},
            {'fyers_symbol': 'NSE:EICHERMOT-EQ', 'yfinance_symbol': 'EICHERMOT.NS', 'name': 'Eicher Motors Ltd'},
            {'fyers_symbol': 'NSE:HEROMOTOCO-EQ', 'yfinance_symbol': 'HEROMOTOCO.NS', 'name': 'Hero MotoCorp Ltd'},
            {'fyers_symbol': 'NSE:CIPLA-EQ', 'yfinance_symbol': 'CIPLA.NS', 'name': 'Cipla Ltd'},
            {'fyers_symbol': 'NSE:UPL-EQ', 'yfinance_symbol': 'UPL.NS', 'name': 'UPL Ltd'},
            {'fyers_symbol': 'NSE:ADANIPORTS-EQ', 'yfinance_symbol': 'ADANIPORTS.NS', 'name': 'Adani Ports and Special Economic Zone Ltd'},
            {'fyers_symbol': 'NSE:TRENT-EQ', 'yfinance_symbol': 'TRENT.NS', 'name': 'Trent Ltd'},
            {'fyers_symbol': 'NSE:IOC-EQ', 'yfinance_symbol': 'IOC.NS', 'name': 'Indian Oil Corporation Ltd'},
            {'fyers_symbol': 'NSE:SBILIFE-EQ', 'yfinance_symbol': 'SBILIFE.NS', 'name': 'SBI Life Insurance Company Ltd'},
            {'fyers_symbol': 'NSE:LTIM-EQ', 'yfinance_symbol': 'LTIM.NS', 'name': 'LTIMindtree Ltd'},
            {'fyers_symbol': 'NSE:APOLLOHOSP-EQ', 'yfinance_symbol': 'APOLLOHOSP.NS', 'name': 'Apollo Hospitals Enterprise Ltd'},
            {'fyers_symbol': 'NSE:SHRIRAMFIN-EQ', 'yfinance_symbol': 'SHRIRAMFIN.NS', 'name': 'Shriram Finance Ltd'},
            {'fyers_symbol': 'NSE:VEDL-EQ', 'yfinance_symbol': 'VEDL.NS', 'name': 'Vedanta Ltd'},
            {'fyers_symbol': 'NSE:BAJAJ-AUTO-EQ', 'yfinance_symbol': 'BAJAJ-AUTO.NS', 'name': 'Bajaj Auto Ltd'},
            {'fyers_symbol': 'NSE:TATACONSUM-EQ', 'yfinance_symbol': 'TATACONSUM.NS', 'name': 'Tata Consumer Products Ltd'},
            {'fyers_symbol': 'NSE:ADANIENT-EQ', 'yfinance_symbol': 'ADANIENT.NS', 'name': 'Adani Enterprises Ltd'}
        ]
        
        self.mapping_df = pd.DataFrame(default_mapping)
        self._build_mapping_dicts()
    
    def load_mapping_from_csv(self, file_path: str):
        """Load symbol mapping from CSV file"""
        try:
            self.mapping_df = pd.read_csv(file_path)
            # Ensure required columns exist
            required_cols = ['fyers_symbol', 'yfinance_symbol', 'name']
            if not all(col in self.mapping_df.columns for col in required_cols):
                logging.warning(f"CSV file missing required columns. Using enhanced mapping.")
                self._create_enhanced_mapping()
                return
            
            self._build_mapping_dicts()
            logging.info(f"Loaded {len(self.mapping_df)} symbol mappings from {file_path}")
            
        except Exception as e:
            logging.error(f"Error loading mapping from {file_path}: {e}")
            self._create_enhanced_mapping()
    
    def _build_mapping_dicts(self):
        """Build bidirectional mapping dictionaries"""
        if self.mapping_df is not None:
            self.fyers_to_yf = dict(zip(self.mapping_df['fyers_symbol'], self.mapping_df['yfinance_symbol']))
            self.yf_to_fyers = dict(zip(self.mapping_df['yfinance_symbol'], self.mapping_df['fyers_symbol']))
    
    def get_yfinance_symbol(self, fyers_symbol: str) -> Optional[str]:
        """Convert Fyers symbol to Yahoo Finance symbol"""
        return self.fyers_to_yf.get(fyers_symbol)
    
    def get_fyers_symbol(self, yf_symbol: str) -> Optional[str]:
        """Convert Yahoo Finance symbol to Fyers symbol"""
        return self.yf_to_fyers.get(yf_symbol)
    
    def get_all_symbols(self) -> List[Dict[str, str]]:
        """Get all available symbols with mapping"""
        if self.mapping_df is not None:
            return self.mapping_df.to_dict('records')
        return []


class RealTimeDataFetcher:
    """Fetch real-time market data using Fyers API with YFinance fallback"""
    
    def __init__(self, fyers_api_key: Optional[str] = None, fyers_access_token: Optional[str] = None):
        self.fyers_api_key = fyers_api_key
        self.fyers_access_token = fyers_access_token
        self.symbol_mapper = StockSymbolMapper()
        
        # Initialize Fyers client if credentials available
        self.fyers_client = None
        if fyers_api_key and fyers_access_token:
            self._init_fyers_client()
    
    def _init_fyers_client(self):
        """Initialize Fyers API client"""
        try:
            # Import Fyers API library if available
            from fyers_apiv3 import fyersModel
            self.fyers_client = fyersModel.FyersModel(
                client_id=self.fyers_api_key,
                token=self.fyers_access_token,
                log_path=""
            )
            logging.info("Fyers API client initialized successfully")
        except ImportError:
            logging.warning("Fyers API library not installed. Using YFinance only.")
        except Exception as e:
            logging.error(f"Error initializing Fyers client: {e}")
    
    def get_top_100_stocks(self) -> List[str]:
        """Get the list of top 100 stocks for ML model processing"""
        try:
            from top100_stocks_mapping import TOP_100_STOCKS
            return TOP_100_STOCKS
        except ImportError:
            # Return a subset if import fails
            return [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                'ICICIBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS',
                'ASIANPAINT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'ULTRACEMCO.NS'
            ]
    
    def is_ml_model_symbol(self, symbol: str) -> bool:
        """Check if symbol should be processed by ML models (top 100 only)"""
        try:
            from top100_stocks_mapping import is_symbol_supported
            return is_symbol_supported(symbol)
        except ImportError:
            return symbol in self.get_top_100_stocks()
    
    def get_real_time_price(self, symbol: str, prefer_fyers: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get real-time price data for a symbol
        
        Args:
            symbol: Stock symbol (can be Fyers or YFinance format)
            prefer_fyers: Whether to try Fyers API first
            
        Returns:
            Dictionary with price data or None
        """
        if prefer_fyers and self.fyers_client:
            # Try Fyers API first
            fyers_symbol = symbol if symbol.startswith('NSE:') else self.symbol_mapper.get_fyers_symbol(symbol)
            if fyers_symbol:
                data = self._get_fyers_price(fyers_symbol)
                if data:
                    return data
        
        # Fallback to YFinance
        yf_symbol = symbol if not symbol.startswith('NSE:') else self.symbol_mapper.get_yfinance_symbol(symbol)
        if yf_symbol:
            return self._get_yfinance_price(yf_symbol)
        
        return None
    
    def _get_fyers_price(self, fyers_symbol: str) -> Optional[Dict[str, Any]]:
        """Get price data from Fyers API"""
        try:
            if not self.fyers_client:
                return None
            
            # Get current quote
            data = {"symbols": fyers_symbol}
            response = self.fyers_client.quotes(data)
            
            if response['code'] == 200 and response['d']:
                quote_data = response['d'][0]['v']
                return {
                    'symbol': fyers_symbol,
                    'current_price': quote_data.get('lp', 0),  # Last price
                    'open_price': quote_data.get('o', 0),
                    'high_price': quote_data.get('h', 0),
                    'low_price': quote_data.get('l', 0),
                    'previous_close': quote_data.get('prev_close_price', 0),
                    'change': quote_data.get('ch', 0),
                    'change_percent': quote_data.get('chp', 0),
                    'volume': quote_data.get('volume', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'fyers'
                }
        except Exception as e:
            logging.error(f"Error fetching Fyers data for {fyers_symbol}: {e}")
        
        return None
    
    def _get_yfinance_price(self, yf_symbol: str) -> Optional[Dict[str, Any]]:
        """Get price data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            current_data = hist.iloc[-1]
            previous_data = hist.iloc[-2] if len(hist) > 1 else current_data
            
            current_price = current_data['Close']
            previous_close = previous_data['Close']
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                'symbol': yf_symbol,
                'current_price': round(current_price, 2),
                'open_price': round(current_data['Open'], 2),
                'high_price': round(current_data['High'], 2),
                'low_price': round(current_data['Low'], 2),
                'previous_close': round(previous_close, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(current_data['Volume']),
                'timestamp': datetime.now().isoformat(),
                'source': 'yfinance'
            }
        except Exception as e:
            logging.error(f"Error fetching YFinance data for {yf_symbol}: {e}")
        
        return None
    
    def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data for analysis"""
        yf_symbol = symbol if not symbol.startswith('NSE:') else self.symbol_mapper.get_yfinance_symbol(symbol)
        if not yf_symbol:
            return None
        
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period, interval=interval)
            return hist
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def test_fyers_connection(self) -> Dict[str, Any]:
        """Test Fyers API connection"""
        if not self.fyers_client:
            return {
                'success': False,
                'message': 'Fyers client not initialized',
                'error': 'Missing API credentials'
            }
        
        try:
            # Test with a simple symbol
            test_symbol = "NSE:RELIANCE-EQ"
            data = {"symbols": test_symbol}
            response = self.fyers_client.quotes(data)
            
            if response['code'] == 200:
                return {
                    'success': True,
                    'message': 'Fyers API connection successful',
                    'test_symbol': test_symbol,
                    'response_code': response['code']
                }
            else:
                return {
                    'success': False,
                    'message': 'Fyers API connection failed',
                    'error': response.get('message', 'Unknown error'),
                    'response_code': response['code']
                }
        except Exception as e:
            return {
                'success': False,
                'message': 'Fyers API test failed',
                'error': str(e)
            }


# Global instance
real_time_fetcher = RealTimeDataFetcher()
