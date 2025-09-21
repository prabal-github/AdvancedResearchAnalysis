#!/usr/bin/env python3
"""
Fix existing analyst profiles with NULL avg_quality_score values
"""

import sys
import sqlite3
from datetime import datetime

def fix_null_quality_scores():
    """Update existing analyst profiles to have default values"""
    print("🔧 FIXING NULL QUALITY SCORES")
    print("=" * 35)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db_path = 'investment_research.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current NULL values
        cursor.execute("SELECT COUNT(*) FROM analyst_profile WHERE avg_quality_score IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"📊 Found {null_count} analyst profiles with NULL avg_quality_score")
        
        if null_count > 0:
            # Update NULL values to 0.0
            cursor.execute("""
                UPDATE analyst_profile 
                SET avg_quality_score = 0.0 
                WHERE avg_quality_score IS NULL
            """)
            
            # Also ensure improvement_trend has a default value
            cursor.execute("""
                UPDATE analyst_profile 
                SET improvement_trend = 'New' 
                WHERE improvement_trend IS NULL OR improvement_trend = ''
            """)
            
            conn.commit()
            print(f"✅ Updated {null_count} analyst profiles")
            print("   • Set avg_quality_score to 0.0 for NULL values")
            print("   • Set improvement_trend to 'New' for empty values")
        else:
            print("✅ No NULL values found - all analyst profiles are properly initialized")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM analyst_profile WHERE avg_quality_score IS NULL")
        remaining_nulls = cursor.fetchone()[0]
        
        cursor.execute("SELECT name, avg_quality_score, improvement_trend FROM analyst_profile LIMIT 5")
        sample_data = cursor.fetchall()
        
        print(f"\n🔍 VERIFICATION:")
        print(f"   Remaining NULL values: {remaining_nulls}")
        print(f"   Sample analyst data:")
        for analyst in sample_data:
            score = analyst[1] if analyst[1] is not None else "NULL"
            trend = analyst[2] if analyst[2] else "Empty"
            print(f"     - {analyst[0]}: score={score}, trend={trend}")
        
        conn.close()
        
        if remaining_nulls == 0:
            print(f"\n🎉 SUCCESS: All analyst profiles now have proper default values!")
            return True
        else:
            print(f"\n⚠️  WARNING: {remaining_nulls} NULL values still remain")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing quality scores: {e}")
        return False

def main():
    print("🛠️  ANALYST PROFILE DATA FIX")
    print("=" * 50)
    
    success = fix_null_quality_scores()
    
    if success:
        print(f"\n📋 NEXT STEPS:")
        print("1. Restart Flask application")
        print("2. Test /analysts route")
        print("3. Verify no more TypeError on avg_quality_score")
    else:
        print(f"\n⚠️  MANUAL INTERVENTION MAY BE REQUIRED")

if __name__ == "__main__":
    main()