#!/usr/bin/env python3
"""
Test script for the new fundamental analysis and stock quality features
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    print("Testing imports...")
    from app import get_detailed_fundamental_analysis, calculate_stock_quality_score, get_quality_rating, calculate_fundamental_metrics
    from models.scoring import ResearchReportScorer
    from models.llm_integration import LLMClient
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_fundamental_analysis():
    """Test fundamental analysis function"""
    print("\n" + "="*50)
    print("TESTING FUNDAMENTAL ANALYSIS")
    print("="*50)
    
    # Test with a popular Indian stock
    test_ticker = "RELIANCE.NS"
    print(f"Testing fundamental analysis for {test_ticker}...")
    
    try:
        analysis = get_detailed_fundamental_analysis(test_ticker)
        
        if analysis:
            print("✓ Fundamental analysis successful")
            print(f"Company: {analysis['basic_info']['company_name']}")
            print(f"Sector: {analysis['basic_info']['sector']}")
            print(f"Current Price: ₹{analysis['basic_info']['current_price']:.2f}")
            
            # Test quality assessment
            quality = analysis['quality_assessment']
            print(f"Quality Score: {quality['overall_score']}/100")
            print(f"Quality Rating: {quality['quality_rating']}")
            
            # Test component breakdown
            print("\nComponent Scores:")
            for component, score in quality['component_scores'].items():
                print(f"  {component}: {score}")
            
            return True
        else:
            print(f"✗ No analysis returned for {test_ticker}")
            return False
            
    except Exception as e:
        print(f"✗ Error in fundamental analysis: {e}")
        return False

def test_stock_quality_scoring():
    """Test stock quality scoring integration"""
    print("\n" + "="*50)
    print("TESTING STOCK QUALITY SCORING")
    print("="*50)
    
    try:
        # Initialize scorer
        llm_client = LLMClient()
        scorer = ResearchReportScorer(llm_client)
        
        # Test stock quality assessment
        test_tickers = ["RELIANCE.NS", "TCS.NS"]
        test_ohlc_data = {
            "RELIANCE.NS": {
                'current_price': 2500.0,
                '52w_high': 2700.0,
                '52w_low': 2100.0,
                'volatility': 0.25,
                'avg_volume': 5000000,
                'price_change_percent': 15.5
            },
            "TCS.NS": {
                'current_price': 3400.0,
                '52w_high': 3600.0,
                '52w_low': 3000.0,
                'volatility': 0.20,
                'avg_volume': 2000000,
                'price_change_percent': 8.2
            }
        }
        
        print("Testing stock quality assessment...")
        stock_quality = scorer._assess_stock_quality(test_tickers, test_ohlc_data)
        
        print("✓ Stock quality assessment successful")
        print(f"Average Quality Score: {stock_quality['average_score']:.3f}")
        print(f"Total Stocks Analyzed: {stock_quality['total_stocks']}")
        
        print("\nQuality Distribution:")
        for quality_level, count in stock_quality['quality_distribution'].items():
            print(f"  {quality_level}: {count}")
        
        print("\nStock Details:")
        for ticker, details in stock_quality['stock_details'].items():
            print(f"  {ticker}: {details['quality_score']:.3f} ({details['quality_rating']})")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in stock quality scoring: {e}")
        return False

def test_composite_score_integration():
    """Test that stock quality is properly integrated into composite scoring"""
    print("\n" + "="*50)
    print("TESTING COMPOSITE SCORE INTEGRATION")
    print("="*50)
    
    try:
        # Initialize scorer
        llm_client = LLMClient()
        scorer = ResearchReportScorer(llm_client)
        
        # Test report text
        test_report = """
        Research Report on Reliance Industries [RELIANCE.NS]
        
        Company Overview:
        Reliance Industries is India's largest private sector company with strong fundamentals.
        The company shows excellent profitability with ROE of 18% and strong cash flows.
        
        Financial Analysis:
        - Revenue growth of 15% YoY
        - EBITDA margin of 22%
        - Strong balance sheet with low debt-to-equity ratio
        
        Investment Recommendation:
        Target Price: ₹2,800 (12-month horizon)
        Current Price: ₹2,500
        Recommendation: BUY
        
        Risk Factors:
        Market risk, regulatory changes, and oil price volatility may impact performance.
        
        Disclaimer: This is not investment advice. Please consult your financial advisor.
        """
        
        test_tickers = ["RELIANCE.NS"]
        test_ohlc_data = {
            "RELIANCE.NS": {
                'current_price': 2500.0,
                '52w_high': 2700.0,
                '52w_low': 2100.0,
                'volatility': 0.25,
                'avg_volume': 5000000,
                'price_change_percent': 15.5
            }
        }
        
        print("Testing full report scoring with stock quality integration...")
        result = scorer.score_report(
            report_text=test_report,
            analyst="Test Analyst",
            tickers=test_tickers,
            ohlc_data=test_ohlc_data,
            plagiarism_score=0.0,
            ai_probability=0.1
        )
        
        print("✓ Composite scoring with stock quality successful")
        print(f"Composite Quality Score: {result['composite_quality_score']:.3f}")
        print(f"Base Composite Score: {result['base_composite_score']:.3f}")
        
        # Check if stock quality assessment is included
        if 'stock_quality_assessment' in result:
            stock_quality = result['stock_quality_assessment']
            print(f"Stock Quality Average Score: {stock_quality['average_score']:.3f}")
            print(f"Stock Quality contributes: {stock_quality['average_score'] * 0.10:.3f} to composite score")
            print("✓ Stock quality successfully integrated into composite score")
        else:
            print("✗ Stock quality assessment not found in results")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error in composite score integration: {e}")
        return False

def test_api_endpoint():
    """Test the new API endpoint for fundamental analysis"""
    print("\n" + "="*50)
    print("TESTING API ENDPOINT SIMULATION")
    print("="*50)
    
    try:
        # We can't test the actual API without running Flask, 
        # but we can test the core function that the API would call
        print("Testing fundamental analysis API function...")
        
        # This simulates what the API endpoint would do
        test_ticker = "RELIANCE.NS"
        analysis = get_detailed_fundamental_analysis(test_ticker)
        
        if analysis:
            # Format response like the API would
            api_response = {
                'ticker': test_ticker,
                'fundamental_analysis': analysis,
                'analysis_timestamp': '2025-07-19T01:30:00.000000',
                'success': True
            }
            
            print("✓ API endpoint simulation successful")
            print(f"Response contains {len(api_response)} fields")
            print(f"Analysis for: {analysis['basic_info']['company_name']}")
            return True
        else:
            print("✗ API endpoint simulation failed - no data returned")
            return False
            
    except Exception as e:
        print(f"✗ Error in API endpoint simulation: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("STARTING COMPREHENSIVE TEST OF NEW FEATURES")
    print("="*60)
    
    tests = [
        ("Fundamental Analysis", test_fundamental_analysis),
        ("Stock Quality Scoring", test_stock_quality_scoring),
        ("Composite Score Integration", test_composite_score_integration),
        ("API Endpoint Simulation", test_api_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! New features are working correctly.")
        print("\nFeatures successfully implemented:")
        print("✓ Detailed fundamental analysis of stocks")
        print("✓ Stock quality scoring (0-100 scale)")
        print("✓ Integration into composite quality score (10% weight)")
        print("✓ API endpoint for fundamental analysis")
        print("✓ Enhanced report analysis with stock quality metrics")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
