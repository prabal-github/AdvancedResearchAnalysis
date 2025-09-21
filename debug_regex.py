#!/usr/bin/env python3
import re

# Test the regex pattern from our function
pattern = r'\b([A-Z]{2,10}\.(?:NS|BO))\b'
test_text = "Latest on INFY.NS"
test_text_upper = test_text.upper()

print(f"Original text: '{test_text}'")
print(f"Upper text: '{test_text_upper}'")
print(f"Pattern: {pattern}")
print(f"Direct matches: {re.findall(pattern, test_text_upper)}")

# Test with different patterns
pattern2 = r'([A-Z]{2,10}\.(?:NS|BO))'
print(f"Without word boundaries: {re.findall(pattern2, test_text_upper)}")

pattern3 = r'\b([A-Z]+\.NS)\b'
print(f"Simpler NS pattern: {re.findall(pattern3, test_text_upper)}")
