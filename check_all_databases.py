import sqlite3
import os
from datetime import datetime

databases = [
    'investment_research.db',
    'ml_ai_system.db', 
    'risk_management.db',
    'ml_dashboard.db',
    'test.db'
]

print("🗄️ Database Analysis Report")
print("=" * 60)

for db_name in databases:
    if os.path.exists(db_name):
        print(f"\n📊 {db_name}")
        print("-" * 40)
        
        stat = os.stat(db_name)
        size_kb = round(stat.st_size / 1024, 2)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        
        print(f"Size: {size_kb} KB | Modified: {modified}")
        
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            print(f"Tables: {len(tables)}")
            
            total_rows = 0
            for table_name, in tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                count = cursor.fetchone()[0]
                total_rows += count
                if count > 0:
                    print(f"  {table_name}: {count:,} rows")
            
            print(f"Total Rows: {total_rows:,}")
            conn.close()
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"\n❌ {db_name} - Not found")

print(f"\n🎯 Main Application Database: investment_research.db")
print("💾 Use this file for primary data backup and migration")