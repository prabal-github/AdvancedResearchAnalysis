#!/usr/bin/env python3
"""
Test Risk Management Integration with VS Terminal AClass
Validates that the risk management system is properly integrated into the main terminal interface.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://127.0.0.1:80"
VS_TERMINAL_URL = f"{BASE_URL}/vs_terminal_AClass"
RISK_MANAGEMENT_API_BASE = f"{BASE_URL}/api/vs_terminal_AClass/risk_management"

def test_vs_terminal_access():
    """Test that VS Terminal AClass is accessible"""
    print("🔍 Testing VS Terminal AClass access...")
    try:
        response = requests.get(VS_TERMINAL_URL, timeout=10)
        if response.status_code == 200:
            print("✅ VS Terminal AClass is accessible")
            # Check if risk management tab is present
            if 'Risk Management' in response.text:
                print("✅ Risk Management tab found in VS Terminal interface")
                return True
            else:
                print("❌ Risk Management tab not found in interface")
                return False
        else:
            print(f"❌ VS Terminal AClass not accessible (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error accessing VS Terminal: {e}")
        return False

def test_risk_management_endpoints():
    """Test risk management API endpoints"""
    print("\n🔍 Testing Risk Management API endpoints...")
    
    endpoints = [
        ("/comprehensive_analysis", "POST"),
        ("/agent_status", "GET"),
        ("/stress_test", "POST"),
        ("/advisor_query", "POST"),
        ("/risk_alerts", "GET")
    ]
    
    results = []
    
    for endpoint, method in endpoints:
        url = f"{RISK_MANAGEMENT_API_BASE}{endpoint}"
        print(f"  Testing {method} {endpoint}...")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                # POST with minimal test data
                test_data = {
                    "query": "Test risk analysis",
                    "scenario_type": "market_crash",
                    "timeframe": "1W"
                }
                response = requests.post(url, json=test_data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"    ✅ {endpoint} - OK")
                results.append(True)
            else:
                print(f"    ⚠️ {endpoint} - Status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"    ❌ {endpoint} - Error: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 API Endpoints Success Rate: {success_rate:.1f}%")
    return success_rate > 60  # Consider success if >60% endpoints work

def test_risk_dashboard_components():
    """Test that risk dashboard components are properly integrated"""
    print("\n🔍 Testing Risk Dashboard Integration...")
    
    try:
        response = requests.get(VS_TERMINAL_URL, timeout=10)
        content = response.text
        
        # Check for key risk management elements
        required_elements = [
            'upperTabBtn-risk',  # Risk tab button
            'upperTab-risk',     # Risk tab content
            'loadRiskDashboard', # JavaScript function
            'activateAllAgents', # AI agents function
            'riskChatMessages',  # Chat interface
            'riskMatrixTable'    # Risk matrix table
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
                print(f"    ✅ Found: {element}")
            else:
                print(f"    ❌ Missing: {element}")
        
        integration_score = len(found_elements) / len(required_elements) * 100
        print(f"\n📊 Integration Completeness: {integration_score:.1f}%")
        return integration_score > 80
        
    except Exception as e:
        print(f"❌ Error testing dashboard integration: {e}")
        return False

def test_ai_agents_functionality():
    """Test AI agents activation and response"""
    print("\n🔍 Testing AI Agents Functionality...")
    
    try:
        # Test agent status
        status_url = f"{RISK_MANAGEMENT_API_BASE}/agent_status"
        response = requests.get(status_url, timeout=15)
        
        if response.status_code == 200:
            print("✅ AI Agents status endpoint responding")
            
            # Test advisor query
            advisor_url = f"{RISK_MANAGEMENT_API_BASE}/advisor_query"
            advisor_data = {
                "query": "What is my portfolio risk level?",
                "context": "risk_analysis"
            }
            
            advisor_response = requests.post(advisor_url, json=advisor_data, timeout=15)
            if advisor_response.status_code == 200:
                try:
                    advisor_result = advisor_response.json()
                    if advisor_result.get('status') == 'success':
                        print("✅ AI Advisor query is functional")
                        return True
                    else:
                        print("⚠️ AI Advisor returned non-success status")
                        return False
                except:
                    print("⚠️ AI Advisor response format issue")
                    return False
            else:
                print(f"❌ AI Advisor query failed (status: {advisor_response.status_code})")
                return False
        else:
            print(f"❌ AI Agents status check failed (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI agents: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Risk Management Integration Tests")
    print("=" * 60)
    
    tests = [
        ("VS Terminal Access", test_vs_terminal_access),
        ("API Endpoints", test_risk_management_endpoints), 
        ("Dashboard Components", test_risk_dashboard_components),
        ("AI Agents", test_ai_agents_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running Test: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"🏁 {test_name}: {status}")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<25} {status}")
    
    print(f"\n🎯 Overall Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Risk Management is fully integrated.")
    elif passed >= total * 0.75:
        print("✅ Most tests passed. Risk Management is mostly functional.")
    else:
        print("⚠️ Some issues found. Please review the integration.")
    
    print(f"\n🌐 Access your integrated Risk Management at:")
    print(f"   {VS_TERMINAL_URL}")
    print(f"   Click the 'Risk Management' tab in the upper navigation")

if __name__ == "__main__":
    main()
