#!/usr/bin/env python3
"""
Utility functions to extract recommendations and results from script outputs
"""

import re
import json

def extract_recommendation_from_output(output_text):
    """
    Extract recommendation from script output using pattern matching
    Returns: recommendation string or None
    """
    if not output_text:
        return None
    
    # Convert to string if not already
    output_text = str(output_text).lower()
    
    # Common recommendation patterns
    patterns = [
        r'recommendation[:\s]*([a-zA-Z\s]+)',
        r'suggest[a-zA-Z\s]*[:\s]*([a-zA-Z\s]+)', 
        r'action[:\s]*([a-zA-Z\s]+)',
        r'decision[:\s]*([a-zA-Z\s]+)',
        r'final.*?([buy|sell|hold])',
        r'([buy|sell|hold])\s*recommendation',
        r'strategy[:\s]*([a-zA-Z\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            recommendation = match.group(1).strip()
            # Clean up the recommendation
            if any(word in recommendation for word in ['buy', 'purchase', 'acquire']):
                return 'Buy'
            elif any(word in recommendation for word in ['sell', 'short', 'exit']):
                return 'Sell'
            elif any(word in recommendation for word in ['hold', 'wait', 'maintain']):
                return 'Hold'
            elif any(word in recommendation for word in ['btst', 'buy today sell tomorrow']):
                return 'BTST Buy'
    
    # Look for specific words directly
    if any(word in output_text for word in ['buy', 'purchase', 'acquire']):
        return 'Buy'
    elif any(word in output_text for word in ['sell', 'short', 'exit']):
        return 'Sell'
    elif any(word in output_text for word in ['hold', 'wait', 'maintain']):
        return 'Hold'
    elif any(word in output_text for word in ['btst']):
        return 'BTST Buy'
    
    return None

def extract_result_from_output(output_text):
    """
    Extract actual result from script output (profit/loss percentage, etc.)
    Returns: result string or None
    """
    if not output_text:
        return None
    
    # Convert to string if not already
    output_text = str(output_text).lower()
    
    # Look for percentage returns
    percent_pattern = r'[-+]?\d*\.?\d+%'
    percent_match = re.search(percent_pattern, output_text)
    if percent_match:
        return percent_match.group(0)
    
    # Look for profit/loss indicators
    if any(word in output_text for word in ['profit', 'gain', 'positive', 'up']):
        return 'Profit'
    elif any(word in output_text for word in ['loss', 'negative', 'down']):
        return 'Loss'
    
    # Look for numeric returns
    return_pattern = r'return[:\s]*[-+]?\d*\.?\d+'
    return_match = re.search(return_pattern, output_text, re.IGNORECASE)
    if return_match:
        return return_match.group(0).split(':')[-1].strip()
    
    return None

def simulate_actual_result(recommendation):
    """
    Simulate actual result based on recommendation (for demo purposes)
    In a real scenario, this would come from market data after some time
    """
    import random
    
    if recommendation == 'Buy' or recommendation == 'BTST Buy':
        # Buy recommendations have 70% success rate
        if random.random() < 0.7:
            return f"{random.uniform(2, 15):.1f}%"  # Profit
        else:
            return f"-{random.uniform(0.5, 8):.1f}%"  # Loss
    elif recommendation == 'Sell':
        # Sell recommendations have 65% success rate
        if random.random() < 0.65:
            return 'Profit'
        else:
            return 'Loss'
    elif recommendation == 'Hold':
        # Hold recommendations usually neutral
        return f"{random.uniform(-2, 4):.1f}%"
    
    return None

if __name__ == "__main__":
    # Test the extraction functions
    test_outputs = [
        "Analysis complete. Recommendation: BUY RELIANCE with target price 2500",
        "Final decision: SELL due to bearish indicators",
        "Strategy suggests HOLD position until next quarter",
        "BTST opportunity detected for TCS. Expected return: 5.2%",
        "Stock analysis shows positive momentum. Action: Buy. Profit target: 12%"
    ]
    
    print("Testing recommendation extraction:")
    for output in test_outputs:
        rec = extract_recommendation_from_output(output)
        result = extract_result_from_output(output)
        print(f"Output: {output[:50]}...")
        print(f"  Recommendation: {rec}")
        print(f"  Result: {result}")
        print()
