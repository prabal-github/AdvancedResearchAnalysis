#!/usr/bin/env python3
"""
Quick ML Test
"""

import sys
sys.path.append('.')

print("Testing Options ML Analyzer...")
from models.options_ml_analyzer import OptionsMLAnalyzer
options = OptionsMLAnalyzer()
print(f"Options analyzer: {options.name}")

result = options.analyze('NSE_INDEX|Nifty 50', '2025-08-12', 7, 0.05, 22000)
print(f"Options success: {result.get('success')}")
print(f"Trade recommendations: {len(result.get('trade_recommendations', []))}")

print("\nTesting Sector ML Analyzer...")
from models.sector_ml_analyzer import SectorMLAnalyzer  
sector = SectorMLAnalyzer()
print(f"Sector analyzer: {sector.name}")

# Test with just one sector to be fast
result = sector.analyze_sector('Banking', '3mo')
print(f"Sector success: {'error' not in result}")
print(f"Has sector_recommendation: {result.get('sector_recommendation') is not None}")
if result.get('sector_recommendation'):
    print(f"Recommendation: {result['sector_recommendation'].get('recommendation', 'N/A')}")
    print(f"Confidence: {result['sector_recommendation'].get('confidence', 0)}%")

print("\nDone!")
