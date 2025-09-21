#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Analysis and Script
Analyzes SQLite databases and provides migration time estimates
"""

import sqlite3
import psycopg2
import os
import time
from datetime import datetime
from urllib.parse import urlparse
import json

# Database configurations
SQLITE_DATABASES = [
    'investment_research.db',
    'instance/investment_research.db',
    'instance/reports.db',
    'instance/research_reports.db',
    'instance/google_meetings.db',
    'ml_ai_system.db',
    'ml_dashboard.db',
    'risk_management.db',
    'investor_accounts.db',
    'investor_scripts.db',
    'predictram_dashboard.db'
]

POSTGRESQL_URL = "postgresql://admin:admin%402001@3.85.19.80:5432/research"

def analyze_sqlite_database(db_path):
    """Analyze SQLite database structure and data volume"""
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get file size
        file_size = os.path.getsize(db_path)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_info = {}
        total_rows = 0
        
        for table in tables:
            table_name = table[0]
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get sample data to estimate row size
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample_row = cursor.fetchone()
                
                table_info[table_name] = {
                    'rows': row_count,
                    'columns': len(columns),
                    'column_info': columns,
                    'has_data': row_count > 0
                }
            except Exception as e:
                table_info[table_name] = {
                    'error': str(e),
                    'rows': 0,
                    'columns': 0,
                    'has_data': False
                }
        
        conn.close()
        
        return {
            'path': db_path,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'total_rows': total_rows,
            'table_count': len(tables),
            'tables': table_info
        }
    
    except Exception as e:
        return {
            'path': db_path,
            'error': str(e),
            'file_size_mb': 0,
            'total_rows': 0,
            'table_count': 0,
            'tables': {}
        }

def estimate_migration_time(analysis_results):
    """Estimate migration time based on data volume"""
    total_size_mb = sum(result['file_size_mb'] for result in analysis_results if 'error' not in result)
    total_rows = sum(result['total_rows'] for result in analysis_results if 'error' not in result)
    total_tables = sum(result['table_count'] for result in analysis_results if 'error' not in result)
    
    # Base estimates (conservative):
    # - Small datasets (< 1MB): 30 seconds per MB
    # - Medium datasets (1-10MB): 20 seconds per MB
    # - Large datasets (> 10MB): 15 seconds per MB
    # - Add overhead for table creation and indexing
    
    if total_size_mb < 1:
        base_time = total_size_mb * 30  # 30 seconds per MB
    elif total_size_mb < 10:
        base_time = total_size_mb * 20  # 20 seconds per MB
    else:
        base_time = total_size_mb * 15  # 15 seconds per MB
    
    # Add overhead for table operations
    table_overhead = total_tables * 5  # 5 seconds per table for creation/indexing
    row_overhead = total_rows * 0.001  # 0.001 seconds per row for processing
    
    total_estimated_seconds = base_time + table_overhead + row_overhead
    
    return {
        'total_size_mb': total_size_mb,
        'total_rows': total_rows,
        'total_tables': total_tables,
        'estimated_seconds': total_estimated_seconds,
        'estimated_minutes': round(total_estimated_seconds / 60, 2),
        'estimated_human_readable': format_duration(total_estimated_seconds)
    }

def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes} minutes {remaining_seconds} seconds"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} hours {minutes} minutes"

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    try:
        # Parse the URL
        parsed = urlparse(POSTGRESQL_URL)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password.replace('%40', '@')  # URL decode
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        
        conn.close()
        
        return {
            'status': 'success',
            'version': version[0],
            'database': current_db[0],
            'connection_time': 'Connected successfully'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def generate_migration_script():
    """Generate SQL migration script"""
    migration_sql = """
-- SQLite to PostgreSQL Migration Script
-- Generated on: {timestamp}

-- Set up environment
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

-- Create extension for UUID if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Migration strategy:
-- 1. Create tables with proper PostgreSQL data types
-- 2. Handle SQLite-specific features (AUTOINCREMENT -> SERIAL)
-- 3. Migrate data with proper type conversion
-- 4. Create indexes and constraints

-- Note: This script template needs to be customized based on your specific table schemas
""".format(timestamp=datetime.now().isoformat())
    
    return migration_sql

def main():
    print("=" * 80)
    print("🔄 SQLite to PostgreSQL Migration Analysis")
    print("=" * 80)
    
    # Test PostgreSQL connection first
    print("\n📡 Testing PostgreSQL connection...")
    pg_test = test_postgresql_connection()
    
    if pg_test['status'] == 'success':
        print(f"✅ PostgreSQL connection successful!")
        print(f"   Database: {pg_test['database']}")
        print(f"   Version: {pg_test['version'][:50]}...")
    else:
        print(f"❌ PostgreSQL connection failed: {pg_test['error']}")
        print("   Please check your connection details and try again.")
        return
    
    # Analyze SQLite databases
    print("\n🔍 Analyzing SQLite databases...")
    analysis_results = []
    
    for db_path in SQLITE_DATABASES:
        print(f"   Analyzing: {db_path}")
        result = analyze_sqlite_database(db_path)
        if result:
            analysis_results.append(result)
    
    # Filter out databases with errors or no data
    valid_results = [r for r in analysis_results if 'error' not in r and r['total_rows'] > 0]
    empty_results = [r for r in analysis_results if 'error' not in r and r['total_rows'] == 0]
    error_results = [r for r in analysis_results if 'error' in r]
    
    print(f"\n📊 Analysis Summary:")
    print(f"   ✅ Valid databases with data: {len(valid_results)}")
    print(f"   📭 Empty databases: {len(empty_results)}")
    print(f"   ❌ Databases with errors: {len(error_results)}")
    
    if valid_results:
        print(f"\n📈 Databases with Data:")
        for result in valid_results:
            print(f"   📁 {result['path']}")
            print(f"      Size: {result['file_size_mb']} MB")
            print(f"      Tables: {result['table_count']}")
            print(f"      Total Rows: {result['total_rows']:,}")
            
            if result['tables']:
                print(f"      Table Details:")
                for table_name, table_info in result['tables'].items():
                    if table_info.get('has_data', False):
                        print(f"        • {table_name}: {table_info['rows']:,} rows, {table_info['columns']} columns")
    
    if empty_results:
        print(f"\n📭 Empty Databases (will be skipped):")
        for result in empty_results:
            print(f"   📁 {result['path']} - {result['file_size_mb']} MB")
    
    if error_results:
        print(f"\n❌ Databases with Errors:")
        for result in error_results:
            print(f"   📁 {result['path']} - Error: {result['error']}")
    
    # Estimate migration time
    if valid_results:
        print(f"\n⏱️ Migration Time Estimation:")
        estimates = estimate_migration_time(valid_results)
        
        print(f"   📊 Total Data Volume: {estimates['total_size_mb']} MB")
        print(f"   📋 Total Tables: {estimates['total_tables']}")
        print(f"   📝 Total Rows: {estimates['total_rows']:,}")
        print(f"   ⏱️ Estimated Time: {estimates['estimated_human_readable']}")
        
        print(f"\n🚀 Migration Phases:")
        
        # Phase breakdown
        schema_time = estimates['total_tables'] * 5
        data_time = estimates['estimated_seconds'] - schema_time
        
        print(f"   1️⃣ Schema Creation: ~{format_duration(schema_time)}")
        print(f"   2️⃣ Data Migration: ~{format_duration(data_time)}")
        print(f"   3️⃣ Index Creation: ~{format_duration(estimates['total_tables'] * 2)}")
        print(f"   4️⃣ Validation: ~{format_duration(estimates['total_tables'] * 1)}")
        
        print(f"\n💡 Migration Recommendations:")
        
        if estimates['total_size_mb'] < 1:
            print(f"   🟢 Small dataset - Migration should be very fast")
            print(f"   🔧 Can be done during normal hours")
        elif estimates['total_size_mb'] < 10:
            print(f"   🟡 Medium dataset - Plan for brief downtime")
            print(f"   🔧 Recommended during low-traffic period")
        else:
            print(f"   🟠 Large dataset - Plan for maintenance window")
            print(f"   🔧 Consider incremental migration strategy")
        
        print(f"\n📝 Migration Steps:")
        print(f"   1. Create full database backup")
        print(f"   2. Set up PostgreSQL schema")
        print(f"   3. Migrate data in batches")
        print(f"   4. Create indexes and constraints")
        print(f"   5. Validate data integrity")
        print(f"   6. Update application configuration")
        print(f"   7. Test application functionality")
        
        # Generate detailed migration plan
        with open('migration_analysis_report.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'postgresql_connection': pg_test,
                'databases_analyzed': len(analysis_results),
                'valid_databases': len(valid_results),
                'migration_estimates': estimates,
                'database_details': valid_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: migration_analysis_report.json")
    
    else:
        print(f"\n⚠️ No databases with data found for migration.")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
