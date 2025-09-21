!pip install yfinance

import yfinance as yf

# Define the stock symbol and exchange (NSE in this case)
ticker_symbol = 'TCS.NS'

# Fetch the data for the specified stock symbol from NSE
stock = yf.Ticker(ticker_symbol)

# Download historical price data
history = stock.history(period='1d', start="2020-01-01", end="2023-01-01")

# Print the dataframe
print(history)