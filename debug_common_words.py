#!/usr/bin/env python3

common_words = {'WHAT', 'IS', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH', 'ON', 'AT', 'TO', 'IN', 'BY', 'OF', 'FROM', 'UP', 'OUT', 'IF', 'ABOUT', 'WHO', 'GET', 'GO', 'DO', 'MAKE', 'TAKE', 'NEW', 'GOOD', 'HIGH', 'LOW', 'BIG', 'SMALL', 'LONG', 'SHORT', 'HOW', 'WHEN', 'WHERE', 'WHY', 'NOW', 'HERE', 'THERE'}

ticker = 'INFY.NS'
ticker_clean = ticker.upper().replace('.NS', '').replace('.BO', '')

print(f'Ticker: {ticker}')
print(f'Clean: "{ticker_clean}"')
print(f'Common words: {sorted(common_words)}')
print(f'Has common word: {any(word in ticker_clean for word in common_words)}')

# Check each word specifically
matches = [word for word in common_words if word in ticker_clean]
print(f'Matching words: {matches}')

# Check if "IN" is causing the issue
print(f'"IN" in "INFY": {"IN" in "INFY"}')
print(f'"IF" in "INFY": {"IF" in "INFY"}')
