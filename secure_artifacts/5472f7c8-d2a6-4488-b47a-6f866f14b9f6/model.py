import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 10 sample NSE stocks
stocks = [
    "ABB.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS"
]

results = []

for ticker in stocks:
    print(f"Fetching {ticker} ...")
    df = yf.download(ticker, period="2y", interval="1d")

    if df.empty:
        print(f"No data for {ticker}")
        continue

    # Ensure Close is 1D
    if isinstance(df["Close"], pd.DataFrame):
        df["Close"] = df["Close"].iloc[:, 0]

    # Features
    df["Return_1d"] = df["Close"].pct_change()
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["Volatility_5d"] = df["Return_1d"].rolling(5).std()

    # Target: future 5-day return
    df["Future_Return_5d"] = df["Close"].shift(-5) / df["Close"] - 1
    df["Target"] = (df["Future_Return_5d"] > 0).astype(int)

    df = df.dropna()

    if df.empty:
        continue

    # Features and target
    X = df[["Return_1d", "SMA_5", "SMA_10", "Volatility_5d"]]
    y = df["Target"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Accuracy
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    # Predict next period (last row of features)
    latest_features = X.iloc[[-1]]
    prediction = model.predict(latest_features)[0]

    results.append({
        "Ticker": ticker,
        "Accuracy": round(acc, 3),
        "Prediction (Next 5d)": "UP" if prediction == 1 else "DOWN"
    })

# Final results
df_results = pd.DataFrame(results)
print("\nML Model Results:")
print(df_results)
