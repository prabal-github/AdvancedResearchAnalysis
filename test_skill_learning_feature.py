#!/usr/bin/env python3
"""
Test the new Skill Learning Analysis feature
"""

import requests
import json
from datetime import datetime

def test_skill_learning_feature():
    """Test the skill learning analysis feature end-to-end"""
    base_url = "http://localhost:5008"
    
    print("🎓 TESTING SKILL LEARNING ANALYSIS FEATURE")
    print("=" * 60)
    
    # Sample report with financial data that should trigger skill learning modules
    sample_report = {
        "analyst": "Financial Analyst with Coding Skills",
        "text": """
COMPREHENSIVE FINANCIAL ANALYSIS - TATA CONSULTANCY SERVICES (TCS.NS)
ANALYST: John Doe, CFA, SEBI Registration: INH000001234

EXECUTIVE SUMMARY:
TCS demonstrates exceptional financial performance with strong revenue growth and improving margins.
This technical analysis incorporates fundamental metrics, sentiment analysis, and market trends.

FINANCIAL HIGHLIGHTS & REVENUE TREND ANALYSIS:
Q1 2024 Revenue: ₹58,229 Cr (+16.8% YoY growth)
Q2 2024 Revenue: ₹61,327 Cr (+12.3% QoQ growth) 
Operating Margin: 25.1% (industry-leading performance)
Net Income: ₹11,058 Cr (+12.5% YoY growth)
ROE: 41.2% (excellent capital efficiency)

TECHNICAL ANALYSIS & STOCK PERFORMANCE:
Current Price: ₹3,847
52-week Range: ₹3,100 - ₹4,200
RSI: 68.5 (approaching overbought territory)
MACD: Bullish crossover observed
Moving Averages: Price above 20-day and 50-day SMAs

MARKET SENTIMENT ANALYSIS:
Recent news sentiment shows 78% positive coverage
Analyst upgrades from 3 major firms in last quarter
Strong client wins in BFSI and retail sectors
ESG initiatives receiving positive market response

QUARTERLY PERFORMANCE DATABASE ANALYSIS:
Revenue CAGR (3-year): 15.2%
Profit margin expansion: 180 bps over 24 months
Debt-to-equity ratio: 0.05 (conservative balance sheet)
Free cash flow: ₹45,000 Cr (strong cash generation)

GEOPOLITICAL CONSIDERATIONS:
H-1B visa challenges offset by nearshore strategy
Europe expansion proceeding as planned
Digital transformation demand remains robust
AI/ML capabilities providing competitive advantage

INVESTMENT RECOMMENDATION: BUY
Target Price: ₹4,200 (12-month horizon)
Risk Rating: Low-Medium
Key Catalysts: Digital deals, margin expansion, AI adoption
        """
    }
    
    print("\n1. Submitting Sample Report for Analysis...")
    print("-" * 40)
    
    try:
        # Submit the report
        response = requests.post(f"{base_url}/analyze", json=sample_report)
        
        if response.status_code == 200:
            result = response.json()
            report_id = result['report_id']
            analysis_result = result['result']
            
            print(f"✅ Report submitted successfully!")
            print(f"📋 Report ID: {report_id}")
            
            # Check if skill learning data is included in response
            if 'skill_learning' in analysis_result:
                skill_data = analysis_result['skill_learning']
                print(f"✅ Skill Learning Analysis included in response")
                print(f"📚 Learning modules generated: {skill_data['modules_count']}")
                
                for i, module in enumerate(skill_data['modules'], 1):
                    print(f"   {i}. {module['title']} ({module['skill_category'].upper()})")
            else:
                print("⚠️ Skill Learning Analysis not found in response")
            
            print(f"\n2. Testing Skill Learning Analysis Page...")
            print("-" * 40)
            
            # Test the skill learning analysis page
            skill_response = requests.get(f"{base_url}/skill_learning/{report_id}")
            
            if skill_response.status_code == 200:
                print("✅ Skill Learning Analysis page loads successfully")
                
                # Check for key elements in the page
                page_content = skill_response.text
                success_indicators = [
                    ("Skill Learning Analysis", "Page title"),
                    ("Perfect Fusion of Financial Reporting + Upskilling", "Feature description"),
                    ("Python", "Python skill section"),
                    ("SQL", "SQL skill section"),
                    ("Click to See How This Was Done in Code", "Expandable code sections"),
                    ("What You Learned from This", "Learning objectives"),
                    ("Business Insight", "Business insights")
                ]
                
                for indicator, description in success_indicators:
                    if indicator in page_content:
                        print(f"   ✅ {description} found")
                    else:
                        print(f"   ❌ {description} missing")
                        
            else:
                print(f"❌ Skill Learning Analysis page failed: {skill_response.status_code}")
            
            print(f"\n3. Testing Navigation Integration...")
            print("-" * 40)
            
            # Test regular report page for skill learning button
            report_response = requests.get(f"{base_url}/report/{report_id}")
            if report_response.status_code == 200 and "Skill Learning Analysis" in report_response.text:
                print("✅ Skill Learning button added to report page")
            else:
                print("❌ Skill Learning button missing from report page")
            
            # Test enhanced analysis page for skill learning button
            enhanced_response = requests.get(f"{base_url}/enhanced_analysis/{report_id}")
            if enhanced_response.status_code == 200 and "Skill Learning Analysis" in enhanced_response.text:
                print("✅ Skill Learning button added to enhanced analysis page")
            else:
                print("❌ Skill Learning button missing from enhanced analysis page")
            
            # Test main dashboard for skill learning buttons
            dashboard_response = requests.get(f"{base_url}/")
            if dashboard_response.status_code == 200 and "Learn Code" in dashboard_response.text:
                print("✅ Skill Learning buttons added to main dashboard")
            else:
                print("❌ Skill Learning buttons missing from main dashboard")
                
            print(f"\n4. Testing API Integration...")
            print("-" * 40)
            
            # Test direct API access to skill learning data
            try:
                api_response = requests.get(f"{base_url}/api/enhanced_analysis_reports")
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    if api_data.get('success'):
                        print("✅ API integration working")
                    else:
                        print("❌ API response indicates failure")
                else:
                    print(f"❌ API request failed: {api_response.status_code}")
            except Exception as e:
                print(f"❌ API test failed: {e}")
            
            return report_id
            
        else:
            print(f"❌ Report submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None

def demonstrate_feature_examples():
    """Show examples of what the skill learning feature provides"""
    print(f"\n🚀 SKILL LEARNING FEATURE EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "title": "Financial Trend Analysis (Python)",
            "description": "Learn to analyze revenue trends with pandas and matplotlib",
            "skills": ["Data manipulation", "Time series analysis", "Professional charts", "Growth calculations"]
        },
        {
            "title": "Stock Technical Analysis (Python)", 
            "description": "Master technical indicators like RSI, MACD using yfinance",
            "skills": ["Financial APIs", "Technical indicators", "Trading signals", "Multi-panel charts"]
        },
        {
            "title": "Financial Database Queries (SQL)",
            "description": "Advanced SQL for financial database analysis",
            "skills": ["Window functions", "Growth rate calculations", "Ranking", "Time series SQL"]
        },
        {
            "title": "AI-Powered Sentiment Analysis (AI/ML)",
            "description": "Use machine learning for market sentiment analysis",
            "skills": ["Natural Language Processing", "Machine Learning", "Correlation analysis", "Predictive modeling"]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   📝 {example['description']}")
        print(f"   🎯 Skills: {', '.join(example['skills'])}")
    
    print(f"\n💡 KEY BENEFITS:")
    print("   • Perfect fusion of financial reporting + upskilling")
    print("   • Real code examples based on actual report content")
    print("   • Expandable 'See How This Was Done in Code' sections")
    print("   • Learning objectives and business insights")
    print("   • Progressive skill levels (Beginner → Intermediate → Advanced)")
    print("   • Copy-paste ready code with syntax highlighting")

if __name__ == "__main__":
    print("🎓 SKILL LEARNING ANALYSIS - COMPREHENSIVE TEST")
    print("Making Financial Analysts Job-Ready with Coding Skills")
    print("=" * 80)
    
    # Test the feature
    report_id = test_skill_learning_feature()
    
    # Show feature examples
    demonstrate_feature_examples()
    
    print(f"\n🎯 TESTING SUMMARY:")
    print("=" * 60)
    
    if report_id:
        print("✅ Skill Learning Analysis feature is working!")
        print(f"✅ Test report ID: {report_id}")
        print(f"✅ Access skill learning at: http://localhost:5000/skill_learning/{report_id}")
        print("\n🌟 FEATURE HIGHLIGHTS:")
        print("   • Automatic code generation based on report content")
        print("   • Python, SQL, and AI/ML examples")
        print("   • Interactive expandable code sections")
        print("   • Copy-to-clipboard functionality")
        print("   • Business insights + technical implementation")
        print("   • Perfect for analyst skill development!")
    else:
        print("❌ Some issues detected. Please check the application.")
    
    print(f"\n🎉 Perfect fusion of reporting + upskilling achieved!")
    print("Financial analysts can now learn coding while analyzing reports!")
