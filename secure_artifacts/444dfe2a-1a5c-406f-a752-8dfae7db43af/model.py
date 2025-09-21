import yfinance as yf
from datetime import datetime, timedelta

# Define the ticker
ticker = "TCS.NS"

# Set the date range for the last 30 days
end_date = datetime.today()
start_date = end_date - timedelta(days=30)

# Download historical data
data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

# Print the data
print(f"Last 30 days price data for {ticker}:")
print(data[['Open', 'High', 'Low', 'Close', 'Volume']])
