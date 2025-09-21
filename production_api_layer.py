"""
Production API Integration Layer
===============================

Robust API layer that seamlessly integrates yfinance (development) and Fyers API (production)
with enhanced error handling, caching, rate limiting, and fallback mechanisms.

Author: GitHub Copilot
Date: September 2025
"""

import asyncio
import aiohttp
import time
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from functools import wraps
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA PROVIDER ENUMS AND CONFIGURATIONS
# =============================================================================

class DataProvider(Enum):
    YFINANCE = "yfinance"
    FYERS = "fyers"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    QUANDL = "quandl"

class DataType(Enum):
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    INTRADAY = "intraday"
    FUNDAMENTALS = "fundamentals"
    NEWS = "news"
    OPTIONS = "options"

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class APICredentials:
    """API credentials for different providers"""
    provider: DataProvider
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    app_id: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    timeout: int = 30  # seconds

@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    price: float
    change: float
    change_pct: float
    volume: int
    high: float
    low: float
    open_price: float
    timestamp: datetime
    provider: DataProvider
    exchange: Optional[str] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    market_cap: Optional[float] = None

# =============================================================================
# RATE LIMITING AND CACHING
# =============================================================================

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate_limit: int = 60, time_window: int = 60):
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.tokens = rate_limit
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from the bucket"""
        with self.lock:
            now = time.time()
            
            # Refill tokens based on time elapsed
            elapsed = now - self.last_refill
            if elapsed > 0:
                tokens_to_add = int(elapsed * (self.rate_limit / self.time_window))
                self.tokens = min(self.rate_limit, self.tokens + tokens_to_add)
                self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Calculate wait time until next token is available"""
        with self.lock:
            if self.tokens > 0:
                return 0
            
            return self.time_window / self.rate_limit

class DataCache:
    """Thread-safe data cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """Get cached data if not expired"""
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check if expired
            ttl = ttl or self.default_ttl
            if time.time() - self.timestamps[key] > ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set cached data with timestamp"""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get cache size"""
        with self.lock:
            return len(self.cache)

# =============================================================================
# BASE DATA PROVIDER INTERFACE
# =============================================================================

class BaseDataProvider:
    """Base class for all data providers"""
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.rate_limiter = RateLimiter(credentials.rate_limit)
        self.cache = DataCache()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.credentials.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _make_cache_key(self, symbol: str, data_type: DataType, **kwargs) -> str:
        """Generate cache key"""
        key_parts = [symbol, data_type.value, self.credentials.provider.value]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)
    
    async def get_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Get real-time market data"""
        raise NotImplementedError
    
    async def get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime, interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical market data"""
        raise NotImplementedError
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get real-time data for multiple symbols"""
        results = {}
        for symbol in symbols:
            try:
                data = await self.get_real_time_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
        return results

# =============================================================================
# YFINANCE DATA PROVIDER
# =============================================================================

class YFinanceProvider(BaseDataProvider):
    """YFinance data provider implementation"""
    
    def __init__(self, credentials: APICredentials = None):
        if credentials is None:
            credentials = APICredentials(
                provider=DataProvider.YFINANCE,
                rate_limit=2000,  # YFinance is quite generous
                timeout=30
            )
        super().__init__(credentials)
    
    async def get_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Get real-time data from YFinance"""
        cache_key = self._make_cache_key(symbol, DataType.REAL_TIME)
        
        # Check cache first
        cached_data = self.cache.get(cache_key, ttl=60)  # 1-minute cache
        if cached_data:
            return cached_data
        
        # Rate limiting
        if not self.rate_limiter.acquire():
            logger.warning(f"Rate limit hit for YFinance: {symbol}")
            return None
        
        try:
            # Import yfinance dynamically
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            data = MarketData(
                symbol=symbol,
                price=float(info.get('regularMarketPrice', 0)),
                change=float(info.get('regularMarketChange', 0)),
                change_pct=float(info.get('regularMarketChangePercent', 0)),
                volume=int(info.get('regularMarketVolume', 0)),
                high=float(info.get('dayHigh', 0)),
                low=float(info.get('dayLow', 0)),
                open_price=float(info.get('regularMarketOpen', 0)),
                timestamp=datetime.now(),
                provider=DataProvider.YFINANCE,
                market_cap=info.get('marketCap')
            )
            
            # Cache the result
            self.cache.set(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"YFinance fetch error for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime, interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data from YFinance"""
        cache_key = self._make_cache_key(symbol, DataType.HISTORICAL, 
                                       start=start_date.date(), end=end_date.date(), interval=interval)
        
        # Check cache (longer TTL for historical data)
        cached_data = self.cache.get(cache_key, ttl=3600)  # 1-hour cache
        if cached_data is not None:
            return cached_data
        
        if not self.rate_limiter.acquire():
            logger.warning(f"Rate limit hit for YFinance historical: {symbol}")
            return None
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date.date(),
                end=end_date.date(),
                interval=interval,
                auto_adjust=True,
                prepost=True,
                threads=True
            )
            
            if data.empty:
                return None
            
            # Standardize column names
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data['symbol'] = symbol
            data['provider'] = DataProvider.YFINANCE.value
            
            # Cache the result
            self.cache.set(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"YFinance historical fetch error for {symbol}: {e}")
            return None

# =============================================================================
# FYERS DATA PROVIDER
# =============================================================================

class FyersProvider(BaseDataProvider):
    """Fyers API data provider implementation"""
    
    def __init__(self, credentials: APICredentials):
        super().__init__(credentials)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Fyers client"""
        try:
            from fyers_apiv3 import fyersModel
            
            self.client = fyersModel.FyersModel(
                client_id=self.credentials.app_id,
                token=self.credentials.access_token,
                log_path=os.getcwd()
            )
            logger.info("Fyers client initialized successfully")
            
        except ImportError:
            logger.error("Fyers API not available - install fyers-apiv3")
            self.client = None
        except Exception as e:
            logger.error(f"Fyers client initialization failed: {e}")
            self.client = None
    
    async def get_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Get real-time data from Fyers"""
        if not self.client:
            return None
        
        cache_key = self._make_cache_key(symbol, DataType.REAL_TIME)
        
        # Check cache
        cached_data = self.cache.get(cache_key, ttl=30)  # 30-second cache
        if cached_data:
            return cached_data
        
        if not self.rate_limiter.acquire():
            logger.warning(f"Rate limit hit for Fyers: {symbol}")
            return None
        
        try:
            # Fyers symbol format: NSE:SYMBOL-EQ
            fyers_symbol = self._convert_to_fyers_symbol(symbol)
            
            response = self.client.quotes({"symbols": fyers_symbol})
            
            if response.get('code') != 200 or 'd' not in response:
                return None
            
            quote_data = response['d'][0]
            
            data = MarketData(
                symbol=symbol,
                price=float(quote_data.get('lp', 0)),
                change=float(quote_data.get('ch', 0)),
                change_pct=float(quote_data.get('chp', 0)),
                volume=int(quote_data.get('v', 0)),
                high=float(quote_data.get('h', 0)),
                low=float(quote_data.get('l', 0)),
                open_price=float(quote_data.get('o', 0)),
                timestamp=datetime.now(),
                provider=DataProvider.FYERS,
                exchange="NSE",
                bid=quote_data.get('bid'),
                ask=quote_data.get('ask')
            )
            
            self.cache.set(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Fyers fetch error for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime, interval: str = "1D") -> Optional[pd.DataFrame]:
        """Get historical data from Fyers"""
        if not self.client:
            return None
        
        cache_key = self._make_cache_key(symbol, DataType.HISTORICAL, 
                                       start=start_date.date(), end=end_date.date(), interval=interval)
        
        cached_data = self.cache.get(cache_key, ttl=3600)
        if cached_data is not None:
            return cached_data
        
        if not self.rate_limiter.acquire():
            logger.warning(f"Rate limit hit for Fyers historical: {symbol}")
            return None
        
        try:
            fyers_symbol = self._convert_to_fyers_symbol(symbol)
            
            data = {
                "symbol": fyers_symbol,
                "resolution": interval,
                "date_format": "1",
                "range_from": start_date.strftime("%Y-%m-%d"),
                "range_to": end_date.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }
            
            response = self.client.history(data)
            
            if response.get('code') != 200 or 'candles' not in response:
                return None
            
            candles = response['candles']
            if not candles:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df['symbol'] = symbol
            df['provider'] = DataProvider.FYERS.value
            
            self.cache.set(cache_key, df)
            return df
            
        except Exception as e:
            logger.error(f"Fyers historical fetch error for {symbol}: {e}")
            return None
    
    def _convert_to_fyers_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Fyers format"""
        # Simple conversion - in production, use comprehensive mapping
        if ':' in symbol:
            return symbol  # Already in Fyers format
        return f"NSE:{symbol}-EQ"

# =============================================================================
# UNIFIED DATA MANAGER
# =============================================================================

class UnifiedDataManager:
    """Unified data manager that handles multiple providers with intelligent fallback"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.providers = {}
        self.provider_priority = []
        self.circuit_breakers = {}
        self.performance_metrics = defaultdict(lambda: {'success': 0, 'failures': 0, 'avg_latency': 0})
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize data providers based on environment"""
        if self.environment == Environment.PRODUCTION:
            # Production: Fyers primary, YFinance fallback
            fyers_creds = self._get_fyers_credentials()
            if fyers_creds:
                self.providers[DataProvider.FYERS] = FyersProvider(fyers_creds)
                self.provider_priority.append(DataProvider.FYERS)
            
            yf_creds = APICredentials(provider=DataProvider.YFINANCE)
            self.providers[DataProvider.YFINANCE] = YFinanceProvider(yf_creds)
            self.provider_priority.append(DataProvider.YFINANCE)
            
        else:
            # Development: YFinance primary, Fyers fallback (if available)
            yf_creds = APICredentials(provider=DataProvider.YFINANCE)
            self.providers[DataProvider.YFINANCE] = YFinanceProvider(yf_creds)
            self.provider_priority.append(DataProvider.YFINANCE)
            
            fyers_creds = self._get_fyers_credentials()
            if fyers_creds:
                self.providers[DataProvider.FYERS] = FyersProvider(fyers_creds)
                self.provider_priority.append(DataProvider.FYERS)
        
        # Initialize circuit breakers
        for provider in self.providers.keys():
            self.circuit_breakers[provider] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=300  # 5 minutes
            )
    
    def _get_fyers_credentials(self) -> Optional[APICredentials]:
        """Get Fyers credentials from environment"""
        app_id = os.environ.get('FYERS_APP_ID')
        access_token = os.environ.get('FYERS_ACCESS_TOKEN')
        
        if app_id and access_token:
            return APICredentials(
                provider=DataProvider.FYERS,
                app_id=app_id,
                access_token=access_token,
                rate_limit=100,  # Fyers rate limit
                timeout=30
            )
        return None
    
    async def get_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Get real-time data with provider fallback"""
        for provider_type in self.provider_priority:
            provider = self.providers.get(provider_type)
            circuit_breaker = self.circuit_breakers.get(provider_type)
            
            if not provider or not circuit_breaker.can_execute():
                continue
            
            try:
                start_time = time.time()
                
                async with provider:
                    data = await provider.get_real_time_data(symbol)
                
                latency = time.time() - start_time
                
                if data:
                    # Record success
                    self._record_success(provider_type, latency)
                    circuit_breaker.record_success()
                    return data
                
            except Exception as e:
                # Record failure
                self._record_failure(provider_type)
                circuit_breaker.record_failure()
                logger.warning(f"Provider {provider_type.value} failed for {symbol}: {e}")
                continue
        
        logger.error(f"All providers failed for symbol: {symbol}")
        return None
    
    async def get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime, interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data with provider fallback"""
        for provider_type in self.provider_priority:
            provider = self.providers.get(provider_type)
            circuit_breaker = self.circuit_breakers.get(provider_type)
            
            if not provider or not circuit_breaker.can_execute():
                continue
            
            try:
                start_time = time.time()
                
                async with provider:
                    data = await provider.get_historical_data(symbol, start_date, end_date, interval)
                
                latency = time.time() - start_time
                
                if data is not None and not data.empty:
                    self._record_success(provider_type, latency)
                    circuit_breaker.record_success()
                    return data
                
            except Exception as e:
                self._record_failure(provider_type)
                circuit_breaker.record_failure()
                logger.warning(f"Provider {provider_type.value} failed for historical {symbol}: {e}")
                continue
        
        logger.error(f"All providers failed for historical data: {symbol}")
        return None
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get multiple quotes efficiently"""
        results = {}
        
        # Try batch operations first (if supported by provider)
        for provider_type in self.provider_priority:
            provider = self.providers.get(provider_type)
            circuit_breaker = self.circuit_breakers.get(provider_type)
            
            if not provider or not circuit_breaker.can_execute():
                continue
            
            try:
                remaining_symbols = [s for s in symbols if s not in results]
                if not remaining_symbols:
                    break
                
                async with provider:
                    batch_results = await provider.get_multiple_quotes(remaining_symbols)
                
                results.update(batch_results)
                
                if batch_results:
                    circuit_breaker.record_success()
                
            except Exception as e:
                circuit_breaker.record_failure()
                logger.warning(f"Batch fetch failed for {provider_type.value}: {e}")
                continue
        
        return results
    
    def _record_success(self, provider: DataProvider, latency: float):
        """Record successful API call"""
        metrics = self.performance_metrics[provider]
        metrics['success'] += 1
        
        # Update average latency
        total_calls = metrics['success'] + metrics['failures']
        metrics['avg_latency'] = ((metrics['avg_latency'] * (total_calls - 1)) + latency) / total_calls
    
    def _record_failure(self, provider: DataProvider):
        """Record failed API call"""
        self.performance_metrics[provider]['failures'] += 1
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for all providers"""
        metrics = {}
        
        for provider, stats in self.performance_metrics.items():
            total_calls = stats['success'] + stats['failures']
            success_rate = (stats['success'] / total_calls * 100) if total_calls > 0 else 0
            
            metrics[provider.value] = {
                'success_rate': round(success_rate, 2),
                'total_calls': total_calls,
                'avg_latency_ms': round(stats['avg_latency'] * 1000, 2),
                'circuit_breaker_state': self.circuit_breakers[provider].state.value
            }
        
        return metrics

# =============================================================================
# CIRCUIT BREAKER PATTERN
# =============================================================================

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for API resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            
            # HALF_OPEN state
            return True
    
    def record_success(self):
        """Record successful execution"""
        with self.lock:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self):
        """Record failed execution"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout

# =============================================================================
# PRODUCTION READY API LAYER
# =============================================================================

class ProductionAPILayer:
    """Production-ready API layer with comprehensive features"""
    
    def __init__(self, environment: Environment = None):
        # Auto-detect environment if not specified
        if environment is None:
            environment = self._detect_environment()
        
        self.environment = environment
        self.data_manager = UnifiedDataManager(environment)
        self.symbol_mapper = self._initialize_symbol_mapper()
        
        logger.info(f"Initialized ProductionAPILayer for {environment.value} environment")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        # Check for AWS metadata service
        try:
            import requests
            response = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=1)
            if response.status_code == 200:
                return Environment.PRODUCTION
        except:
            pass
        
        # Check environment variables
        env_name = os.environ.get('ENVIRONMENT', '').lower()
        if env_name in ['production', 'prod']:
            return Environment.PRODUCTION
        elif env_name in ['staging', 'stage']:
            return Environment.STAGING
        
        return Environment.DEVELOPMENT
    
    def _initialize_symbol_mapper(self):
        """Initialize symbol mapper for cross-provider compatibility"""
        # In production, this would load from a comprehensive mapping database
        mapping = {}
        
        # Load from CSV if available
        try:
            import csv
            csv_file = 'fyers_yfinance_mapping.csv'
            if os.path.exists(csv_file):
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        fyers_symbol = row['fyers_symbol']
                        yfinance_symbol = row['yfinance_symbol']
                        name = row['name']
                        
                        mapping[yfinance_symbol] = {
                            'fyers': fyers_symbol,
                            'yfinance': yfinance_symbol,
                            'name': name
                        }
        except Exception as e:
            logger.warning(f"Could not load symbol mapping: {e}")
        
        return mapping
    
    async def get_market_data(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """Get market data with automatic provider selection"""
        try:
            # Map symbol for current environment
            mapped_symbol = self._map_symbol_for_environment(symbol)
            
            data = await self.data_manager.get_real_time_data(mapped_symbol)
            
            if data:
                return {
                    'symbol': symbol,
                    'original_symbol': mapped_symbol,
                    'price': data.price,
                    'change': data.change,
                    'change_pct': data.change_pct,
                    'volume': data.volume,
                    'high': data.high,
                    'low': data.low,
                    'open': data.open_price,
                    'timestamp': data.timestamp.isoformat(),
                    'provider': data.provider.value,
                    'exchange': data.exchange,
                    'market_cap': data.market_cap
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
    
    async def get_historical_data(self, symbol: str, days: int = 30, 
                                interval: str = "1d") -> Optional[Dict]:
        """Get historical data with automatic provider selection"""
        try:
            mapped_symbol = self._map_symbol_for_environment(symbol)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = await self.data_manager.get_historical_data(
                mapped_symbol, start_date, end_date, interval
            )
            
            if data is not None and not data.empty:
                # Convert to JSON-serializable format
                result = {
                    'symbol': symbol,
                    'original_symbol': mapped_symbol,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'interval': interval,
                    'data': data.to_dict('records'),
                    'provider': data['provider'].iloc[0] if 'provider' in data.columns else 'unknown'
                }
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    async def get_portfolio_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get market data for multiple symbols efficiently"""
        try:
            # Map all symbols for current environment
            mapped_symbols = [self._map_symbol_for_environment(s) for s in symbols]
            
            # Create mapping back to original symbols
            reverse_mapping = {mapped: original for original, mapped in zip(symbols, mapped_symbols)}
            
            # Fetch data for all symbols
            results = await self.data_manager.get_multiple_quotes(mapped_symbols)
            
            # Convert to standard format
            portfolio_data = {}
            for mapped_symbol, data in results.items():
                original_symbol = reverse_mapping.get(mapped_symbol, mapped_symbol)
                
                portfolio_data[original_symbol] = {
                    'price': data.price,
                    'change': data.change,
                    'change_pct': data.change_pct,
                    'volume': data.volume,
                    'high': data.high,
                    'low': data.low,
                    'open': data.open_price,
                    'timestamp': data.timestamp.isoformat(),
                    'provider': data.provider.value
                }
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error fetching portfolio data: {e}")
            return {}
    
    def _map_symbol_for_environment(self, symbol: str) -> str:
        """Map symbol based on current environment"""
        symbol = symbol.strip().upper()
        
        if symbol not in self.symbol_mapper:
            return symbol
        
        mapping = self.symbol_mapper[symbol]
        
        if self.environment == Environment.PRODUCTION:
            return mapping.get('fyers', symbol)
        else:
            return mapping.get('yfinance', symbol)
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health metrics"""
        return {
            'environment': self.environment.value,
            'providers': list(self.data_manager.providers.keys()),
            'provider_priority': [p.value for p in self.data_manager.provider_priority],
            'performance_metrics': self.data_manager.get_performance_metrics(),
            'cache_stats': {
                provider: provider_instance.cache.size() 
                for provider, provider_instance in self.data_manager.providers.items()
            },
            'symbol_mappings_loaded': len(self.symbol_mapper),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
production_api = ProductionAPILayer()

def get_production_api() -> ProductionAPILayer:
    """Get the global production API instance"""
    return production_api

# Export main classes and functions
__all__ = [
    'ProductionAPILayer',
    'UnifiedDataManager',
    'DataProvider',
    'Environment',
    'MarketData',
    'get_production_api'
]