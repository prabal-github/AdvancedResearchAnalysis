#!/usr/bin/env python3
"""
Quick Report Submission Test
Demonstrates exactly how to submit reports to the system
"""

import requests
import json

def test_report_submission():
    """Test report submission with a sample report"""
    
    base_url = "http://localhost:5000"
    
    print("📝 REPORT SUBMISSION TEST")
    print("=" * 40)
    
    # Sample report for testing
    sample_report = {
        "analyst": "Test Analyst CFA",
        "text": """
TATA CONSULTANCY SERVICES (TCS) - BUY RECOMMENDATION

ANALYST: Test Analyst, CFA, SEBI Registration: INH000001234

EXECUTIVE SUMMARY:
TCS demonstrates strong fundamentals in IT services with robust digital transformation capabilities.
The company maintains market leadership with excellent client relationships and geographic diversification.

FINANCIAL HIGHLIGHTS:
- Revenue: ₹58,229 Cr (+16.8% YoY)
- Operating Margin: 25.1%
- Net Income: ₹11,058 Cr (+12.5% YoY)
- ROE: 41.2%

GEOPOLITICAL CONSIDERATIONS:
Trade war tensions and H-1B visa restrictions pose challenges, but TCS's nearshore strategy
and local hiring initiatives mitigate regulatory changes. Political instability in key markets
is offset by geographic diversification across 46 countries.

RISK FACTORS:
Market Risk: Currency fluctuations (70% USD revenues)
Regulatory Risk: Visa policy changes in US/UK
Operational Risk: Talent attrition (industry average 15%)
Concentration Risk: Top 10 clients represent 31% of revenue

ESG HIGHLIGHTS:
Carbon neutral by 2030, diversity initiatives, strong governance practices

SEBI COMPLIANCE:
Full disclosures as per Research Analyst Regulations 2014
No material conflicts, DCF-based valuation methodology

PRICE TARGET: ₹4,200 (15% upside from current ₹3,650)
        """
    }
    
    print(f"🎯 Testing submission for: {sample_report['analyst']}")
    print(f"📊 Report covers: TCS")
    
    try:
        # Test the submission
        print("\n1. Submitting report via API...")
        response = requests.post(
            f"{base_url}/analyze",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(sample_report)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report submitted successfully!")
            
            if 'report_id' in result:
                report_id = result['report_id']
                print(f"📋 Report ID: {report_id}")
                
                # Test accessing the report
                print(f"\n2. Testing report access...")
                report_url = f"{base_url}/report/{report_id}"
                report_response = requests.get(report_url)
                
                if report_response.status_code == 200:
                    print(f"✅ Report accessible at: {report_url}")
                else:
                    print(f"⚠️ Report access failed: {report_response.status_code}")
                
                # Test enhanced analysis
                print(f"\n3. Testing enhanced analysis...")
                enhanced_url = f"{base_url}/enhanced_analysis/{report_id}"
                enhanced_response = requests.get(enhanced_url)
                
                if enhanced_response.status_code == 200:
                    print(f"✅ Enhanced analysis accessible at: {enhanced_url}")
                else:
                    print(f"⚠️ Enhanced analysis failed: {enhanced_response.status_code}")
                
            else:
                print("⚠️ No report ID returned")
                print(f"Response: {result}")
                
        else:
            print(f"❌ Submission failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during submission: {e}")

def show_submission_methods():
    """Show different ways to submit reports"""
    
    print("\n" + "=" * 50)
    print("📚 REPORT SUBMISSION METHODS")
    print("=" * 50)
    
    print("\n🌐 METHOD 1: Web Interface")
    print("-" * 30)
    print("1. Go to: http://localhost:5000")
    print("2. Click: 'Analyze New Report' (blue button)")
    print("3. Fill in: Analyst name and report text")
    print("4. Click: 'Analyze Report'")
    print("5. View: Results and enhanced analysis")
    
    print("\n🔗 METHOD 2: API Call (Python)")
    print("-" * 30)
    print("""
import requests
import json

data = {
    'analyst': 'Your Name',
    'text': 'Your report content...'
}

response = requests.post(
    'http://localhost:5000/analyze',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(data)
)

result = response.json()
print(f"Report ID: {result['report_id']}")
    """)
    
    print("\n📋 METHOD 3: Direct Form Submission")
    print("-" * 30)
    print("Use the HTML form with POST to /analyze")
    print("Content-Type: application/json")
    print("Fields: analyst (string), text (string)")

if __name__ == "__main__":
    print("🚀 ENHANCED RESEARCH QUALITY ASSESSMENT SYSTEM")
    print("Report Submission Guide & Test")
    
    # Run the test
    test_report_submission()
    
    # Show submission methods
    show_submission_methods()
    
    print("\n🎉 READY TO USE!")
    print("Your system is ready to accept and analyze research reports!")
    print("🌐 Access at: http://localhost:5000")
