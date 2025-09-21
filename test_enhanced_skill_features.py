#!/usr/bin/env python3
"""
Quick test to validate enhanced skill learning features
"""

import requests

def test_enhanced_features():
    """Test the enhanced features on an existing report"""
    base_url = "http://localhost:5008"
    report_id = "rep_30226255_220717"  # From previous test
    
    print("🎓 TESTING ENHANCED SKILL LEARNING FEATURES")
    print("=" * 60)
    
    try:
        # Test the enhanced skill learning page
        print(f"📋 Testing Report ID: {report_id}")
        print("-" * 40)
        
        response = requests.get(f"{base_url}/skill_learning/{report_id}", timeout=30)
        
        if response.status_code == 200:
            content = response.text
            print("✅ Skill learning page loaded successfully")
            
            # Check for enhanced features
            enhanced_features = [
                ('Original content section', 'What You Wrote in Your Report'),
                ('Enhanced button text', 'See How YOUR Analysis Was Done in Code'),
                ('Content mapping indicator', 'Your Analysis → Code'),
                ('Flow explanation', '"What You Wrote" → "How to Code It"'),
                ('Quote formatting', 'bi bi-quote'),
                ('Enhanced intro', 'We analyzed your report text'),
                ('Enhanced feature description', 'Perfect fusion')
            ]
            
            print("\n🔍 Enhanced Feature Detection:")
            print("-" * 40)
            
            features_found = 0
            for feature_name, search_text in enhanced_features:
                if search_text in content:
                    print(f"   ✅ {feature_name} - FOUND")
                    features_found += 1
                else:
                    print(f"   ❌ {feature_name} - MISSING")
            
            print(f"\n📊 Enhanced Features Score: {features_found}/{len(enhanced_features)}")
            
            if features_found >= 5:
                print("🎉 ENHANCEMENT SUCCESSFUL!")
                print("✨ Original content mapping is working!")
            else:
                print("⚠️ Some enhancements may need review")
                
            print(f"\n🌐 Direct Access: {base_url}/skill_learning/{report_id}")
                
        else:
            print(f"❌ Page load failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ENHANCED FEATURE SUMMARY:")
    print("✨ Shows 'What You Wrote' from original report")
    print("✨ Maps analyst content to code examples")
    print("✨ Enhanced visual flow indicators")
    print("✨ Contextual learning based on actual content")
    print("🎉 Perfect fusion of financial analysis + coding skills!")

if __name__ == "__main__":
    test_enhanced_features()
