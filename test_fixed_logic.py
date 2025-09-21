#!/usr/bin/env python3

common_words = {'WHAT', 'IS', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH', 'ON', 'AT', 'TO', 'IN', 'BY', 'OF', 'FROM', 'UP', 'OUT', 'IF', 'ABOUT', 'WHO', 'GET', 'GO', 'DO', 'MAKE', 'TAKE', 'NEW', 'GOOD', 'HIGH', 'LOW', 'BIG', 'SMALL', 'LONG', 'SHORT', 'HOW', 'WHEN', 'WHERE', 'WHY', 'NOW', 'HERE', 'THERE'}

ticker = 'INFY.NS'
ticker_clean = ticker.upper().replace('.NS', '').replace('.BO', '')

print(f'Testing fixed logic:')
print(f'Ticker: {ticker}')
print(f'Clean: "{ticker_clean}"')
print(f'Is exactly a common word: {ticker_clean in common_words}')
print(f'Should keep ticker: {ticker_clean not in common_words}')

# Test with a few different cases
test_cases = ['INFY.NS', 'TCS.NS', 'ON.NS', 'IN.NS', 'THE.NS', 'RELIANCE.NS']
print('\nTest cases:')
for test_ticker in test_cases:
    clean = test_ticker.upper().replace('.NS', '').replace('.BO', '')
    keep = clean not in common_words
    print(f'  {test_ticker} -> "{clean}" -> Keep: {keep}')
