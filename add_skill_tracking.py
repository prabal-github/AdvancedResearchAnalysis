#!/usr/bin/env python3
"""
Add skill completion tracking to the database
"""

import sqlite3
import os
from datetime import datetime

def add_skill_tracking_tables():
    """Add tables for tracking analyst skill completions"""
    
    db_path = 'instance/research_reports.db'
    
    # Ensure instance directory exists
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    print("🎓 ADDING SKILL COMPLETION TRACKING TABLES")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Create skill_completions table
        print("1. Creating skill_completions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analyst_name VARCHAR(100) NOT NULL,
                report_id VARCHAR(32) NOT NULL,
                skill_category VARCHAR(50) NOT NULL,
                skill_title VARCHAR(200) NOT NULL,
                analysis_type VARCHAR(100) NOT NULL,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                UNIQUE(analyst_name, report_id, skill_category, analysis_type)
            )
        ''')
        
        # 2. Create analyst_skill_summary table for aggregated view
        print("2. Creating analyst_skill_summary table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyst_skill_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analyst_name VARCHAR(100) NOT NULL UNIQUE,
                total_skills_completed INTEGER DEFAULT 0,
                python_skills INTEGER DEFAULT 0,
                sql_skills INTEGER DEFAULT 0,
                ai_ml_skills INTEGER DEFAULT 0,
                avg_rating DECIMAL(3,2) DEFAULT 0.0,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                skill_level VARCHAR(20) DEFAULT 'beginner',
                achievements TEXT DEFAULT '[]'
            )
        ''')
        
        # 3. Create indexes for better performance
        print("3. Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_completions_analyst ON skill_completions(analyst_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_completions_report ON skill_completions(report_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_completions_category ON skill_completions(skill_category)')
        
        conn.commit()
        print("✅ Skill tracking tables created successfully!")
        
        # Check current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📋 Current database tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        conn.close()
    
    print("\n🎉 Skill completion tracking database ready!")

if __name__ == "__main__":
    add_skill_tracking_tables()
