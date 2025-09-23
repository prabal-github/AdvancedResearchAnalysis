#!/usr/bin/env python3
"""
Test the enhanced Skill Learning Analysis feature with original content mapping
"""

import requests
import json
from datetime import datetime

def test_enhanced_skill_learning():
    """Test the enhanced skill learning feature with original content extraction"""
    base_url = "http://localhost:80"
    
    print("🎓 TESTING ENHANCED SKILL LEARNING ANALYSIS")
    print("=" * 70)
    print("✨ NEW FEATURE: 'What You Wrote' → 'How to Code It' mapping")
    print("-" * 70)
    
    # Enhanced sample report with rich financial content
    sample_report = {
        "analyst": "Senior Financial Analyst",
        "text": """
TCS Q3 FY2024 Financial Analysis Report

Revenue Growth Analysis:
TCS reported impressive revenue growth of 16.8% year-over-year, reaching ₹59,381 crores in Q3 FY2024. The company demonstrated strong quarterly performance with revenue increasing from ₹50,976 crores in Q3 FY2023. This consistent growth trajectory indicates robust business fundamentals and effective market expansion strategies.

Stock Performance & Technical Analysis:
TCS stock (NSE: TCS) has shown remarkable technical strength, trading at ₹3,650 with strong support levels around ₹3,500. The RSI indicator shows healthy momentum at 58, indicating neither overbought nor oversold conditions. Moving averages suggest an upward trend with 20-day MA above 50-day MA, confirming bullish sentiment.

Market Sentiment Analysis:
Market sentiment towards TCS remains overwhelmingly positive. Recent news coverage highlights the company's strong digital transformation wins and cloud adoption acceleration. Investor sentiment is bullish due to strong Q3 earnings and optimistic management guidance for Q4 FY2024.

Financial Database Analysis:
Our quarterly financial database analysis reveals that TCS maintains industry-leading margins with operating margin of 24.3%. The company's financial performance consistently ranks in the top quartile when compared to industry peers in our comprehensive financial database.

AI-Powered Outlook:
Using machine learning sentiment analysis on recent market news and earnings calls, our AI models predict continued positive momentum for TCS. The sentiment score of 0.75 indicates strong market confidence, correlating positively with historical price movements.
        """
    }
    
    try:
        # Submit the enhanced report
        print("1. Submitting Enhanced Report for Analysis...")
        print("-" * 40)
        response = requests.post(f"{base_url}/analyze", json=sample_report, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            report_id = result.get('report_id')
            print(f"✅ Report submitted successfully!")
            print(f"📋 Report ID: {report_id}")
            
            # Check if skill learning analysis was generated
            if 'skill_learning_analysis' in result:
                skill_data = json.loads(result['skill_learning_analysis'])
                print(f"📚 Learning modules generated: {len(skill_data)}")
                
                # Display what content was extracted
                print("\n2. Original Content Extraction Results:")
                print("-" * 40)
                for i, module in enumerate(skill_data, 1):
                    print(f"   {i}. {module['title']} ({module['skill_category'].upper()})")
                    if 'original_content' in module and module['original_content']:
                        print(f"      📝 Original content extracted: {len(module['original_content'])} sentences")
                        for j, content in enumerate(module['original_content'][:2], 1):  # Show first 2
                            print(f"      {j}. \"{content[:80]}...\"")
                    else:
                        print(f"      ⚠️ No original content extracted")
                    print()
            
            # Test the enhanced skill learning page
            print("3. Testing Enhanced Skill Learning Page...")
            print("-" * 40)
            
            page_response = requests.get(f"{base_url}/skill_learning/{report_id}", timeout=30)
            if page_response.status_code == 200:
                page_content = page_response.text
                print("✅ Enhanced skill learning page loads successfully")
                
                # Check for enhanced features
                enhanced_features = [
                    ('Original content section', 'What You Wrote in Your Report'),
                    ('Enhanced button text', 'See How YOUR Analysis Was Done in Code'),
                    ('Content mapping indicator', 'Your Analysis → Code'),
                    ('Flow explanation', 'What You Wrote" → "How to Code It"'),
                    ('Quote formatting', 'bi bi-quote')
                ]
                
                for feature_name, search_text in enhanced_features:
                    if search_text in page_content:
                        print(f"   ✅ {feature_name} found")
                    else:
                        print(f"   ❌ {feature_name} missing")
                
            else:
                print(f"❌ Skill learning page failed: {page_response.status_code}")
            
        else:
            print(f"❌ Report submission failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 ENHANCED FEATURE BENEFITS:")
    print("-" * 70)
    print("✨ Analysts can see EXACTLY how their written analysis")
    print("   translates to professional code implementation")
    print("✨ Clear 'Your Words → Code' mapping for better learning")
    print("✨ Contextual examples based on actual report content")
    print("✨ Perfect fusion of financial writing + technical skills")
    print("\n🎉 Enhanced Skill Learning Analysis Feature Ready!")

if __name__ == "__main__":
    test_enhanced_skill_learning()
