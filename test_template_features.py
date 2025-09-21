#!/usr/bin/env python3
"""
Test Script for New Research Template and AI Simulation Features
This script tests the new functionality to ensure everything works correctly.
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_flask_app_running(base_url="http://localhost:5008"):
    """Test if the Flask app is running"""
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✓ Flask application is running")
            return True
        else:
            print(f"✗ Flask app returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Flask application is not running: {e}")
        return False

def test_research_templates_page(base_url="http://localhost:5008"):
    """Test the research templates page"""
    try:
        response = requests.get(f"{base_url}/research_templates", timeout=10)
        if response.status_code == 200:
            print("✓ Research Templates page loads successfully")
            if "Research Templates" in response.text:
                print("✓ Research Templates page content is correct")
                return True
            else:
                print("✗ Research Templates page content missing")
                return False
        else:
            print(f"✗ Research Templates page returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access Research Templates page: {e}")
        return False

def test_ai_simulation_page(base_url="http://localhost:5008"):
    """Test the AI simulation page"""
    try:
        response = requests.get(f"{base_url}/ai_simulation", timeout=10)
        if response.status_code == 200:
            print("✓ AI Simulation page loads successfully")
            if "AI Simulation Engine" in response.text:
                print("✓ AI Simulation page content is correct")
                return True
            else:
                print("✗ AI Simulation page content missing")
                return False
        else:
            print(f"✗ AI Simulation page returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access AI Simulation page: {e}")
        return False

def run_quick_test():
    """Run a quick test to check if features are accessible"""
    print("=" * 50)
    print("TESTING NEW FEATURES")
    print("=" * 50)
    
    base_url = "http://localhost:5008"
    
    # Test if app is running
    if not test_flask_app_running(base_url):
        print("\n❌ Flask application is not running!")
        print("Please start the application with: python app.py")
        return False
    
    # Test if pages are accessible
    templates_ok = test_research_templates_page(base_url)
    simulation_ok = test_ai_simulation_page(base_url)
    
    print("\n" + "=" * 50)
    if templates_ok and simulation_ok:
        print("✅ ALL TESTS PASSED!")
        print("\nNew features are ready to use:")
        print("- Research Templates: /research_templates")
        print("- AI Simulation: /ai_simulation")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the error messages above.")
    
    print("=" * 50)
    return templates_ok and simulation_ok

if __name__ == '__main__':
    success = run_quick_test()
    exit(0 if success else 1)
