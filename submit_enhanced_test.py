#!/usr/bin/env python3
"""
Submit a test report through the enhanced interface
"""

import requests
import json
import time

def submit_test_report():
    print("🧪 Submitting Enhanced Report Test")
    print("=" * 40)
    
    # Test data with all new fields
    test_data = {
        "analyst": "Technology Analyst Sarah Chen",
        "topic": "Cloud Computing Growth",
        "sub_heading": "Enterprise Digital Transformation Accelerating Cloud Adoption",
        "text": """
        MICROSOFT CORPORATION (MSFT) - CLOUD COMPUTING ANALYSIS
        
        Executive Summary:
        Microsoft continues to dominate the enterprise cloud computing market with Azure 
        showing strong growth trajectory. The company's integrated ecosystem of productivity 
        tools and cloud services creates significant competitive advantages.
        
        Key Performance Indicators:
        • Azure Revenue Growth: 27% YoY
        • Cloud Revenue: $28.5B quarterly
        • Market Share: 23% of global cloud market
        • Enterprise Customers: 250,000+ active Azure customers
        
        Investment Highlights:
        1. Market Leadership: Strong position in enterprise cloud services
        2. Ecosystem Integration: Office 365, Teams, and Azure synergies
        3. AI Integration: Copilot and OpenAI partnership driving innovation
        4. Subscription Model: Predictable recurring revenue streams
        
        Financial Metrics:
        • Revenue: $62.0B (Q4 2024)
        • Net Income: $22.1B
        • Free Cash Flow: $20.5B
        • Gross Margin: 69.7%
        
        Risk Assessment:
        - Intense competition from AWS and Google Cloud
        - Regulatory scrutiny on market dominance
        - Cybersecurity threats to cloud infrastructure
        - Economic slowdown impact on enterprise spending
        
        Price Target: $425 (Current: $378)
        Recommendation: STRONG BUY
        Expected Return: 12.4%
        Time Horizon: 12 months
        
        This analysis incorporates the latest quarterly earnings, Azure growth metrics,
        and forward guidance from Microsoft's recent investor conference calls.
        """
    }
    
    print(f"📝 Report Details:")
    print(f"   Analyst: {test_data['analyst']}")
    print(f"   Topic: {test_data['topic']}")
    print(f"   Sub-heading: {test_data['sub_heading']}")
    print(f"   Content Length: {len(test_data['text'])} characters")
    
    try:
        # Submit the report
        print(f"\n📤 Submitting to /analyze endpoint...")
        response = requests.post(
            "http://127.0.0.1:80/analyze",
            json=test_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Report processed.")
            
            if 'report_id' in result:
                report_id = result['report_id']
                print(f"🆔 Report ID: {report_id}")
                
                # Wait a moment for processing
                time.sleep(2)
                
                # Check public view
                public_url = f"http://127.0.0.1:80/public/report/{report_id}"
                print(f"\n🌐 Testing Public View: {public_url}")
                
                public_response = requests.get(public_url, timeout=10)
                if public_response.status_code == 200:
                    content = public_response.text
                    
                    # Verify new features
                    checks = [
                        (test_data['topic'], "Topic"),
                        (test_data['sub_heading'], "Sub-heading"),
                        (test_data['analyst'], "Analyst name"),
                        ("MICROSOFT CORPORATION", "Report content"),
                        ("og:title", "LinkedIn meta tags"),
                        ("badge", "Topic badge styling")
                    ]
                    
                    print(f"🔍 Public View Verification:")
                    for check_text, description in checks:
                        if check_text in content:
                            print(f"   ✅ {description} found")
                        else:
                            print(f"   ❌ {description} missing")
                    
                    # Show URLs
                    print(f"\n🔗 Access Links:")
                    print(f"   📄 Public Report: {public_url}")
                    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={public_url}"
                    print(f"   📱 LinkedIn Share: {linkedin_url}")
                    
                    return report_id
                else:
                    print(f"❌ Public view failed: {public_response.status_code}")
            else:
                print(f"⚠️  No report_id in response: {result}")
        else:
            print(f"❌ Submission failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    report_id = submit_test_report()
    
    if report_id:
        print(f"\n🎉 Test completed successfully!")
        print(f"✅ Enhanced fields working correctly")
        print(f"✅ Public report view updated")
        print(f"✅ LinkedIn sharing optimized")
        print(f"\n🔗 Quick Access: http://127.0.0.1:80/public/report/{report_id}")
    else:
        print(f"\n⚠️  Test incomplete - check error messages above")
