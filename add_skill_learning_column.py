#!/usr/bin/env python3
"""
Add skill learning analysis column to reports table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_skill_learning_column():
    """Add skill_learning_analysis column to the reports table"""
    try:
        with app.app_context():
            # Check if column already exists
            result = db.session.execute(db.text("PRAGMA table_info(report)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'skill_learning_analysis' not in columns:
                print("Adding skill_learning_analysis column to report table...")
                db.session.execute(db.text("ALTER TABLE report ADD COLUMN skill_learning_analysis TEXT"))
                db.session.commit()
                print("✅ Successfully added skill_learning_analysis column")
            else:
                print("✅ skill_learning_analysis column already exists")
            
            # Verify the addition
            result = db.session.execute(db.text("PRAGMA table_info(report)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Current report table columns: {columns}")
            
    except Exception as e:
        print(f"❌ Error adding skill_learning_analysis column: {e}")
        db.session.rollback()

if __name__ == "__main__":
    print("🔧 ADDING SKILL LEARNING ANALYSIS COLUMN")
    print("=" * 50)
    add_skill_learning_column()
    print("\n🎉 Database migration completed!")
