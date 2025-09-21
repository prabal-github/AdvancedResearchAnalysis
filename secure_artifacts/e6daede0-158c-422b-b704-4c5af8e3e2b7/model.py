import yfinance as yf
import pandas as pd

# Pick 10 stocks
stocks = [
    "ABB.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS"
]

results = []

for ticker in stocks:
    print(f"Fetching {ticker} ...")
    df = yf.download(ticker, period="1y", interval="1d")

    if df.empty:
        print(f"No data for {ticker}")
        continue

    # Fix multi-dimensional Close column
    if isinstance(df["Close"], pd.DataFrame):
        df["Close"] = df["Close"].iloc[:, 0]

    # Calculate daily returns
    df["Daily Return"] = df["Close"].pct_change()

    # Calculate annualized return & volatility
    mean_return = df["Daily Return"].mean() * 252
    volatility = df["Daily Return"].std() * (252 ** 0.5)

    results.append({
        "Ticker": ticker,
        "Annualized Return": round(mean_return, 4),
        "Annualized Volatility": round(volatility, 4)
    })

# Show analysis
df_results = pd.DataFrame(results)
print("\nStock Analysis:")
print(df_results)
