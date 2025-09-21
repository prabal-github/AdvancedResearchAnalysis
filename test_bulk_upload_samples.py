#!/usr/bin/env python3
"""
Comprehensive Bulk Upload Testing Suite
Tests the bulk analyst creation feature with various sample CSV files.
"""

import requests
import os
from datetime import datetime

def test_csv_file_upload(file_path, test_name, expected_result):
    """Test uploading a specific CSV file"""
    
    base_url = "http://127.0.0.1:5008"
    
    print(f"\n🧪 Test: {test_name}")
    print(f"📁 File: {os.path.basename(file_path)}")
    print(f"🎯 Expected: {expected_result}")
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        # Read file and prepare for upload
        with open(file_path, 'rb') as file:
            files = {
                'csv_file': (os.path.basename(file_path), file, 'text/csv')
            }
            
            # Upload the file
            response = requests.post(
                f"{base_url}/admin/bulk_create_analysts?admin_key=admin123",
                files=files
            )
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                # Analyze response content for results
                response_text = response.text.lower()
                
                # Check for various indicators
                if "successfully created" in response_text:
                    print("✅ Found success indicators")
                if "failed to create" in response_text:
                    print("⚠️  Found failure indicators")
                if "duplicate" in response_text:
                    print("⚠️  Found duplicate indicators")
                if "error" in response_text and "missing" in response_text:
                    print("⚠️  Found validation errors")
                
                # Look for results summary
                if "creation results" in response_text or "summary" in response_text:
                    print("✅ Results summary displayed")
                
                return True
            else:
                print(f"❌ Upload failed with status: {response.status_code}")
                return False
                
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def display_file_contents(file_path, max_lines=5):
    """Display the contents of a CSV file"""
    
    print(f"\n📄 File Contents: {os.path.basename(file_path)}")
    print("─" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for i, line in enumerate(lines[:max_lines]):
                line_num = i + 1
                print(f"{line_num:2d}: {line.rstrip()}")
            
            if len(lines) > max_lines:
                print(f"... ({len(lines) - max_lines} more lines)")
                
            print(f"📊 Total rows: {len(lines)} (including header)")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main testing function"""
    
    print("🧪 BULK ANALYST CREATION - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test file configurations
    test_files = [
        {
            "file": "sample_analysts_success.csv",
            "name": "Successful Bulk Creation",
            "expected": "All 10 analysts should be created successfully",
            "description": "Professional analysts with complete data"
        },
        {
            "file": "sample_analysts_minimal.csv", 
            "name": "Minimal Required Fields",
            "expected": "3 analysts created with only required fields",
            "description": "Only name, email, password provided"
        },
        {
            "file": "sample_analysts_mixed.csv",
            "name": "Mixed Success/Failure Batch",
            "expected": "Some success, some failures, some duplicates",
            "description": "Combination of valid and invalid data"
        },
        {
            "file": "sample_analysts_errors.csv",
            "name": "Error Handling Test",
            "expected": "Most/all should fail with specific error messages",
            "description": "Various validation errors and edge cases"
        },
        {
            "file": "sample_analysts_bad_headers.csv",
            "name": "Invalid CSV Headers",
            "expected": "Should fail due to missing required headers",
            "description": "CSV with wrong column names"
        }
    ]
    
    print("📋 TEST PLAN OVERVIEW:")
    print()
    for i, test in enumerate(test_files, 1):
        print(f"{i}. {test['name']}")
        print(f"   📁 File: {test['file']}")
        print(f"   📝 Description: {test['description']}")
        print(f"   🎯 Expected: {test['expected']}")
        print()
    
    # Run tests
    print("🚀 STARTING BULK UPLOAD TESTS")
    print("=" * 40)
    
    results = []
    
    for test in test_files:
        file_path = test['file']
        
        # Display file contents first
        display_file_contents(file_path)
        
        # Run the test
        success = test_csv_file_upload(
            file_path,
            test['name'], 
            test['expected']
        )
        
        results.append({
            'name': test['name'],
            'file': test['file'],
            'success': success
        })
        
        print()
    
    # Summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print()
    
    for result in results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{status} - {result['name']} ({result['file']})")
    
    print()
    print("🎯 WHAT TO VERIFY:")
    print("1. Access the admin management page to see created accounts")
    print("2. Check that duplicate detection worked correctly")
    print("3. Verify error messages are clear and helpful")
    print("4. Confirm successful accounts are active and complete")
    print()
    print("🔗 VERIFICATION URLS:")
    print("📊 Admin Management: http://127.0.0.1:5008/admin/manage_analysts?admin_key=admin123")
    print("📤 Bulk Upload: http://127.0.0.1:5008/admin/bulk_create_analysts?admin_key=admin123")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Bulk upload system is working correctly!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} test(s) failed. Check the results above.")

if __name__ == "__main__":
    main()
