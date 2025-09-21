#!/usr/bin/env python3
"""
Test script to verify the published models API pagination is working correctly
"""

import requests
import json

def test_api_pagination():
    """Test the API endpoint with different page sizes"""
    
    base_url = "http://127.0.0.1:5009/api/public/published_models"
    
    # Test different page sizes
    page_sizes = [25, 50, 100]
    
    print("Testing Published Models API Pagination")
    print("=" * 50)
    
    for page_size in page_sizes:
        try:
            url = f"{base_url}?page_size={page_size}&page=1"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok'):
                    print(f"\n📊 Page Size: {page_size}")
                    print(f"   Total models in database: {data.get('total', 'unknown')}")
                    print(f"   Models returned: {len(data.get('models', []))}")
                    print(f"   Total pages: {data.get('pages', 'unknown')}")
                    print(f"   Current page: {data.get('page', 'unknown')}")
                    
                    # Show a few model names as examples
                    models = data.get('models', [])
                    if models:
                        print(f"   Sample models:")
                        for model in models[:3]:
                            print(f"     - {model.get('name', 'Unknown')}")
                        if len(models) > 3:
                            print(f"     ... and {len(models) - 3} more")
                else:
                    print(f"❌ Page Size {page_size}: API returned error - {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Page Size {page_size}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Page Size {page_size}: Error - {e}")
    
    # Test pagination (second page with page_size=50)
    print(f"\n🔄 Testing Pagination (Page 2 with page_size=50)")
    try:
        url = f"{base_url}?page_size=50&page=2"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                models = data.get('models', [])
                print(f"   Page 2 models returned: {len(models)}")
                if models:
                    print(f"   First model on page 2: {models[0].get('name', 'Unknown')}")
            else:
                print(f"   Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   HTTP {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_api_pagination()
