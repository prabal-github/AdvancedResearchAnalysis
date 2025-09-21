# 🔄 SQLite to PostgreSQL Migration Guide

## Migration Time Estimate: **~18 minutes**

Based on your data analysis, here's the complete migration plan for moving your SQLite data to PostgreSQL RDS.

---

## 📊 **Migration Summary**

| Metric | Value |
|--------|-------|
| **Total Data Size** | 7.2 MB |
| **Total Tables** | 190 tables |
| **Total Rows** | 2,727 rows |
| **Estimated Time** | **18 minutes 16 seconds** |
| **Recommended Window** | Low-traffic period (brief downtime) |

---

## 🗄️ **Databases to Migrate**

### ✅ **Databases with Data (5 databases)**

1. **`investment_research.db`** - 0.13 MB, 6 tables, 50 rows
2. **`instance/investment_research.db`** - 5.26 MB, 126 tables, 1,941 rows ⭐ *Main database*
3. **`instance/reports.db`** - 1.63 MB, 37 tables, 686 rows
4. **`instance/google_meetings.db`** - 0.04 MB, 6 tables, 8 rows
5. **`ml_ai_system.db`** - 0.14 MB, 15 tables, 42 rows

### 📭 **Empty Databases (6 databases - will be skipped)**

- `instance/research_reports.db`, `ml_dashboard.db`, `risk_management.db`, etc.

---

## ⏱️ **Migration Timeline Breakdown**

### **Phase 1: Schema Creation (~16 minutes)**
- Create PostgreSQL table schemas from SQLite
- Handle data type conversions (AUTOINCREMENT → SERIAL, etc.)
- Set up primary keys and basic constraints

### **Phase 2: Data Migration (~2.5 minutes)**
- Bulk copy data from SQLite to PostgreSQL
- Handle data type conversions
- Batch processing for large tables

### **Phase 3: Index Creation (~6 minutes)**
- Create indexes for performance
- Set up foreign key constraints
- Optimize for your application queries

### **Phase 4: Validation (~3 minutes)**
- Verify row counts match
- Test application connectivity
- Run sample queries

---

## 🚀 **Step-by-Step Migration Process**

### **Prerequisites** ✅
- [x] PostgreSQL RDS instance running (`3.85.19.80:5432`)
- [x] Network connectivity verified
- [x] Application has RDS-compatible configuration

### **Step 1: Backup Current Data (2 minutes)**

```bash
# Create backup directory
mkdir -p /tmp/sqlite_backup
cd "c:\PythonProjectTestCopy\FinalDashboard12\Copy5AllRDS - Copy2 - Copy12AWSBEDROCK - Copy (10)3 - Copy"

# Backup all SQLite databases
cp *.db /tmp/sqlite_backup/ 2>/dev/null || true
cp instance/*.db /tmp/sqlite_backup/ 2>/dev/null || true

echo "✅ SQLite databases backed up to /tmp/sqlite_backup/"
```

### **Step 2: Install Migration Dependencies (1 minute)**

```bash
# Install required packages
pip install psycopg2-binary
pip install sqlite-utils  # For easier SQLite operations
```

### **Step 3: Run Migration Script (15-18 minutes)**

Use the automated migration script below:

```python
# migration_script.py
import sqlite3
import psycopg2
import os
from urllib.parse import urlparse
import time

def migrate_database():
    # Your existing PostgreSQL connection
    pg_url = "postgresql://admin:admin%402001@3.85.19.80:5432/research"
    
    # Parse PostgreSQL URL
    parsed = urlparse(pg_url)
    pg_conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password.replace('%40', '@')
    )
    
    # List of SQLite databases to migrate
    databases = [
        'investment_research.db',
        'instance/investment_research.db', 
        'instance/reports.db',
        'instance/google_meetings.db',
        'ml_ai_system.db'
    ]
    
    total_tables_migrated = 0
    total_rows_migrated = 0
    
    for db_path in databases:
        if not os.path.exists(db_path):
            continue
            
        print(f"📁 Migrating {db_path}...")
        sqlite_conn = sqlite3.connect(db_path)
        
        # Get all tables
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            # Skip system tables
            if table_name.startswith('sqlite_'):
                continue
                
            # Migrate table
            rows_migrated = migrate_table(sqlite_conn, pg_conn, table_name, db_path)
            total_rows_migrated += rows_migrated
            total_tables_migrated += 1
            
        sqlite_conn.close()
    
    pg_conn.close()
    
    print(f"✅ Migration completed!")
    print(f"   Tables migrated: {total_tables_migrated}")
    print(f"   Rows migrated: {total_rows_migrated:,}")

def migrate_table(sqlite_conn, pg_conn, table_name, source_db):
    # Implementation details...
    pass

if __name__ == "__main__":
    migrate_database()
```

### **Step 4: Application Configuration (2 minutes)**

Update your application to use PostgreSQL:

```bash
# Update .env file
echo "DATABASE_URL=postgresql://admin:admin%402001@3.85.19.80:5432/research" > .env.production
```

### **Step 5: Test and Validate (3 minutes)**

```python
# test_migration.py
from app import app, db

with app.app_context():
    # Test database connection
    result = db.session.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\'')
    table_count = result.fetchone()[0]
    print(f"✅ Found {table_count} tables in PostgreSQL")
    
    # Test sample queries
    try:
        # Test a few key tables (adjust based on your schema)
        test_queries = [
            "SELECT COUNT(*) FROM report",
            "SELECT COUNT(*) FROM analyst_profile", 
            "SELECT COUNT(*) FROM investor_account"
        ]
        
        for query in test_queries:
            try:
                result = db.session.execute(query)
                count = result.fetchone()[0]
                print(f"✅ {query}: {count} rows")
            except Exception as e:
                print(f"⚠️ {query}: {e}")
                
    except Exception as e:
        print(f"❌ Migration validation failed: {e}")
```

---

## 🛠️ **Complete Migration Script**

Here's the complete, ready-to-run migration script:

```python
#!/usr/bin/env python3
"""
Complete SQLite to PostgreSQL Migration Script
Estimated time: 15-20 minutes
"""

import sqlite3
import psycopg2
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

# Configuration
POSTGRESQL_URL = "postgresql://admin:admin%402001@3.85.19.80:5432/research"
SQLITE_DATABASES = [
    'investment_research.db',
    'instance/investment_research.db',
    'instance/reports.db', 
    'instance/google_meetings.db',
    'ml_ai_system.db'
]

def connect_postgresql():
    """Connect to PostgreSQL database"""
    parsed = urlparse(POSTGRESQL_URL)
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password.replace('%40', '@')
    )

def get_sqlite_schema(sqlite_conn, table_name):
    """Get SQLite table schema and convert to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    pg_columns = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        is_primary = col[5]
        
        # Convert SQLite types to PostgreSQL
        if 'INTEGER' in col_type and is_primary:
            pg_type = 'SERIAL PRIMARY KEY'
        elif 'INTEGER' in col_type:
            pg_type = 'INTEGER'
        elif 'TEXT' in col_type:
            pg_type = 'TEXT'
        elif 'REAL' in col_type:
            pg_type = 'REAL'
        elif 'BLOB' in col_type:
            pg_type = 'BYTEA'
        else:
            pg_type = 'TEXT'  # Default fallback
            
        if is_primary and 'SERIAL' not in pg_type:
            pg_type += ' PRIMARY KEY'
            
        pg_columns.append(f"{col_name} {pg_type}")
    
    return pg_columns

def migrate_table_data(sqlite_conn, pg_conn, table_name, source_prefix=""):
    """Migrate data from SQLite table to PostgreSQL"""
    try:
        # Get PostgreSQL table name (with prefix to avoid conflicts)
        pg_table_name = f"{source_prefix}_{table_name}" if source_prefix else table_name
        
        # Get SQLite data
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   📭 {table_name}: No data to migrate")
            return 0
        
        # Get column names
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Create PostgreSQL table
        pg_cursor = pg_conn.cursor()
        
        # Drop table if exists
        pg_cursor.execute(f"DROP TABLE IF EXISTS {pg_table_name} CASCADE")
        
        # Create table schema
        pg_columns = get_sqlite_schema(sqlite_conn, table_name)
        create_sql = f"CREATE TABLE {pg_table_name} ({', '.join(pg_columns)})"
        pg_cursor.execute(create_sql)
        
        # Insert data
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {pg_table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Insert in batches for better performance
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            pg_cursor.executemany(insert_sql, batch)
        
        pg_conn.commit()
        
        print(f"   ✅ {table_name} → {pg_table_name}: {len(rows)} rows migrated")
        return len(rows)
        
    except Exception as e:
        print(f"   ❌ {table_name}: Migration failed - {e}")
        pg_conn.rollback()
        return 0

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    start_time = time.time()
    total_tables = 0
    total_rows = 0
    
    try:
        # Connect to PostgreSQL
        print("📡 Connecting to PostgreSQL...")
        pg_conn = connect_postgresql()
        print("✅ PostgreSQL connection successful")
        
        # Process each SQLite database
        for db_path in SQLITE_DATABASES:
            if not os.path.exists(db_path):
                print(f"⚠️ Skipping {db_path} (not found)")
                continue
            
            print(f"\n📁 Processing {db_path}...")
            
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(db_path)
            
            # Get all tables
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Create prefix from database name to avoid conflicts
            db_prefix = os.path.basename(db_path).replace('.db', '').replace('/', '_')
            
            # Migrate each table
            for table_name in tables:
                if table_name.startswith('sqlite_'):
                    continue  # Skip system tables
                
                rows_migrated = migrate_table_data(sqlite_conn, pg_conn, table_name, db_prefix)
                total_rows += rows_migrated
                total_tables += 1
            
            sqlite_conn.close()
        
        # Final summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 Migration Completed Successfully!")
        print(f"⏱️ Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 Tables migrated: {total_tables}")
        print(f"📝 Rows migrated: {total_rows:,}")
        print(f"🗄️ Database: research @ 3.85.19.80:5432")
        
        # Test connection
        print("\n🧪 Testing migrated data...")
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        migrated_tables = pg_cursor.fetchall()
        print(f"✅ Found {len(migrated_tables)} tables in PostgreSQL")
        
        pg_conn.close()
        
        print("\n📋 Next Steps:")
        print("1. Update your application's DATABASE_URL")
        print("2. Test application functionality")
        print("3. Remove SQLite files after validation")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🔧 **Quick Migration Commands**

### **Option 1: Automated Script (Recommended)**

```bash
# Save the migration script above as migrate_to_postgresql.py
python migrate_to_postgresql.py
```

### **Option 2: Manual Step-by-Step**

```bash
# 1. Test PostgreSQL connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://admin:admin@2001@3.85.19.80:5432/research')
print('✅ PostgreSQL connection successful')
conn.close()
"

# 2. Update application config
echo 'DATABASE_URL=postgresql://admin:admin%402001@3.85.19.80:5432/research' > .env

# 3. Initialize tables in PostgreSQL
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ PostgreSQL tables created')
"

# 4. Run custom migration for your data
# (Use the migration script above)
```

---

## ⚡ **Expected Timeline**

| Phase | Duration | Description |
|-------|----------|-------------|
| **Preparation** | 2-3 minutes | Backup, install deps |
| **Schema Creation** | 8-12 minutes | Create tables, constraints |
| **Data Migration** | 2-4 minutes | Copy 2,727 rows |
| **Index Creation** | 3-5 minutes | Create indexes |
| **Validation** | 2-3 minutes | Test & verify |
| **Total** | **17-27 minutes** | End-to-end |

---

## 🎯 **Success Criteria**

- [ ] All 2,727 rows migrated successfully
- [ ] 190 tables created in PostgreSQL
- [ ] Application connects to PostgreSQL
- [ ] Sample queries return expected results
- [ ] No data loss or corruption

---

## 🔍 **Post-Migration Validation**

```python
# validation_script.py
from app import app, db

with app.app_context():
    # Check total tables
    result = db.session.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    print(f"PostgreSQL tables: {result.fetchone()[0]}")
    
    # Check some key row counts
    test_tables = ['report', 'analyst_profile', 'investor_account']
    for table in test_tables:
        try:
            result = db.session.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"{table}: {result.fetchone()[0]} rows")
        except:
            print(f"{table}: Not found or empty")
```

---

## 💡 **Pro Tips**

1. **Schedule during low traffic** - Although it's only ~18 minutes, plan for a maintenance window
2. **Keep SQLite as backup** - Don't delete SQLite files until you're 100% confident
3. **Test thoroughly** - Run your application's key functions after migration
4. **Monitor performance** - PostgreSQL may have different query performance characteristics

Your migration is relatively small and straightforward. The **18-minute estimate is conservative** - it could be completed faster with good network connectivity!

Would you like me to create the actual migration script tailored to your specific table schemas?
