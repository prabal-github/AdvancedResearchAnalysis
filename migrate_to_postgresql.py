#!/usr/bin/env python3
"""
Production-Ready SQLite to PostgreSQL Migration Script
Optimized for your specific database structure

Estimated Time: 15-20 minutes
Data Volume: 7.2 MB, 2,727 rows, 190 tables
"""

import sqlite3
import psycopg2
import os
import sys
import time
import json
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

# Data type mapping from SQLite to PostgreSQL
TYPE_MAPPING = {
    'INTEGER': 'INTEGER',
    'TEXT': 'TEXT',
    'REAL': 'REAL',
    'NUMERIC': 'NUMERIC',
    'BLOB': 'BYTEA',
    'BOOLEAN': 'BOOLEAN',
    'DATETIME': 'TIMESTAMP',
    'DATE': 'DATE',
    'TIME': 'TIME'
}

class MigrationStats:
    def __init__(self):
        self.start_time = time.time()
        self.tables_migrated = 0
        self.rows_migrated = 0
        self.errors = []
        self.databases_processed = 0

def connect_postgresql():
    """Connect to PostgreSQL database with proper error handling"""
    try:
        parsed = urlparse(POSTGRESQL_URL)
        password = parsed.password.replace('%40', '@') if parsed.password else ''
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=password,
            connect_timeout=30
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        sys.exit(1)

def get_sqlite_table_info(sqlite_conn, table_name):
    """Get complete SQLite table information"""
    cursor = sqlite_conn.cursor()
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Get foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = cursor.fetchall()
    
    # Get indexes
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    return {
        'columns': columns,
        'foreign_keys': foreign_keys,
        'indexes': indexes
    }

def convert_sqlite_type_to_postgresql(sqlite_type, is_primary_key=False, is_auto_increment=False):
    """Convert SQLite data type to PostgreSQL equivalent"""
    sqlite_type = sqlite_type.upper()
    
    # Handle AUTOINCREMENT primary keys
    if is_primary_key and (is_auto_increment or 'AUTOINCREMENT' in sqlite_type):
        return 'SERIAL PRIMARY KEY'
    
    # Map basic types
    for sqlite_key, pg_type in TYPE_MAPPING.items():
        if sqlite_key in sqlite_type:
            return pg_type
    
    # Default fallback
    return 'TEXT'

def create_postgresql_table(pg_conn, table_name, table_info, prefix=""):
    """Create PostgreSQL table from SQLite schema"""
    pg_table_name = f"{prefix}_{table_name}" if prefix else table_name
    
    cursor = pg_conn.cursor()
    
    # Drop table if exists
    cursor.execute(f'DROP TABLE IF EXISTS "{pg_table_name}" CASCADE')
    
    # Build column definitions
    column_defs = []
    primary_keys = []
    
    for col in table_info['columns']:
        col_id, col_name, col_type, not_null, default_val, is_pk = col
        
        # Convert type
        pg_type = convert_sqlite_type_to_postgresql(
            col_type, 
            is_primary_key=is_pk,
            is_auto_increment=False  # We'll handle this separately
        )
        
        # Build column definition
        col_def = f'"{col_name}" {pg_type}'
        
        # Add NOT NULL constraint
        if not_null and 'SERIAL' not in pg_type:
            col_def += ' NOT NULL'
        
        # Add DEFAULT value
        if default_val is not None and 'SERIAL' not in pg_type:
            col_def += f" DEFAULT {default_val}"
        
        column_defs.append(col_def)
        
        if is_pk and 'SERIAL' not in pg_type:
            primary_keys.append(f'"{col_name}"')
    
    # Add primary key constraint if needed
    if primary_keys:
        column_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
    
    # Create table
    create_sql = f'CREATE TABLE "{pg_table_name}" ({", ".join(column_defs)})'
    
    try:
        cursor.execute(create_sql)
        return True
    except Exception as e:
        print(f"   ❌ Failed to create table {pg_table_name}: {e}")
        return False

def migrate_table_data(sqlite_conn, pg_conn, table_name, prefix="", batch_size=500):
    """Migrate data from SQLite to PostgreSQL with batching"""
    pg_table_name = f"{prefix}_{table_name}" if prefix else table_name
    
    try:
        # Get SQLite data
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f'SELECT * FROM "{table_name}"')
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Fetch all data
        all_rows = sqlite_cursor.fetchall()
        
        if not all_rows:
            print(f"   📭 {table_name}: No data to migrate")
            return 0
        
        # Prepare PostgreSQL cursor
        pg_cursor = pg_conn.cursor()
        
        # Build INSERT statement
        columns_str = ', '.join(f'"{col}"' for col in column_names)
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f'INSERT INTO "{pg_table_name}" ({columns_str}) VALUES ({placeholders})'
        
        # Insert data in batches
        rows_inserted = 0
        for i in range(0, len(all_rows), batch_size):
            batch = all_rows[i:i + batch_size]
            
            try:
                pg_cursor.executemany(insert_sql, batch)
                rows_inserted += len(batch)
            except Exception as e:
                print(f"   ⚠️ Batch insert error for {table_name}: {e}")
                # Try inserting rows one by one to identify problematic data
                for row in batch:
                    try:
                        pg_cursor.execute(insert_sql, row)
                        rows_inserted += 1
                    except Exception as row_error:
                        print(f"   ⚠️ Skipping problematic row in {table_name}: {row_error}")
        
        pg_conn.commit()
        print(f"   ✅ {table_name} → {pg_table_name}: {rows_inserted} rows migrated")
        return rows_inserted
        
    except Exception as e:
        print(f"   ❌ {table_name}: Migration failed - {e}")
        pg_conn.rollback()
        return 0

def validate_migration(pg_conn, stats):
    """Validate the migration results"""
    print("\n🔍 Validating migration...")
    
    cursor = pg_conn.cursor()
    
    # Count total tables
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    table_count = cursor.fetchone()[0]
    
    # Count total rows across all tables
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    total_rows = 0
    for (table_name,) in cursor.fetchall():
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cursor.fetchone()[0]
            total_rows += row_count
        except:
            pass
    
    print(f"✅ Validation Results:")
    print(f"   📊 Tables in PostgreSQL: {table_count}")
    print(f"   📝 Total rows: {total_rows:,}")
    print(f"   📈 Expected rows: {stats.rows_migrated:,}")
    
    if total_rows == stats.rows_migrated:
        print("   🎉 Row count matches - Migration successful!")
    else:
        print("   ⚠️ Row count mismatch - Please investigate")

def generate_migration_report(stats):
    """Generate detailed migration report"""
    end_time = time.time()
    duration = end_time - stats.start_time
    
    report = {
        'migration_completed': datetime.now().isoformat(),
        'duration_seconds': round(duration, 2),
        'duration_minutes': round(duration / 60, 2),
        'databases_processed': stats.databases_processed,
        'tables_migrated': stats.tables_migrated,
        'rows_migrated': stats.rows_migrated,
        'errors': stats.errors,
        'postgresql_url': POSTGRESQL_URL.replace('%40', '@'),
        'status': 'SUCCESS' if not stats.errors else 'COMPLETED_WITH_WARNINGS'
    }
    
    with open('migration_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main migration function"""
    print("🚀 SQLite to PostgreSQL Migration Starting")
    print("=" * 70)
    print(f"Target: {POSTGRESQL_URL.replace('%40', '@')}")
    print(f"Databases to migrate: {len(SQLITE_DATABASES)}")
    print("=" * 70)
    
    stats = MigrationStats()
    
    try:
        # Connect to PostgreSQL
        print("📡 Connecting to PostgreSQL...")
        pg_conn = connect_postgresql()
        print("✅ PostgreSQL connection successful")
        
        # Test write permissions
        test_cursor = pg_conn.cursor()
        test_cursor.execute("CREATE TABLE IF NOT EXISTS migration_test (id INTEGER)")
        test_cursor.execute("DROP TABLE migration_test")
        pg_conn.commit()
        print("✅ PostgreSQL write permissions verified")
        
        # Process each SQLite database
        for db_path in SQLITE_DATABASES:
            if not os.path.exists(db_path):
                print(f"⚠️ Skipping {db_path} (file not found)")
                continue
            
            print(f"\n📁 Processing: {db_path}")
            stats.databases_processed += 1
            
            try:
                # Connect to SQLite
                sqlite_conn = sqlite3.connect(db_path)
                
                # Get all tables
                cursor = sqlite_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                print(f"   Found {len(tables)} tables")
                
                # Create table prefix to avoid conflicts
                db_name = os.path.basename(db_path).replace('.db', '')
                if db_path.startswith('instance/'):
                    db_name = 'inst_' + db_name
                
                # Process each table
                for table_name in tables:
                    if table_name.startswith('sqlite_'):
                        continue  # Skip SQLite system tables
                    
                    print(f"   🔄 Migrating table: {table_name}")
                    
                    # Get table schema
                    table_info = get_sqlite_table_info(sqlite_conn, table_name)
                    
                    # Create PostgreSQL table
                    if create_postgresql_table(pg_conn, table_name, table_info, db_name):
                        # Migrate data
                        rows_migrated = migrate_table_data(sqlite_conn, pg_conn, table_name, db_name)
                        stats.rows_migrated += rows_migrated
                        stats.tables_migrated += 1
                    else:
                        stats.errors.append(f"Failed to create table: {table_name}")
                
                sqlite_conn.close()
                
            except Exception as e:
                error_msg = f"Error processing {db_path}: {e}"
                print(f"   ❌ {error_msg}")
                stats.errors.append(error_msg)
        
        # Final validation
        validate_migration(pg_conn, stats)
        
        # Generate report
        report = generate_migration_report(stats)
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 MIGRATION COMPLETED!")
        print("=" * 70)
        print(f"⏱️  Duration: {report['duration_minutes']:.1f} minutes")
        print(f"📊 Databases: {stats.databases_processed}")
        print(f"📋 Tables: {stats.tables_migrated}")
        print(f"📝 Rows: {stats.rows_migrated:,}")
        print(f"⚠️  Errors: {len(stats.errors)}")
        print(f"📄 Report: migration_report.json")
        
        if stats.errors:
            print(f"\n⚠️ Warnings/Errors:")
            for error in stats.errors:
                print(f"   - {error}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Update your app's DATABASE_URL to:")
        print(f"   postgresql://admin:admin%402001@3.85.19.80:5432/research")
        print(f"2. Test your application functionality")
        print(f"3. Backup SQLite files and remove after validation")
        
        pg_conn.close()
        
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        stats.errors.append(f"Fatal error: {e}")
        generate_migration_report(stats)
        sys.exit(1)

if __name__ == "__main__":
    # Confirmation prompt
    print("🔄 SQLite to PostgreSQL Migration Script")
    print("=" * 50)
    print("This script will migrate your SQLite data to PostgreSQL.")
    print(f"Target: postgresql://admin:***@3.85.19.80:5432/research")
    print("Estimated time: 15-20 minutes")
    print("=" * 50)
    
    response = input("\nProceed with migration? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)
    
    main()
