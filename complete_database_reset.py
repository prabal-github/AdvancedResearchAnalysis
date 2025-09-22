#!/usr/bin/env python3
"""
Complete Database Reset for EC2 Deployment
==========================================
This script completely recreates the database with proper schema.
"""

import os
import sys
import sqlite3
from pathlib import Path

def reset_database():
    """Reset the database completely"""
    print("🔧 Complete Database Reset")
    print("=" * 40)
    
    db_path = "research.db"
    backup_path = "research_backup.db"
    
    try:
        # Backup existing database
        if os.path.exists(db_path):
            print(f"📋 Backing up existing database to {backup_path}")
            os.rename(db_path, backup_path)
        
        # Create new database with proper schema
        print("🗄️ Creating new database with complete schema...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create analyst_profile table with ALL required columns
        cursor.execute("""
        CREATE TABLE analyst_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            full_name VARCHAR(200),
            email VARCHAR(120) UNIQUE NOT NULL,
            phone VARCHAR(20),
            password_hash VARCHAR(255) NOT NULL,
            analyst_id VARCHAR(50) UNIQUE,
            last_login DATETIME,
            login_count INTEGER DEFAULT 0,
            university_name VARCHAR(200),
            age INTEGER,
            date_of_birth DATE,
            department VARCHAR(100),
            specialization VARCHAR(200),
            experience_years INTEGER,
            certifications TEXT,
            specializations TEXT,
            sebi_registration VARCHAR(100),
            bio TEXT,
            brief_description TEXT,
            profile_image VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            plan VARCHAR(50) DEFAULT 'free',
            daily_usage_date DATE,
            daily_usage_count INTEGER DEFAULT 0,
            plan_notes TEXT,
            plan_expires_at DATETIME,
            daily_llm_prompt_count INTEGER DEFAULT 0,
            daily_llm_token_count INTEGER DEFAULT 0,
            daily_run_count INTEGER DEFAULT 0,
            corporate_field VARCHAR(100),
            field_specialization VARCHAR(200),
            talent_program_level VARCHAR(50),
            total_reports INTEGER DEFAULT 0,
            avg_quality_score FLOAT DEFAULT 0.0,
            improvement_trend VARCHAR(20) DEFAULT 'stable',
            last_report_date DATETIME
        );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_analyst_email ON analyst_profile(email);")
        cursor.execute("CREATE INDEX idx_analyst_id ON analyst_profile(analyst_id);")
        cursor.execute("CREATE INDEX idx_analyst_active ON analyst_profile(is_active);")
        
        # Recreate other essential tables that might exist
        other_tables = [
            """CREATE TABLE IF NOT EXISTS contact_form_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                email VARCHAR(120),
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""",
            
            """CREATE TABLE IF NOT EXISTS ml_model_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name VARCHAR(100),
                result_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""",
            
            """CREATE TABLE IF NOT EXISTS script_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_name VARCHAR(100),
                execution_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
        ]
        
        for table_sql in other_tables:
            cursor.execute(table_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ New database created successfully!")
        
        # Verify the phone column exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(analyst_profile);")
        columns = cursor.fetchall()
        
        print(f"\n📋 analyst_profile columns:")
        phone_found = False
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            print(f"  • {col_name} ({col_type})")
            if col_name == 'phone':
                phone_found = True
        
        conn.close()
        
        if phone_found:
            print("✅ Phone column confirmed in new database!")
            return True
        else:
            print("❌ Phone column still missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("\n🎉 Database reset completed successfully!")
        print("Now run: python ec2_database_fix.py")
        sys.exit(0)
    else:
        print("\n❌ Database reset failed!")
        sys.exit(1)