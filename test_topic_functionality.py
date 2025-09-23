#!/usr/bin/env python3
"""
Test the new topic and sub_heading functionality
"""

import requests
import json

def test_topic_functionality():
    print("🧪 Testing Topic and Sub-Heading Functionality")
    print("=" * 50)
    
    # Test data with topic and sub_heading
    test_report = {
        "analyst": "Test Analyst",
        "topic": "Q3 Earnings Analysis",
        "sub_heading": "Strong Performance Despite Market Volatility",
        "text": """
        RELIANCE INDUSTRIES LIMITED (RELIANCE.NS) - Q3 2025 EARNINGS ANALYSIS
        
        Executive Summary:
        Reliance Industries has delivered exceptional results in Q3 2025, showcasing robust growth across its diversified business portfolio. The company's strategic focus on digital transformation and green energy initiatives continues to drive value creation.
        
        Key Financial Highlights:
        - Revenue increased by 15.2% YoY to ₹2,35,000 crores
        - Net profit grew by 12.8% to ₹18,500 crores
        - EBITDA margins improved to 22.5%
        - Strong cash flow generation of ₹25,000 crores
        
        Business Segment Performance:
        1. Oil-to-Chemicals (O2C): Maintained steady performance with improved refining margins
        2. Jio Platforms: Subscriber base crossed 450 million with ARPU growth
        3. Retail: Same-store sales growth of 8% with expanding footprint
        4. New Energy: Significant progress in solar and battery manufacturing
        
        Investment Recommendation:
        We maintain a BUY rating with a target price of ₹3,200, representing 20% upside potential. The company's diversified business model and strong execution capabilities position it well for sustained growth.
        
        Risk Factors:
        - Regulatory changes in telecom sector
        - Commodity price volatility
        - Global economic slowdown impact
        """
    }
    
    print("📝 Test Report Data:")
    print(f"   Topic: {test_report['topic']}")
    print(f"   Sub-heading: {test_report['sub_heading']}")
    print(f"   Analyst: {test_report['analyst']}")
    print(f"   Text length: {len(test_report['text'])} characters")
    
    # Submit to local Flask app
    try:
        response = requests.post(
            "http://127.0.0.1:80/analyze",
            json=test_report,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Report submitted successfully!")
            print(f"   Report ID: {result.get('report_id', 'Unknown')}")
            
            if 'report_id' in result:
                report_id = result['report_id']
                public_url = f"http://127.0.0.1:80/public/report/{report_id}"
                linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={public_url}"
                
                print(f"\n🔗 Generated URLs:")
                print(f"   Public Report: {public_url}")
                print(f"   LinkedIn Share: {linkedin_url}")
                
                print(f"\n🎯 Expected Features in Public View:")
                print("   ✅ Topic badge displayed")
                print("   ✅ Sub-heading as H2")
                print("   ✅ First 200 words of report")
                print("   ✅ Enhanced LinkedIn meta tags")
                
                return report_id
        else:
            print(f"❌ Error submitting report: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return None

if __name__ == "__main__":
    test_topic_functionality()
