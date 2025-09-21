import sqlite3
import os

# Check all database files for certificate tables
db_files = ['investment_research.db', 'test.db', 'ml_ai_system.db', 'ml_dashboard.db']

for db_file in db_files:
    if os.path.exists(db_file):
        print(f"\n=== {db_file} ===")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"Tables: {tables}")
            
            # Check specifically for certificate related tables
            cert_tables = [t for t in tables if 'certificate' in t.lower()]
            if cert_tables:
                print(f"Certificate tables found: {cert_tables}")
                
                # Check structure of certificate tables
                for table in cert_tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    print(f"\n{table} columns:")
                    for col in columns:
                        print(f"  {col[1]} ({col[2]})")
            
            conn.close()
        except Exception as e:
            print(f"Error reading {db_file}: {e}")