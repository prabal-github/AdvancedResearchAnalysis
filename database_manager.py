#!/usr/bin/env python3
"""
Database Management Utility
Provides tools for managing SQLite databases in the Investment Research Platform
"""

import os
import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Utility class for managing application databases"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.databases = {
            'primary': 'investment_research.db',
            'ml_ai': 'ml_ai_system.db', 
            'risk': 'risk_management.db',
            'dashboard': 'ml_dashboard.db',
            'test': 'test.db'
        }
        
    def get_database_info(self):
        """Get information about all database files"""
        info = {}
        
        for name, filename in self.databases.items():
            db_path = self.base_path / filename
            
            if db_path.exists():
                stat = db_path.stat()
                info[name] = {
                    'filename': filename,
                    'size_bytes': stat.st_size,
                    'size_kb': round(stat.st_size / 1024, 2),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'exists': True
                }
            else:
                info[name] = {
                    'filename': filename,
                    'size_bytes': 0,
                    'size_kb': 0,
                    'last_modified': 'N/A',
                    'exists': False
                }
                
        return info
    
    def backup_databases(self, backup_dir=None):
        """Create backups of all database files"""
        if backup_dir is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.base_path / f'database_backup_{timestamp}'
        
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(exist_ok=True)
        
        backed_up = []
        
        for name, filename in self.databases.items():
            src_path = self.base_path / filename
            if src_path.exists():
                dst_path = backup_dir / f'{name}_{filename}'
                shutil.copy2(src_path, dst_path)
                backed_up.append({
                    'name': name,
                    'source': str(src_path),
                    'backup': str(dst_path),
                    'size_kb': round(src_path.stat().st_size / 1024, 2)
                })
        
        # Create backup manifest
        manifest = {
            'backup_date': datetime.now().isoformat(),
            'backup_dir': str(backup_dir),
            'files_backed_up': backed_up,
            'total_files': len(backed_up)
        }
        
        manifest_path = backup_dir / 'backup_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    def check_database_integrity(self, db_name='primary'):
        """Check integrity of specified database"""
        if db_name not in self.databases:
            return {'error': f'Unknown database: {db_name}'}
        
        db_path = self.base_path / self.databases[db_name]
        
        if not db_path.exists():
            return {'error': f'Database file not found: {db_path}'}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute('PRAGMA integrity_check;')
            integrity_result = cursor.fetchall()
            
            # Get basic stats
            cursor.execute('PRAGMA page_count;')
            page_count = cursor.fetchone()[0]
            
            cursor.execute('PRAGMA page_size;')
            page_size = cursor.fetchone()[0]
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'database': db_name,
                'integrity': integrity_result[0][0] if integrity_result else 'Unknown',
                'page_count': page_count,
                'page_size': page_size,
                'total_size_bytes': page_count * page_size,
                'table_count': table_count,
                'status': 'OK' if integrity_result and integrity_result[0][0] == 'ok' else 'Issues Found'
            }
            
        except Exception as e:
            return {'error': f'Failed to check integrity: {str(e)}'}
    
    def get_table_list(self, db_name='primary'):
        """Get list of tables in specified database"""
        if db_name not in self.databases:
            return {'error': f'Unknown database: {db_name}'}
        
        db_path = self.base_path / self.databases[db_name]
        
        if not db_path.exists():
            return {'error': f'Database file not found: {db_path}'}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, type, sql 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name;
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name = row[0]
                
                # Get row count for each table
                cursor.execute(f'SELECT COUNT(*) FROM {table_name};')
                row_count = cursor.fetchone()[0]
                
                tables.append({
                    'name': table_name,
                    'type': row[1],
                    'row_count': row_count,
                    'sql': row[2]
                })
            
            conn.close()
            
            return {
                'database': db_name,
                'tables': tables,
                'total_tables': len(tables)
            }
            
        except Exception as e:
            return {'error': f'Failed to get table list: {str(e)}'}
    
    def vacuum_database(self, db_name='primary'):
        """Vacuum specified database to optimize storage"""
        if db_name not in self.databases:
            return {'error': f'Unknown database: {db_name}'}
        
        db_path = self.base_path / self.databases[db_name]
        
        if not db_path.exists():
            return {'error': f'Database file not found: {db_path}'}
        
        try:
            # Get size before vacuum
            size_before = db_path.stat().st_size
            
            conn = sqlite3.connect(str(db_path))
            conn.execute('VACUUM;')
            conn.close()
            
            # Get size after vacuum
            size_after = db_path.stat().st_size
            
            return {
                'database': db_name,
                'size_before_bytes': size_before,
                'size_after_bytes': size_after,
                'space_saved_bytes': size_before - size_after,
                'space_saved_kb': round((size_before - size_after) / 1024, 2),
                'status': 'Success'
            }
            
        except Exception as e:
            return {'error': f'Failed to vacuum database: {str(e)}'}

def main():
    """Main function for command-line usage"""
    db_manager = DatabaseManager()
    
    print("🗄️ Database Management Utility")
    print("=" * 50)
    
    # Get database information
    print("\n📊 Database Status:")
    info = db_manager.get_database_info()
    
    total_size = 0
    for name, data in info.items():
        status = "✅" if data['exists'] else "❌"
        print(f"{status} {name:12} | {data['filename']:25} | {data['size_kb']:6.1f} KB | {data['last_modified']}")
        total_size += data['size_kb']
    
    print(f"\n📈 Total Database Size: {total_size:.1f} KB")
    
    # Check integrity of primary database
    print("\n🔍 Primary Database Integrity Check:")
    integrity = db_manager.check_database_integrity('primary')
    if 'error' in integrity:
        print(f"❌ Error: {integrity['error']}")
    else:
        print(f"✅ Status: {integrity['status']}")
        print(f"📑 Tables: {integrity['table_count']}")
        print(f"💾 Size: {integrity['total_size_bytes']:,} bytes")
    
    # Get table information
    print("\n📋 Primary Database Tables:")
    tables = db_manager.get_table_list('primary')
    if 'error' in tables:
        print(f"❌ Error: {tables['error']}")
    else:
        for table in tables['tables'][:10]:  # Show first 10 tables
            print(f"  📄 {table['name']:20} | {table['row_count']:6} rows")
        
        if len(tables['tables']) > 10:
            print(f"  ... and {len(tables['tables']) - 10} more tables")
    
    print(f"\n🎯 Primary Database: {db_manager.databases['primary']}")
    print("💡 Use this file for data backup and migration")
    
    # Offer to create backup
    response = input("\n🔄 Create database backup? (y/n): ").lower().strip()
    if response == 'y':
        print("📦 Creating backup...")
        backup_result = db_manager.backup_databases()
        print(f"✅ Backup created: {backup_result['backup_dir']}")
        print(f"📁 Files backed up: {backup_result['total_files']}")

if __name__ == '__main__':
    main()