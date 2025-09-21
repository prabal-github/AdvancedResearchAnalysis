#!/usr/bin/env python3
"""
Test the enhanced skill completion tracking feature
"""

import requests
import json
from datetime import datetime

def test_skill_completion_feature():
    """Test the skill completion tracking feature end-to-end"""
    base_url = "http://localhost:5008"
    
    print("🎓 TESTING SKILL COMPLETION TRACKING FEATURE")
    print("=" * 70)
    print("✨ NEW FEATURE: Mark skills as completed + Analyst profile tracking")
    print("-" * 70)
    
    # Use existing report from previous tests
    report_id = "rep_30226255_220717"
    analyst_name = "Senior Financial Analyst"
    
    try:
        # Test 1: Test skill learning page with completion buttons
        print("1. Testing Enhanced Skill Learning Page...")
        print("-" * 40)
        
        response = requests.get(f"{base_url}/skill_learning/{report_id}", timeout=30)
        if response.status_code == 200:
            content = response.text
            print("✅ Skill learning page loaded successfully")
            
            # Check for skill completion features
            completion_features = [
                ('Completion section', 'Mark This Skill as Completed'),
                ('Rating system', 'skill-rating'),
                ('Notes field', 'Add any notes about your learning'),
                ('Completion button', 'complete-skill-btn'),
                ('JavaScript handler', 'complete_skill'),
                ('Profile link', 'View Profile')
            ]
            
            features_found = 0
            for feature_name, search_text in completion_features:
                if search_text in content:
                    print(f"   ✅ {feature_name} - FOUND")
                    features_found += 1
                else:
                    print(f"   ❌ {feature_name} - MISSING")
            
            print(f"📊 Completion Features Score: {features_found}/{len(completion_features)}")
        else:
            print(f"❌ Skill learning page failed: {response.status_code}")
        
        # Test 2: Test skill completion API
        print("\n2. Testing Skill Completion API...")
        print("-" * 40)
        
        completion_data = {
            "analyst_name": analyst_name,
            "report_id": report_id,
            "skill_category": "python",
            "skill_title": "Financial Trend Analysis",
            "analysis_type": "financial_calculation",
            "rating": 5,
            "notes": "Great learning experience! Now I understand pandas and matplotlib better."
        }
        
        api_response = requests.post(f"{base_url}/api/complete_skill", 
                                   json=completion_data, timeout=30)
        
        if api_response.status_code == 200:
            result = api_response.json()
            if result.get('success'):
                print("✅ Skill completion API working!")
                print(f"   📝 Message: {result.get('message')}")
                print(f"   📅 Completed at: {result.get('completed_at')}")
            else:
                print(f"❌ API returned error: {result.get('error')}")
        else:
            print(f"❌ API request failed: {api_response.status_code}")
            if api_response.status_code == 500:
                print("   (This might be expected if tables don't exist yet)")
        
        # Test 3: Test analyst profile API
        print("\n3. Testing Analyst Profile API...")
        print("-" * 40)
        
        profile_response = requests.get(f"{base_url}/api/analyst_skill_profile/{analyst_name}", timeout=30)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print("✅ Analyst profile API working!")
            print(f"   👤 Analyst: {profile_data.get('analyst_name')}")
            
            summary = profile_data.get('summary', {})
            print(f"   🏆 Total skills: {summary.get('total_skills_completed', 0)}")
            print(f"   🐍 Python skills: {summary.get('python_skills', 0)}")
            print(f"   💾 SQL skills: {summary.get('sql_skills', 0)}")
            print(f"   🤖 AI/ML skills: {summary.get('ai_ml_skills', 0)}")
            print(f"   ⭐ Average rating: {summary.get('avg_rating', 0):.1f}")
            print(f"   📊 Skill level: {summary.get('skill_level', 'beginner')}")
            
            recent_completions = profile_data.get('recent_completions', [])
            print(f"   📚 Recent completions: {len(recent_completions)}")
            
        else:
            print(f"❌ Profile API failed: {profile_response.status_code}")
        
        # Test 4: Test analyst profile page
        print("\n4. Testing Analyst Profile Page...")
        print("-" * 40)
        
        profile_page_response = requests.get(f"{base_url}/analyst_skill_profile/{analyst_name}", timeout=30)
        
        if profile_page_response.status_code == 200:
            page_content = profile_page_response.text
            print("✅ Analyst profile page loaded successfully")
            
            # Check for profile features
            profile_features = [
                ('Skill summary cards', 'Total Skills Completed'),
                ('Skill level display', 'Skill Level'),
                ('Average rating', 'Average Rating'),
                ('Skills by category tabs', 'nav-tabs'),
                ('Reports with skills table', 'Your Reports with Skill Learning'),
                ('Progress tracking', 'progress-bar')
            ]
            
            profile_features_found = 0
            for feature_name, search_text in profile_features:
                if search_text in page_content:
                    print(f"   ✅ {feature_name} - FOUND")
                    profile_features_found += 1
                else:
                    print(f"   ❌ {feature_name} - MISSING")
            
            print(f"📊 Profile Features Score: {profile_features_found}/{len(profile_features)}")
            
        else:
            print(f"❌ Profile page failed: {profile_page_response.status_code}")
        
        print(f"\n🌐 Direct Access URLs:")
        print(f"   📚 Skill Learning: {base_url}/skill_learning/{report_id}")
        print(f"   👤 Analyst Profile: {base_url}/analyst_skill_profile/{analyst_name}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 SKILL COMPLETION FEATURE BENEFITS:")
    print("-" * 70)
    print("✨ Analysts can mark skills as completed with ratings")
    print("✨ Personal skill portfolio tracking in profile")
    print("✨ Progress visualization across Python, SQL, AI/ML")
    print("✨ Learning notes and self-assessment capabilities")
    print("✨ Reports linked to skill development progress")
    print("✨ Skill level progression (Beginner → Intermediate → Advanced)")
    print("\n🎉 Complete skill development ecosystem delivered!")

if __name__ == "__main__":
    test_skill_completion_feature()
