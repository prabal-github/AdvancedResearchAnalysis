#!/usr/bin/env python3
"""
Demo Stock Recommendation Model
===============================

This is a demonstration model that generates stock recommendations 
to test the performance tracking system.
"""

import datetime
import random

def main():
    """Main entry point for the model"""
    print("=" * 60)
    print("DEMO STOCK RECOMMENDATION MODEL")
    print("=" * 60)
    
    # List of popular stocks for demo
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META']
    
    # Generate 3-5 random recommendations
    num_recs = random.randint(3, 5)
    recommendations = []
    
    for i in range(num_recs):
        stock = random.choice(stocks)
        action = random.choice(['BUY', 'SELL', 'HOLD'])
        price = random.uniform(100, 300)
        confidence = random.uniform(70, 95)
        
        if action == 'BUY':
            target = price * random.uniform(1.05, 1.20)
            stop = price * random.uniform(0.85, 0.95)
        elif action == 'SELL':
            target = price * random.uniform(0.80, 0.95)
            stop = price * random.uniform(1.05, 1.15)
        else:  # HOLD
            target = price * random.uniform(0.98, 1.02)
            stop = None
        
        rec = {
            'symbol': stock,
            'action': action,
            'price': price,
            'confidence': confidence,
            'target': target,
            'stop': stop
        }
        recommendations.append(rec)
    
    print(f"\nGenerated {len(recommendations)} stock recommendations:")
    print("-" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. Stock: {rec['symbol']}")
        print(f"   Action: {rec['action']} @ ${rec['price']:.2f}")
        print(f"   Confidence: {rec['confidence']:.1f}%")
        if rec['target']:
            print(f"   Target: ${rec['target']:.2f}")
        if rec['stop']:
            print(f"   Stop Loss: ${rec['stop']:.2f}")
        print()
    
    print("Model Analysis Summary:")
    print(f"- Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- Total recommendations: {len(recommendations)}")
    print(f"- BUY signals: {len([r for r in recommendations if r['action'] == 'BUY'])}")
    print(f"- SELL signals: {len([r for r in recommendations if r['action'] == 'SELL'])}")
    print(f"- HOLD signals: {len([r for r in recommendations if r['action'] == 'HOLD'])}")
    print(f"- Average confidence: {sum(r['confidence'] for r in recommendations) / len(recommendations):.1f}%")
    
    return {
        'recommendations': recommendations,
        'timestamp': datetime.datetime.now().isoformat(),
        'model_name': 'Demo Stock Model',
        'version': '1.0'
    }

if __name__ == '__main__':
    result = main()
    print(f"\nModel execution completed successfully!")
    print(f"Performance tracking will automatically extract these recommendations.")
