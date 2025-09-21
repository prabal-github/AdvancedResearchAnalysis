import requests

try:
    response = requests.get('http://127.0.0.1:5008/investor/scripts/BTSTjson.py')
    html_content = response.text
    
    print("📄 Response Status Code:", response.status_code)
    print("📄 Response Headers:", dict(response.headers))
    print("\n🔍 First 1000 characters of response:")
    print("=" * 50)
    print(html_content[:1000])
    print("=" * 50)
    
    print("\n🔍 Last 500 characters of response:")
    print("=" * 50)
    print(html_content[-500:])
    print("=" * 50)
    
    # Check for redirect patterns
    if 'login' in html_content.lower() or 'redirect' in html_content.lower():
        print("⚠️ Possible redirect to login page detected")
        
    # Check for error patterns
    if 'error' in html_content.lower() or 'exception' in html_content.lower():
        print("⚠️ Possible error in response")
        
except Exception as e:
    print(f"❌ Error: {e}")
