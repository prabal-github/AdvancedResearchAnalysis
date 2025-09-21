#!/usr/bin/env python3
"""Test script to verify subscription flow and debug catalog/ML Class integration."""

import requests
import json

BASE_URL = "http://127.0.0.1:5008"

def test_subscription_flow():
    """Test the complete subscription flow from catalog to ML Class."""
    print("=== Testing Subscription Flow ===\n")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # 1. Check current subscriptions
    print("1. Current subscriptions:")
    resp = session.get(f"{BASE_URL}/api/catalog/subscriptions")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            subs = resp.json()
            print(f"   Data: {json.dumps(subs, indent=2)}")
        except Exception as e:
            print(f"   JSON Error: {e}")
            print(f"   Raw content: {resp.text[:200]}")
    else:
        print(f"   Error: {resp.text[:200]}")
    
    # 2. Get available agents and models from catalog
    print("\n2. Available catalog agents:")
    resp = session.get(f"{BASE_URL}/api/catalog/agents")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            agents = resp.json()
            print(f"   Agents: {[a['id'] for a in agents.get('agents', [])]}")
        except Exception as e:
            print(f"   JSON Error: {e}")
    
    print("\n3. Available catalog models:")
    resp = session.get(f"{BASE_URL}/api/catalog/models")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            models = resp.json()
            print(f"   Models: {[m['id'] for m in models.get('models', [])]}")
        except Exception as e:
            print(f"   JSON Error: {e}")
    
    # 3. Subscribe to some items
    print("\n4. Subscribing to portfolio_risk_monitor agent:")
    resp = session.post(f"{BASE_URL}/api/catalog/subscribe", 
                        json={"type": "agent", "id": "portfolio_risk_monitor"})
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            print(f"   Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"   Raw response: {resp.text}")
    else:
        print(f"   Error: {resp.text}")
    
    print("\n5. Subscribing to volatility_garch model:")
    resp = session.post(f"{BASE_URL}/api/catalog/subscribe", 
                        json={"type": "model", "id": "volatility_garch"})
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            print(f"   Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"   Raw response: {resp.text}")
    else:
        print(f"   Error: {resp.text}")
    
    # 4. Check subscriptions again
    print("\n6. Updated subscriptions:")
    resp = session.get(f"{BASE_URL}/api/catalog/subscriptions")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            subs = resp.json()
            print(f"   Data: {json.dumps(subs, indent=2)}")
        except:
            print(f"   Raw response: {resp.text[:200]}")
    
    # 5. Set a fake session to test ML Class endpoint
    print("\n7. Setting fake investor session...")
    # First visit a page to get session cookie
    session.get(f"{BASE_URL}/")
    
    # Try to set session manually (this won't work without proper login)
    print("\n8. ML Class subscribed endpoint:")
    resp = session.get(f"{BASE_URL}/api/vs_terminal_MLClass/subscribed")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            ml_subs = resp.json()
            print(f"   Mode: {ml_subs.get('mode')}")
            print(f"   Agents: {[a['id'] for a in ml_subs.get('agents', [])]}")
            print(f"   Models: {[m['id'] for m in ml_subs.get('models', [])]}")
            print(f"   Raw subscriptions: {ml_subs.get('raw_subscriptions')}")
        except:
            print(f"   Raw response: {resp.text[:200]}")
    else:
        print(f"   Error: {resp.status_code} - {resp.text[:200]}")
    
    # 6. Check if subscription file exists
    print("\n9. Checking subscription file:")
    try:
        with open('catalog_subscriptions.json', 'r') as f:
            file_content = json.load(f)
            print(f"   File content: {json.dumps(file_content, indent=2)}")
    except FileNotFoundError:
        print("   File not found")
    except Exception as e:
        print(f"   Error reading file: {e}")

if __name__ == "__main__":
    test_subscription_flow()
