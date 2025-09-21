from app import extract_tickers_from_text

# Test the new bracketed ticker extraction
test_reports = [
    "This is a report about [ITC.NS] and [TCS.NS] showing strong performance.",
    "We recommend buying [RELIANCE.NS] and [INFY.NS] for long term growth.",
    "Analysis of HDFC Bank and ITC without brackets should not be extracted.",
    "Mixed format: [WIPRO.NS] with brackets and TCS.NS without brackets.",
    "No Indian stocks mentioned in this report about global markets.",
    "[BAJFINANCE.NS] and [HDFCBANK.NS] are showing bullish trends in the market."
]

print("Testing new bracketed ticker extraction:")
print("=" * 50)

for i, report in enumerate(test_reports, 1):
    print(f"\nTest {i}:")
    print(f"Report: {report}")
    tickers = extract_tickers_from_text(report)
    print(f"Extracted tickers: {tickers}")
    print("-" * 40)
