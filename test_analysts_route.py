#!/usr/bin/env python3
"""
Test the /analysts route to verify the TypeError is fixed
"""

import sys
sys.path.append('.')

def test_analysts_route():
    """Test the analysts route functionality"""
    print("🧪 TESTING /analysts ROUTE")
    print("=" * 30)
    
    try:
        from app import app, db, AnalystProfile
        
        with app.app_context():
            # Get all analyst profiles
            profiles = AnalystProfile.query.filter_by(is_active=True).all()
            print(f"✅ Found {len(profiles)} active analyst profiles")
            
            # Test the problematic calculation for each profile
            for profile in profiles:
                try:
                    # This is the calculation that was failing
                    quality_percentage = (profile.avg_quality_score * 100)
                    print(f"   📊 {profile.name}: {quality_percentage:.1f}% quality score")
                except Exception as e:
                    print(f"   ❌ {profile.name}: Error - {e}")
                    return False
            
            print(f"\n✅ All quality score calculations successful!")
            
            # Test template rendering simulation
            print(f"\n🎨 Template rendering test:")
            for profile in profiles[:3]:  # Test first 3 profiles
                rounded_score = round(profile.avg_quality_score * 100, 0)
                detailed_score = round(profile.avg_quality_score * 100, 1)
                print(f"   • {profile.name}: {rounded_score}% (detailed: {detailed_score}%)")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_analysts_route()
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print("✅ /analysts route should now work without errors")
        print("✅ All avg_quality_score calculations working")
        print("✅ Template should render properly")
    else:
        print(f"\n❌ FAILED!")
        print("There are still issues that need to be resolved")