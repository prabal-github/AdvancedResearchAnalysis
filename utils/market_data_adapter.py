"""
Market data provider adapter: centralize quote/history/download so we can swap yfinance with another API.

Usage:
    from utils.market_data_adapter import get_provider
    provider = get_provider()
    quote = provider.get_quote("TCS.NS")
    df = provider.get_history("TCS.NS", period="6mo")
    multi = provider.download(["TCS.NS","INFY.NS"], period="1y")

Switch provider:
    - Set env MARKET_DATA_PROVIDER=custom (default: yfinance)
    - Implement CustomProvider below using your API of choice (e.g., Alpha Vantage, Polygon).
"""
from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Any, Iterable, Optional

import pandas as pd

# Optional: yfinance as the default implementation
try:
    import yfinance as yf  # type: ignore
    YF_AVAILABLE = True
except Exception:
    YF_AVAILABLE = False

# Optional: Fyers API v3
try:
    from fyers_apiv3 import fyersModel  # type: ignore
    FYERS_AVAILABLE = True
except Exception:
    FYERS_AVAILABLE = False

def _now() -> float:
    return time.time()

@dataclass
class Quote:
    price: Optional[float]
    change: Optional[float]  # percentage
    volume: Optional[float]
    market_cap: Optional[float]
    pe_ratio: Optional[float]

class BaseProvider:
    def get_quote(self, symbol: str) -> dict:
        raise NotImplementedError

    def get_history(
        self,
        symbol: str,
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def download(
        self,
        symbols: Iterable[str] | str,
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

class YFinanceProvider(BaseProvider):
    def __init__(self) -> None:
        if not YF_AVAILABLE:
            raise RuntimeError("yfinance not available")

    def get_quote(self, symbol: str) -> dict:
        t = yf.Ticker(symbol)
        # Attempt to compute a self-consistent snapshot using history
        try:
            hist = t.history(period="1d")
            price = float(hist["Close"].iloc[-1]) if not hist.empty else None
        except Exception:
            price = None
        info = getattr(t, "info", {}) or {}
        prev_close = info.get("previousClose") or price
        try:
            change = ((price - prev_close) / prev_close * 100.0) if (price and prev_close) else None
        except Exception:
            change = None
        volume = None
        try:
            if not hist.empty:
                volume = float(hist["Volume"].iloc[-1])
        except Exception:
            volume = info.get("volume")
        return {
            "price": round(price, 2) if isinstance(price, (int, float)) else None,
            "change": round(change, 2) if isinstance(change, (int, float)) else None,
            "volume": volume,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
        }

    def get_history(self, symbol: str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        if period:
            return yf.Ticker(symbol).history(period=period)
        return yf.Ticker(symbol).history(start=start, end=end)

    def download(self, symbols: Iterable[str] | str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        if period:
            out = yf.download(symbols, period=period)
        else:
            out = yf.download(symbols, start=start, end=end)
        # Ensure we always return a DataFrame
        return out if isinstance(out, pd.DataFrame) else pd.DataFrame()

class CustomProvider(BaseProvider):
    """
    Template for integrating another market data API.
    Fill in HTTP calls using `requests` and map responses to the expected shapes.
    Consider using app-level `fetch_json_cached` for caching.
    """

    BASE_URL: str = os.getenv("CUSTOM_API_BASE_URL", "")

    def __init__(self) -> None:
        api_key = os.getenv("CUSTOM_API_KEY")
        if not self.BASE_URL:
            # You can still proceed if your API uses client libs or different base URLs
            pass
        self.api_key = api_key

    def get_quote(self, symbol: str) -> dict:
        # Example (pseudocode):
        # url = f"{self.BASE_URL}/quote?symbol={symbol}&apikey={self.api_key}"
        # data = fetch_json_cached(url, ttl_seconds=30)
        # Map fields accordingly:
        return {
            "price": None,
            "change": None,
            "volume": None,
            "market_cap": None,
            "pe_ratio": None,
        }

    def get_history(self, symbol: str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        # Example: construct URL with either period or start/end
        # Return a DataFrame with at least a DateTime index and Close/Volume columns
        return pd.DataFrame()

    def download(self, symbols: Iterable[str] | str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        # Example: batch/multi-symbol endpoint if available
        return pd.DataFrame()

class FyersProvider(BaseProvider):
    """Market data provider using Fyers API v3.

    Requires:
    - pip install fyers-apiv3
    - Env: FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN (or FYERS_TOKEN_PATH with JSON {"access_token": "..."})
    """

    def __init__(self) -> None:
        if not FYERS_AVAILABLE:
            raise RuntimeError("fyers-apiv3 not available. Run: pip install fyers-apiv3")
        self.client_id = os.getenv("FYERS_CLIENT_ID")
        self._access_token = os.getenv("FYERS_ACCESS_TOKEN")
        token_path = os.getenv("FYERS_TOKEN_PATH")
        if not self._access_token and token_path and os.path.exists(token_path):
            try:
                import json
                with open(token_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._access_token = data.get("access_token") or data.get("token")
            except Exception:
                pass
        if not self.client_id or not self._access_token:
            raise RuntimeError("FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN are required for FyersProvider")
        self._client = fyersModel.FyersModel(client_id=self.client_id, token=self._access_token, log_path=None)

    @staticmethod
    def _to_fyers_symbol(symbol: str) -> str:
        if ":" in symbol:
            return symbol
        s = symbol.upper()
        if s.endswith(".NS"):
            base = s[:-3]
            return f"NSE:{base}-EQ"
        if s.endswith(".BO"):
            base = s[:-3]
            return f"BSE:{base}"
        return f"NSE:{s}-EQ"

    def get_quote(self, symbol: str) -> dict:
        sym = self._to_fyers_symbol(symbol)
        try:
            res = self._client.quotes({"symbols": sym})
            data = None
            if isinstance(res, dict):
                arr = res.get("d") or res.get("data")
                if isinstance(arr, list) and arr:
                    data = arr[0]
            if not data:
                return {"price": None, "change": None, "volume": None, "market_cap": None, "pe_ratio": None}
            price = data.get("lp") or data.get("ltp")
            change = data.get("chp")
            volume = data.get("v") or data.get("volume")
            return {
                "price": round(price, 2) if isinstance(price, (int, float)) else price,
                "change": round(change, 2) if isinstance(change, (int, float)) else change,
                "volume": volume,
                "market_cap": None,
                "pe_ratio": None,
            }
        except Exception:
            return {"price": None, "change": None, "volume": None, "market_cap": None, "pe_ratio": None}

    def get_history(self, symbol: str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        from datetime import datetime, timedelta
        sym = self._to_fyers_symbol(symbol)
        if period and not (start or end):
            days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
            days = days_map.get(period, 365)
            _end = datetime.utcnow().date()
            _start = _end - timedelta(days=days)
        else:
            _start = datetime.strptime(start, "%Y-%m-%d").date() if start else (datetime.utcnow().date() - timedelta(days=365))
            _end = datetime.strptime(end, "%Y-%m-%d").date() if end else datetime.utcnow().date()
        payload = {
            "symbol": sym,
            "resolution": "D",
            "date_format": "1",
            "range_from": _start.strftime("%Y-%m-%d"),
            "range_to": _end.strftime("%Y-%m-%d"),
            "cont_flag": "1",
        }
        try:
            res = self._client.history(payload)
            candles = (res or {}).get("candles") or []
            if not candles:
                return pd.DataFrame()
            df = pd.DataFrame(candles, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])
            df["Date"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df.drop(columns=["timestamp"]).set_index("Date").sort_index()
            return df
        except Exception:
            return pd.DataFrame()

    def download(self, symbols: Iterable[str] | str, period: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        if isinstance(symbols, str):
            return self.get_history(symbols, period=period, start=start, end=end)
        frames = {}
        for s in symbols:
            df = self.get_history(s, period=period, start=start, end=end)
            if not df.empty and "Close" in df.columns:
                frames[s] = df["Close"].rename(s)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames.values(), axis=1)

def get_provider() -> BaseProvider:
    name = (os.getenv("MARKET_DATA_PROVIDER") or "yfinance").strip().lower()
    if name == "custom":
        return CustomProvider()
    if name == "fyers":
        return FyersProvider()
    return YFinanceProvider()
