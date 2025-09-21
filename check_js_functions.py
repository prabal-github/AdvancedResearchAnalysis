import requests

try:
    response = requests.get('http://127.0.0.1:5008/investor/scripts/BTSTjson.py')
    html_content = response.text
    
    if 'loadEnhancedAnalysis' in html_content:
        print("✅ loadEnhancedAnalysis function found in HTML")
    else:
        print("❌ loadEnhancedAnalysis function NOT found in HTML")
        
    if 'loadLatestInsights' in html_content:
        print("✅ loadLatestInsights function found in HTML")
    else:
        print("❌ loadLatestInsights function NOT found in HTML")
        
    if 'loadAi' in html_content:
        print("✅ loadAi function found in HTML")
    else:
        print("❌ loadAi function NOT found in HTML")
        
    # Check if template is being rendered properly
    if 'investor_script_detail.html' in html_content or 'Latest Result' in html_content:
        print("✅ Template appears to be rendering correctly")
    else:
        print("❌ Template may not be rendering correctly")
        
    # Check for script tags
    script_count = html_content.count('<script>')
    print(f"📝 Found {script_count} <script> tags in HTML")
    
    # Look for error patterns
    if 'Error' in html_content[:500]:
        print("⚠️ Possible error in HTML start")
        print("First 500 chars:", html_content[:500])
        
except Exception as e:
    print(f"❌ Error checking page: {e}")
