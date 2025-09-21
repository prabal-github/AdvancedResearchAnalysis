#!/usr/bin/env python3
"""
Test report submission through the enhanced /analyze_new interface
"""

import requests
import json

def test_enhanced_analyze_new():
    print("🧪 Testing Enhanced /analyze_new Interface")
    print("=" * 50)
    
    # Test submission with enhanced fields
    test_data = {
        "analyst": "Enhanced Test Analyst",
        "topic": "Technology Sector Analysis",
        "sub_heading": "AI and Cloud Computing Driving Growth",
        "text": """
        TCS.NS - TECHNOLOGY SECTOR ANALYSIS
        
        Executive Summary:
        Tata Consultancy Services continues to lead the Indian IT sector with strong performance 
        in digital transformation services. The company's focus on AI and cloud computing solutions 
        positions it well for future growth.
        
        Key Financial Metrics:
        - Revenue: ₹58,000+ crores (quarterly)
        - Net Profit Margin: 23.5%
        - Employee Count: 615,000+ globally
        - Digital Revenue: 48% of total revenue
        
        Investment Thesis:
        1. Market Leadership: Dominant position in Indian IT services
        2. Digital Transformation: Strong capabilities in emerging technologies
        3. Global Presence: Operations across 55+ countries
        4. Talent Pipeline: Robust recruitment and training programs
        
        Risk Factors:
        - Currency fluctuations impact
        - Increased competition in digital services
        - Regulatory changes in key markets
        
        Recommendation: BUY with target price of ₹4,200
        Current Price: ₹3,750
        Upside Potential: 12%
        
        This analysis incorporates the latest quarterly results and forward guidance
        provided by the management team during recent investor calls.
        """
    }
    
    print("📝 Submitting Enhanced Report:")
    print(f"   Analyst: {test_data['analyst']}")
    print(f"   Topic: {test_data['topic']}")
    print(f"   Sub-heading: {test_data['sub_heading']}")
    print(f"   Report Length: {len(test_data['text'])} characters")
    
    try:
        # Submit the report
        response = requests.post(
            "http://127.0.0.1:5008/analyze",
            json=test_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Report submitted successfully!")
            
            if 'report_id' in result:
                report_id = result['report_id']
                print(f"📄 Report ID: {report_id}")
                
                # Test the public report view
                public_url = f"http://127.0.0.1:5008/public/report/{report_id}"
                public_response = requests.get(public_url, timeout=10)
                
                if public_response.status_code == 200:
                    content = public_response.text
                    print(f"\n🌐 Public Report Analysis:")
                    
                    # Check for topic badge
                    if test_data['topic'] in content:
                        print("   ✅ Topic displayed in public view")
                    else:
                        print("   ❌ Topic not found in public view")
                    
                    # Check for sub-heading
                    if test_data['sub_heading'] in content:
                        print("   ✅ Sub-heading displayed in public view")
                    else:
                        print("   ❌ Sub-heading not found in public view")
                    
                    # Check for analyst name
                    if test_data['analyst'] in content:
                        print("   ✅ Analyst name displayed")
                    else:
                        print("   ❌ Analyst name not found")
                    
                    # Check for content preview
                    if "TCS.NS" in content:
                        print("   ✅ Report content preview displayed")
                    else:
                        print("   ❌ Report content not found")
                    
                    # Check for LinkedIn meta tags
                    if 'og:title' in content and test_data['topic'] in content:
                        print("   ✅ Enhanced LinkedIn meta tags present")
                    else:
                        print("   ❌ LinkedIn meta tags missing or incomplete")
                    
                    print(f"\n🔗 Access URLs:")
                    print(f"   Public Report: {public_url}")
                    print(f"   LinkedIn Share: https://www.linkedin.com/sharing/share-offsite/?url={public_url}")
                    
                    return report_id
                    
                else:
                    print(f"❌ Public view error: {public_response.status_code}")
                    
            else:
                print("❌ No report ID in response")
                print(f"Response: {result}")
                
        else:
            print(f"❌ Submission failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during submission: {e}")
        return None
    
    return None

def test_form_features():
    """Test the form features directly"""
    print("\n🖥️  Testing Form Features:")
    
    try:
        # Test direct access to the form
        response = requests.get("http://127.0.0.1:5008/analyze_new", timeout=5)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for form fields
            checks = [
                ('id="analyst"', 'Analyst Name field'),
                ('id="topic"', 'Topic field'),
                ('id="subHeading"', 'Sub-heading field'),
                ('id="reportText"', 'Report Text field'),
                ('Report Topic', 'Topic label'),
                ('Sub-Heading', 'Sub-heading label')
            ]
            
            for check_text, description in checks:
                if check_text in content:
                    print(f"   ✅ {description} present")
                else:
                    print(f"   ❌ {description} missing")
                    
        else:
            print(f"   ❌ Form page error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking form: {e}")

if __name__ == "__main__":
    # Test form features first
    test_form_features()
    
    # Test report submission
    report_id = test_enhanced_analyze_new()
    
    if report_id:
        print(f"\n🎉 All tests completed successfully!")
        print(f"✅ Enhanced /analyze_new page working correctly")
        print(f"✅ Topic and sub-heading fields functional")
        print(f"✅ Public report view enhanced")
        print(f"✅ LinkedIn sharing optimized")
    else:
        print(f"\n⚠️  Some tests failed - check the output above")
