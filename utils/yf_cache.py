import time
import threading
import yfinance as yf
from typing import Any, Dict, Tuple, Optional, List

# Simple in-process TTL cache for yfinance calls to cut API usage 5–20x.
# Not persistent across restarts; thread-safe enough for simple Flask app.

_lock = threading.Lock()
_store: Dict[str, Tuple[float, Any]] = {}

def _get(key: str) -> Optional[Any]:
    now = time.time()
    with _lock:
        item = _store.get(key)
        if not item:
            return None
        exp, val = item
        if now > exp:
            _store.pop(key, None)
            return None
        return val

def _set(key: str, val: Any, ttl: int):
    with _lock:
        _store[key] = (time.time() + max(1, int(ttl)), val)

# High-level helpers

def ticker_history(symbol: str, period: str = '6mo', ttl: int = 900):
    key = f"hist::{symbol}::{period}"
    cached = _get(key)
    if cached is not None:
        return cached
    data = yf.Ticker(symbol).history(period=period)
    _set(key, data, ttl)
    return data

def download(symbols: List[str] | str, start=None, end=None, ttl: int = 900):
    # Normalize symbols list for key stability
    syms = symbols if isinstance(symbols, list) else [symbols]
    key = f"dl::{','.join(sorted(syms))}::{start}::{end}"
    cached = _get(key)
    if cached is not None:
        return cached
    data = yf.download(symbols, start=start, end=end)
    _set(key, data, ttl)
    return data
