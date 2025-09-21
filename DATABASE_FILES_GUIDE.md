# 🗄️ SQLite Database Files - Complete Guide
**Investment Research Platform Database Architecture**  
**Generated**: September 17, 2025  
**Status**: Production Ready

## 🎯 Executive Summary

Your Investment Research Platform uses **5 active SQLite database files** with a total size of **356 KB**. The primary application data is stored in `investment_research.db`, while specialized data is distributed across dedicated database files.

## 📊 Database Files Overview

### 🏆 **PRIMARY DATABASE**
```
📁 investment_research.db (132 KB)
   └── Main application database
   └── 6 tables, 50 total records
   └── Last modified: September 9, 2025
   └── Status: ✅ ACTIVE
```

**Key Data**:
- `script_executions`: 47 records (execution history)
- `portfolio_commentary`: 1 record (portfolio analysis)
- System tables: 2 records

### 🤖 **ML/AI SYSTEM DATABASE**
```
📁 ml_ai_system.db (148 KB)
   └── Machine Learning & AI data
   └── 15 tables, 42 total records  
   └── Last modified: September 11, 2025
   └── Status: ✅ ACTIVE
```

**Key Data**:
- `ai_agents`: 12 records (8 Agentic AI agents + 4 specialized)
- `ml_models`: 10 records (ML model definitions)
- `user_subscriptions`: 5 records (subscription data)
- `system_config`: 5 records (AI system configuration)
- `users`: 1 record (AI system user)

### 🛡️ **RISK MANAGEMENT DATABASE**
```
📁 risk_management.db (16 KB)
   └── Portfolio risk analytics
   └── 3 tables, 0 records
   └── Last modified: September 10, 2025
   └── Status: 🟡 INITIALIZED (Empty)
```

### 📈 **ML DASHBOARD DATABASE**
```
📁 ml_dashboard.db (36 KB)
   └── ML dashboard visualization data
   └── 2 tables, 0 records
   └── Last modified: August 31, 2025
   └── Status: 🟡 INITIALIZED (Empty)
```

### 🧪 **TEST DATABASE**
```
📁 test.db (24 KB)
   └── Development and testing data
   └── 4 tables, 0 records
   └── Last modified: September 11, 2025
   └── Status: 🟡 DEVELOPMENT
```

## 🔑 **WHICH FILE TO USE**

### For Data Backup:
**Primary**: `investment_research.db` - Contains main application data  
**Secondary**: `ml_ai_system.db` - Contains ML/AI configuration and models

### For Data Migration:
**Essential**: Both `investment_research.db` AND `ml_ai_system.db`  
**Optional**: `risk_management.db` (if you use risk analytics)

### For Development:
**Local Development**: All `.db` files  
**Production**: Configure PostgreSQL and migrate data

## 📋 Database Configuration

### Current Setup (config.py):
```python
# Default SQLite configuration
DATABASE_URL = "sqlite:///investment_research.db"

# For production PostgreSQL:
DATABASE_URL = "postgresql://user:pass@host:port/dbname"
```

### Environment Variables:
```bash
# Local development
DATABASE_URL=sqlite:///investment_research.db

# Production
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/production_db
```

## 💾 Backup Instructions

### Critical Files (Daily Backup Recommended):
1. **`investment_research.db`** - Main application data
2. **`ml_ai_system.db`** - AI system configuration

### Backup Commands:
```powershell
# Create timestamped backup
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "investment_research.db" "backup_main_$date.db"
Copy-Item "ml_ai_system.db" "backup_ai_$date.db"

# Verify backup integrity
python -c "import sqlite3; print('✅ OK' if sqlite3.connect('backup_main_$date.db').execute('PRAGMA integrity_check;').fetchone()[0] == 'ok' else '❌ Error')"
```

### Automated Backup:
```bash
# Use the provided database manager
python database_manager.py

# Or the quick explorer
python explore_database.py
```

## 🔍 Database Analysis Tools

### Provided Scripts:
- **`database_manager.py`** - Complete database management utility
- **`explore_database.py`** - Quick database explorer
- **`check_all_databases.py`** - Analyze all database files
- **`test_database.py`** - Database connectivity testing

### Usage Examples:
```bash
# Explore primary database
python explore_database.py

# Analyze all databases
python check_all_databases.py

# Full database management
python database_manager.py
```

## 🚀 Production Migration

### AWS RDS PostgreSQL Migration:
```bash
# 1. Backup SQLite data
python database_manager.py

# 2. Export data for migration
python migrate_sqlite_to_postgres.py

# 3. Update environment variables
export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/production_db"

# 4. Run application with PostgreSQL
python app.py
```

## 📈 Database Statistics

### Current Usage (September 17, 2025):
```
Total Database Files: 5 active
Total Storage: 356 KB
Primary Data: 132 KB (investment_research.db)
AI/ML Data: 148 KB (ml_ai_system.db)
Other Data: 76 KB (risk, dashboard, test)

Active Tables: 30 total
Active Records: 92 total
```

### Growth Projection:
- **Light Usage**: ~1-2 MB/month
- **Medium Usage**: ~5-10 MB/month
- **Heavy Usage**: ~20-50 MB/month

## 🛠️ Maintenance Tasks

### Weekly:
- Check database integrity: `python explore_database.py`
- Create backup: `python database_manager.py`

### Monthly:
- Vacuum databases: `VACUUM;` command
- Analyze performance: `ANALYZE;` command
- Review storage usage

### Before Deployment:
- Backup all database files
- Test migration to PostgreSQL
- Verify data integrity

## 🔐 Security Considerations

### File Permissions:
```bash
# Restrict database file access
chmod 600 *.db  # Owner read/write only
```

### Data Protection:
- Regular backups to secure location
- Encryption at rest (file system level)
- No sensitive data in plain text
- API keys stored encrypted

## 📞 Quick Reference

**Primary Database**: `investment_research.db` (132 KB)  
**AI/ML Database**: `ml_ai_system.db` (148 KB)  
**Configuration**: `config.py` line 23  
**Backup Tool**: `python database_manager.py`  
**Explorer Tool**: `python explore_database.py`  

## 🎯 Action Items

### Immediate:
1. ✅ **Backup main databases** - `investment_research.db` and `ml_ai_system.db`
2. ✅ **Test database integrity** - Run `python explore_database.py`

### For Production:
1. 🔄 **Setup PostgreSQL RDS** - Migrate from SQLite
2. 🔄 **Configure environment variables** - Update DATABASE_URL
3. 🔄 **Test migration process** - Ensure data integrity

### Ongoing:
1. 📅 **Weekly backups** - Automated backup schedule
2. 📊 **Monitor growth** - Track database size
3. 🔍 **Regular integrity checks** - Monthly maintenance

---

**Database Status**: ✅ Healthy and Ready for Production  
**Primary File**: `investment_research.db`  
**Total Size**: 356 KB  
**Last Updated**: September 17, 2025