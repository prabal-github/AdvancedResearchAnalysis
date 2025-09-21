# API README

This document summarizes all external APIs used by the application and explains how to integrate another market data API in place of yfinance.

## External APIs overview

Stock data and finance
- yfinance (library)
  - Used for quotes and historical data via `yf.Ticker(...).info` and `.history(...)`, and `yf.download(...)`.
  - Responses: pandas DataFrames (OHLCV) and dict-like `info`.
  - Caching: global `requests_cache` (15m) + `utils/yf_cache.py` (TTL wrappers) + in-memory price snapshots.
- Upstox News (HTTP GET)
  - Endpoint: https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=500
  - Response: `{ data: [{ title, description, ... }] }`.
  - Cached with `fetch_json_cached(..., ttl=600)`.
- Upstox Options Strategy Chain (HTTP GET)
  - Endpoint: https://service.upstox.com/option-analytics-tool/open/v1/strategy-chains
  - Params: `assetKey`, `strategyChainType`, `expiry`.
  - Response fields used: `success`, `data.strategyChainData.strikeMap`.
- Sensibull Current Events (HTTP GET)
  - Endpoint: https://api.sensibull.com/v1/current_events
  - Response fields used: `status`, `data.global[]` with `{ title, geography, event_date, event_time, impact, ... }`.
- MFAPI (Mutual Funds, India)
  - List: https://api.mfapi.in/mf
  - Scheme detail: https://api.mfapi.in/mf/{scheme_code}
  - Latest NAV: https://api.mfapi.in/mf/{scheme_code}/latest

Other services
- Attestr PAN verification (HTTP POST)
  - Endpoint: https://api.attestr.com/api/v2/public/checkx/pan
  - Body: `{ "pan": "ABCDE1234F" }`, Header: `Authorization: Basic <token>`.
- Razorpay (SDK + Webhook)
  - Orders: SDK (`client.order.create`). Verify HMAC in-app. Webhook: POST `/api/payments/webhook`.
- AWS SES (SDK, optional)
  - `ses.send_email(...)` for password reset/notifications.
- AI (optional)
  - Anthropic/OpenAI scaffolding present; used only when keys/packages configured.

## Replace yfinance with another market data API

Introduce a provider adapter to centralize quote/history/download so the rest of the app remains unchanged.

### Minimal provider contract
- get_quote(symbol) -> dict with keys: `price`, `change` (percent), `volume`, `market_cap`, `pe_ratio`.
- get_history(symbol, period=None, start=None, end=None) -> pandas DataFrame (must include `Close`, ideally `Volume`).
- download(symbols, start=None, end=None, period=None) -> pandas DataFrame similar to `yf.download`.

### Steps
1) Create a provider module
- See `utils/market_data_adapter.py` (added) for YFinanceProvider and a CustomProvider placeholder.

2) Configure your new provider
- Set env var to switch provider (PowerShell):
  - `$env:MARKET_DATA_PROVIDER = "custom"`
  - Add API keys: `setx ALPHAVANTAGE_API_KEY "your_key"` (example).

3) Implement the provider
- Map the new API’s endpoints to the contract above; normalize symbols and timezones as needed.

4) Add caching and limits
- Wrap HTTP with `fetch_json_cached` or rely on `requests_cache`. Respect rate limits and add backoff.

5) Migrate call sites incrementally
- Replace direct `yf.Ticker(...).info/history` with `provider.get_quote/get_history`.
- Replace `yf.download` with `provider.download`.
- Grep helpers: `yf\.Ticker\(`, `\.history\(`, `\.info\b`, `yf\.download\(`.

6) Validate
- Compare outputs for a few symbols (price, % change, last close). Ensure DataFrame shapes match downstream analytics.

## Security & config
- Do not hardcode secrets. Use env vars or secure config. Keep timeouts (6–12s) and error handling on all external calls.

---
Need help migrating the portfolio or dashboard to the adapter? Open an issue and I’ll wire the first feature end-to-end.

## Fyers API v3: replacing yfinance (step-by-step)

Install
- pip: `pip install fyers-apiv3`

Authenticate (one-time flow to obtain access token)
- Follow Fyers OAuth docs to generate the final access token.
- Store it securely. Options supported by the adapter:
  - Env: `FYERS_ACCESS_TOKEN`
  - File: set `FYERS_TOKEN_PATH` to a JSON file that contains `{ "access_token": "<token>" }`.

Configure environment (Windows PowerShell)
- `setx FYERS_CLIENT_ID "YOUR_CLIENT_ID"`
- `setx FYERS_ACCESS_TOKEN "YOUR_FINAL_ACCESS_TOKEN"`
- Optional: `setx FYERS_TOKEN_PATH "C:\\path\\to\\token.json"`
- Switch provider: `setx MARKET_DATA_PROVIDER "fyers"`
- Restart VS Code/terminal to load setx values.

Symbol mapping
- Adapter maps common tickers:
  - "TCS.NS" -> "NSE:TCS-EQ"
  - "INFY.NS" -> "NSE:INFY-EQ"
  - If you pass a provider-format symbol (e.g., "NSE:SBIN-EQ"), it will be used as-is.

Usage in code
```python
from utils.market_data_adapter import get_provider
provider = get_provider()  # returns FyersProvider when MARKET_DATA_PROVIDER=fyers
q = provider.get_quote("TCS.NS")           # { price, change, volume, ... }
hist = provider.get_history("TCS.NS", period="6mo")  # DataFrame with OHLCV
wide = provider.download(["TCS.NS","INFY.NS"], period="1y")
```

Feature support
- Quotes: uses `fyersModel.FyersModel.quotes({"symbols": sym})`.
- History: uses `fyersModel.FyersModel.history({...})` with daily candles.
- Multi-symbol download: builds a wide Close-price DataFrame from individual history calls.

Notes and limits
- Fundamentals like market_cap/pe_ratio are not filled by default; add an extra call if your Fyers plan provides it.
- Respect API limits; add caching (fetch_json_cached or requests_cache) if you proxy via HTTP.
- Ensure your account has market data permissions for required symbols.
