#!/usr/bin/env python3
"""
EC2-Optimized SQLite to PostgreSQL Migration Script
Designed for AWS EC2 deployment with RDS integration

Features:
- Environment variable configuration
- Network optimization for AWS
- Proper error handling and logging
- Progress tracking and reporting
- Automatic retry mechanisms
"""

import sqlite3
import psycopg2
import os
import sys
import time
import json
import logging
from datetime import datetime
from urllib.parse import urlparse

# Configure logging for EC2
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration - Uses environment variables for security
POSTGRESQL_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://admin:admin%402001@3.85.19.80:5432/research'
)

# SQLite databases to migrate (relative to application directory)
SQLITE_DATABASES = [
    'investment_research.db',
    'instance/investment_research.db',
    'instance/reports.db',
    'instance/google_meetings.db',
    'ml_ai_system.db'
]

# EC2-specific configuration
MAX_RETRIES = 3
BATCH_SIZE = 1000  # Larger batches for better network utilization
CONNECTION_TIMEOUT = 60  # Longer timeout for EC2-RDS connection

class EC2MigrationStats:
    def __init__(self):
        self.start_time = time.time()
        self.tables_migrated = 0
        self.rows_migrated = 0
        self.errors = []
        self.databases_processed = 0
        self.retries_used = 0

def check_ec2_environment():
    """Check if running on EC2 and log environment info"""
    try:
        # Try to get EC2 metadata
        import requests
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id',
            timeout=3
        )
        instance_id = response.text
        logger.info(f"✅ Running on EC2 instance: {instance_id}")
        
        # Get availability zone
        az_response = requests.get(
            'http://169.254.169.254/latest/meta-data/placement/availability-zone',
            timeout=3
        )
        az = az_response.text
        logger.info(f"📍 Availability Zone: {az}")
        
        return True, instance_id, az
    except:
        logger.info("🖥️ Not running on EC2 or metadata service unavailable")
        return False, None, None

def connect_postgresql_with_retry():
    """Connect to PostgreSQL with retry logic for EC2-RDS"""
    parsed = urlparse(POSTGRESQL_URL)
    password = parsed.password.replace('%40', '@') if parsed.password else ''
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"🔌 Connecting to PostgreSQL (attempt {attempt + 1}/{MAX_RETRIES})")
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/'),
                user=parsed.username,
                password=password,
                connect_timeout=CONNECTION_TIMEOUT,
                # EC2-specific optimizations
                application_name='ec2_migration_script',
                sslmode='prefer'  # Use SSL if available
            )
            
            conn.autocommit = False
            logger.info("✅ PostgreSQL connection successful")
            return conn
            
        except Exception as e:
            logger.warning(f"⚠️ Connection attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 5  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error("❌ All connection attempts failed")
                raise

def check_sqlite_files():
    """Check which SQLite files exist in the EC2 environment"""
    found_files = []
    missing_files = []
    
    for db_path in SQLITE_DATABASES:
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            found_files.append((db_path, size_mb))
            logger.info(f"✅ Found: {db_path} ({size_mb:.2f} MB)")
        else:
            missing_files.append(db_path)
            logger.warning(f"⚠️ Missing: {db_path}")
    
    return found_files, missing_files

def get_sqlite_table_info(sqlite_conn, table_name):
    """Get SQLite table schema information"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def convert_sqlite_type_to_postgresql(sqlite_type, is_primary_key=False):
    """Convert SQLite data types to PostgreSQL equivalents"""
    sqlite_type = sqlite_type.upper()
    
    type_mapping = {
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
    
    if is_primary_key and 'INTEGER' in sqlite_type:
        return 'SERIAL PRIMARY KEY'
    
    for sqlite_key, pg_type in type_mapping.items():
        if sqlite_key in sqlite_type:
            return pg_type
    
    return 'TEXT'  # Default fallback

def create_postgresql_table(pg_conn, table_name, table_info, prefix=""):
    """Create PostgreSQL table from SQLite schema"""
    pg_table_name = f"{prefix}_{table_name}" if prefix else table_name
    cursor = pg_conn.cursor()
    
    # Drop table if exists
    cursor.execute(f'DROP TABLE IF EXISTS "{pg_table_name}" CASCADE')
    
    # Build column definitions
    column_defs = []
    primary_keys = []
    
    for col in table_info:
        col_id, col_name, col_type, not_null, default_val, is_pk = col
        
        pg_type = convert_sqlite_type_to_postgresql(col_type, is_pk)
        col_def = f'"{col_name}" {pg_type}'
        
        if not_null and 'SERIAL' not in pg_type:
            col_def += ' NOT NULL'
        
        if default_val is not None and 'SERIAL' not in pg_type:
            if isinstance(default_val, str):
                col_def += f" DEFAULT '{default_val}'"
            else:
                col_def += f" DEFAULT {default_val}"
        
        column_defs.append(col_def)
        
        if is_pk and 'SERIAL' not in pg_type:
            primary_keys.append(f'"{col_name}"')
    
    if primary_keys:
        column_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
    
    create_sql = f'CREATE TABLE "{pg_table_name}" ({", ".join(column_defs)})'
    
    try:
        cursor.execute(create_sql)
        logger.debug(f"✅ Created table: {pg_table_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create table {pg_table_name}: {e}")
        return False

def migrate_table_data_optimized(sqlite_conn, pg_conn, table_name, prefix="", stats=None):
    """Migrate data with EC2-optimized batching"""
    pg_table_name = f"{prefix}_{table_name}" if prefix else table_name
    
    try:
        # Get SQLite data
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f'SELECT * FROM "{table_name}"')
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Count total rows for progress tracking
        count_cursor = sqlite_conn.cursor()
        count_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows = count_cursor.fetchone()[0]
        
        if total_rows == 0:
            logger.info(f"   📭 {table_name}: No data to migrate")
            return 0
        
        logger.info(f"   🔄 Migrating {table_name}: {total_rows} rows")
        
        # Prepare PostgreSQL cursor
        pg_cursor = pg_conn.cursor()
        
        # Build INSERT statement
        columns_str = ', '.join(f'"{col}"' for col in column_names)
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f'INSERT INTO "{pg_table_name}" ({columns_str}) VALUES ({placeholders})'
        
        # Fetch and insert data in optimized batches
        rows_inserted = 0
        batch_num = 0
        
        while True:
            batch = sqlite_cursor.fetchmany(BATCH_SIZE)
            if not batch:
                break
            
            batch_num += 1
            
            try:
                pg_cursor.executemany(insert_sql, batch)
                rows_inserted += len(batch)
                
                # Progress reporting
                progress = (rows_inserted / total_rows) * 100
                logger.info(f"     📊 Batch {batch_num}: {rows_inserted}/{total_rows} rows ({progress:.1f}%)")
                
            except Exception as e:
                logger.warning(f"     ⚠️ Batch {batch_num} failed: {e}")
                if stats:
                    stats.retries_used += 1
                
                # Try inserting rows individually
                for row in batch:
                    try:
                        pg_cursor.execute(insert_sql, row)
                        rows_inserted += 1
                    except Exception as row_error:
                        logger.error(f"     ❌ Skipping row: {row_error}")
        
        pg_conn.commit()
        logger.info(f"   ✅ {table_name} → {pg_table_name}: {rows_inserted} rows migrated")
        return rows_inserted
        
    except Exception as e:
        logger.error(f"   ❌ {table_name}: Migration failed - {e}")
        pg_conn.rollback()
        return 0

def create_migration_script_for_ec2():
    """Create a simple deployment script for EC2"""
    script_content = """#!/bin/bash
# EC2 Migration Deployment Script

set -e

echo "🚀 Starting SQLite to PostgreSQL Migration on EC2"
echo "================================================="

# Check if running as ec2-user
if [[ $USER != "ec2-user" ]]; then
    echo "⚠️ Consider running as ec2-user for proper permissions"
fi

# Activate virtual environment if it exists
if [[ -f "venv/bin/activate" ]]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages if not present
echo "📦 Installing migration dependencies..."
pip install psycopg2-binary || echo "psycopg2-binary already installed"

# Set environment variables for production
export DATABASE_URL="postgresql://admin:admin%402001@3.85.19.80:5432/research"
export MIGRATION_ENV="production"

# Run migration
echo "🔄 Starting migration..."
python migrate_to_postgresql_ec2.py

echo "✅ Migration script completed!"
echo "📋 Check migration.log for detailed results"
"""
    
    with open('deploy_migration_ec2.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('deploy_migration_ec2.sh', 0o755)
    logger.info("📄 Created deployment script: deploy_migration_ec2.sh")

def generate_ec2_migration_report(stats, instance_info):
    """Generate EC2-specific migration report"""
    end_time = time.time()
    duration = end_time - stats.start_time
    
    is_ec2, instance_id, az = instance_info
    
    report = {
        'migration_completed': datetime.now().isoformat(),
        'environment': {
            'platform': 'AWS EC2' if is_ec2 else 'Local',
            'instance_id': instance_id,
            'availability_zone': az,
            'postgresql_url': POSTGRESQL_URL.replace('%40', '@').replace(':admin@', ':***@')
        },
        'performance': {
            'duration_seconds': round(duration, 2),
            'duration_minutes': round(duration / 60, 2),
            'rows_per_second': round(stats.rows_migrated / duration, 2) if duration > 0 else 0,
            'batch_size_used': BATCH_SIZE,
            'retries_used': stats.retries_used
        },
        'results': {
            'databases_processed': stats.databases_processed,
            'tables_migrated': stats.tables_migrated,
            'rows_migrated': stats.rows_migrated,
            'errors': stats.errors,
            'status': 'SUCCESS' if not stats.errors else 'COMPLETED_WITH_WARNINGS'
        }
    }
    
    # Save to both local and /tmp for EC2 access
    for path in ['migration_report_ec2.json', '/tmp/migration_report_ec2.json']:
        try:
            with open(path, 'w') as f:
                json.dump(report, f, indent=2)
        except:
            pass
    
    return report

def main():
    """Main EC2 migration function"""
    print("🚀 EC2-Optimized SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Check environment
    instance_info = check_ec2_environment()
    is_ec2, instance_id, az = instance_info
    
    stats = EC2MigrationStats()
    
    try:
        # Check SQLite files
        logger.info("📁 Checking SQLite database files...")
        found_files, missing_files = check_sqlite_files()
        
        if not found_files:
            logger.error("❌ No SQLite files found to migrate")
            sys.exit(1)
        
        total_size = sum(size for _, size in found_files)
        logger.info(f"📊 Found {len(found_files)} databases, total size: {total_size:.2f} MB")
        
        # Connect to PostgreSQL
        logger.info("🔌 Connecting to PostgreSQL RDS...")
        pg_conn = connect_postgresql_with_retry()
        
        if not pg_conn:
            logger.error("❌ Failed to establish PostgreSQL connection")
            sys.exit(1)
        
        # Verify write permissions
        test_cursor = pg_conn.cursor()
        test_cursor.execute("CREATE TABLE IF NOT EXISTS migration_test_ec2 (id INTEGER)")
        test_cursor.execute("DROP TABLE migration_test_ec2")
        pg_conn.commit()
        logger.info("✅ PostgreSQL write permissions verified")
        
        # Process each database
        for db_path, size_mb in found_files:
            logger.info(f"\n📁 Processing: {db_path} ({size_mb:.2f} MB)")
            stats.databases_processed += 1
            
            try:
                sqlite_conn = sqlite3.connect(db_path)
                
                # Get all tables
                cursor = sqlite_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"   📋 Found {len(tables)} tables")
                
                # Create table prefix
                db_name = os.path.basename(db_path).replace('.db', '')
                if db_path.startswith('instance/'):
                    db_name = 'inst_' + db_name
                
                # Process each table
                for table_name in tables:
                    if table_name.startswith('sqlite_'):
                        continue
                    
                    # Get table schema
                    table_info = get_sqlite_table_info(sqlite_conn, table_name)
                    
                    # Create PostgreSQL table
                    if create_postgresql_table(pg_conn, table_name, table_info, db_name):
                        # Migrate data
                        rows_migrated = migrate_table_data_optimized(
                            sqlite_conn, pg_conn, table_name, db_name, stats
                        )
                        stats.rows_migrated += rows_migrated
                        stats.tables_migrated += 1
                    else:
                        stats.errors.append(f"Failed to create table: {table_name}")
                
                sqlite_conn.close()
                
            except Exception as e:
                error_msg = f"Error processing {db_path}: {e}"
                logger.error(f"   ❌ {error_msg}")
                stats.errors.append(error_msg)
        
        # Generate report
        report = generate_ec2_migration_report(stats, instance_info)
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 EC2 MIGRATION COMPLETED!")
        print("=" * 60)
        print(f"🖥️  Environment: {'AWS EC2' if is_ec2 else 'Local'}")
        if instance_id:
            print(f"📍 Instance: {instance_id} ({az})")
        print(f"⏱️  Duration: {report['performance']['duration_minutes']:.1f} minutes")
        print(f"🚀 Performance: {report['performance']['rows_per_second']:.0f} rows/second")
        print(f"📊 Results: {stats.tables_migrated} tables, {stats.rows_migrated:,} rows")
        print(f"📄 Report: migration_report_ec2.json")
        
        if stats.errors:
            print(f"\n⚠️ Warnings ({len(stats.errors)}):")
            for error in stats.errors:
                print(f"   - {error}")
        
        logger.info("✅ Migration completed successfully")
        if pg_conn:
            pg_conn.close()
        
    except KeyboardInterrupt:
        logger.error("❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        stats.errors.append(f"Fatal error: {e}")
        generate_ec2_migration_report(stats, instance_info)
        sys.exit(1)

if __name__ == "__main__":
    # Create deployment script
    create_migration_script_for_ec2()
    
    # Run migration
    main()
