# 📊 SQLite Database Documentation
**Investment Research Platform - Database Architecture**  
**Date**: September 17, 2025  
**Version**: 2.3 Production Ready

## 🎯 Overview

The Investment Research Platform uses a multi-database SQLite architecture to organize different functional areas. This documentation provides a complete guide to understanding, managing, and working with the database files.

## 📂 Database Files Inventory

### 🏆 **Primary Database Files**

#### 1. `investment_research.db` *(135 KB)*
**Status**: 🟢 ACTIVE - Primary Application Database  
**Last Modified**: September 9, 2025  
**Configuration**: Default database in `config.py`

**Contains**:
- User accounts and authentication
- Analyst profiles and credentials
- Investment reports and analysis
- Portfolio data and holdings
- Stock analysis and recommendations
- Session management
- Admin settings and configurations
- API keys and external integrations
- Subscription and billing data
- Contact forms and user communications

**Database Models**:
```python
# Key tables include:
- users, analysts, admins
- reports, portfolio_stocks, investor_portfolios
- session_bookings, google_meet_sessions
- contact_forms, subscriptions
- api_keys, admin_configurations
```

#### 2. `ml_ai_system.db` *(151 KB)*
**Status**: 🟢 ACTIVE - ML/AI System Database  
**Last Modified**: September 11, 2025  
**Purpose**: Machine Learning and AI System Data

**Contains**:
- ML model definitions and parameters
- AI analysis results and predictions
- Agentic AI system data
- Model performance metrics
- Training data and results
- Feature engineering data
- Prediction history and accuracy tracking

**Key Features**:
- 8 Specialized Agentic AI Agents (MLClass)
- SONNET 3.5 Portfolio AI integration
- Indian market optimization models
- Risk management AI algorithms

#### 3. `risk_management.db` *(16 KB)*
**Status**: 🟢 ACTIVE - Risk Analytics Database  
**Last Modified**: September 10, 2025  
**Purpose**: Portfolio Risk Management System

**Contains**:
- Risk assessment models
- Portfolio stress testing results
- Market scenario analysis
- Risk tolerance profiles
- Alert configurations
- Compliance tracking data

### 🔧 **Secondary Database Files**

#### 4. `ml_dashboard.db` *(36 KB)*
**Status**: 🟡 SECONDARY - ML Dashboard Data  
**Last Modified**: August 31, 2025  
**Purpose**: ML Dashboard Visualization Data

**Contains**:
- Dashboard configuration
- Chart and visualization data
- Performance tracking metrics
- User dashboard preferences

#### 5. `test.db` *(24 KB)*
**Status**: 🟡 DEVELOPMENT - Testing Database  
**Last Modified**: September 11, 2025  
**Purpose**: Development and Testing

**Contains**:
- Test data and scenarios
- Development environment data
- Feature testing results

### 📝 **Empty/Unused Database Files**

#### Inactive Files (0 KB):
- `investor_accounts.db` - Legacy investor accounts (replaced)
- `investor_scripts.db` - Legacy script storage (replaced)
- `ml_platform.db` - Unused ML platform data
- `predictram_dashboard.db` - Legacy dashboard (replaced)

## ⚙️ Database Configuration

### Configuration Location: `config.py`

```python
# Primary database configuration
_raw_db_url = os.getenv("DATABASE_URL", "sqlite:///investment_research.db")

# Database connection settings
SQLALCHEMY_DATABASE_URI = _raw_db_url
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": 20,
    "max_overflow": 30
}
```

### Environment Variable Override:
```bash
# Use PostgreSQL in production
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Use custom SQLite path
DATABASE_URL=sqlite:///custom_path/database.db
```

## 🗄️ Database Schema Overview

### Primary Tables (investment_research.db):

#### User Management:
```sql
-- Core user tables
users (id, email, password_hash, created_at, ...)
analysts (id, name, email, specialization, ...)
admins (id, username, email, permissions, ...)
```

#### Investment Data:
```sql
-- Investment and portfolio tables
reports (id, title, content, analyst_id, ...)
portfolio_stocks (id, ticker, quantity, price, ...)
investor_portfolios (id, user_id, name, ...)
stock_analysis (id, ticker, analysis, ...)
```

#### Session Management:
```sql
-- Booking and session tables
session_bookings (id, investor_id, analyst_id, ...)
google_meet_sessions (id, booking_id, meet_link, ...)
```

#### System Configuration:
```sql
-- Admin and config tables
admin_configurations (id, key, value, ...)
api_keys (id, service, key_value, ...)
contact_forms (id, name, email, message, ...)
```

## 🔄 Database Migrations

### Automatic Migration System:
The application includes automatic database migration functionality:

```python
# Migration functions in app.py
ensure_video_recording_url_column()
ensure_google_meet_columns()
create_tables_if_not_exists()
```

### Manual Migration Commands:
```bash
# Initialize database
python init_database.py

# Run specific migrations
python migrate_database.py

# Reset database (development only)
python reset_database.py
```

## 💾 Backup and Recovery

### 🔒 **Critical Backup Files**

**Daily Backup Priority**:
1. `investment_research.db` - **HIGHEST PRIORITY**
2. `ml_ai_system.db` - **HIGH PRIORITY**
3. `risk_management.db` - **MEDIUM PRIORITY**

### Backup Commands:
```bash
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "investment_research.db" "backup_investment_research_$timestamp.db"
Copy-Item "ml_ai_system.db" "backup_ml_ai_system_$timestamp.db"
Copy-Item "risk_management.db" "backup_risk_management_$timestamp.db"

# Verify backup integrity
sqlite3 backup_investment_research_$timestamp.db "PRAGMA integrity_check;"
```

### Recovery Process:
```bash
# Restore from backup
Copy-Item "backup_investment_research_20250917_120000.db" "investment_research.db"

# Restart application
python app.py
```

## 🔍 Database Maintenance

### Health Check Commands:
```bash
# Check database integrity
sqlite3 investment_research.db "PRAGMA integrity_check;"

# Analyze database size
sqlite3 investment_research.db "PRAGMA page_count; PRAGMA page_size;"

# Vacuum database (optimize)
sqlite3 investment_research.db "VACUUM;"
```

### Performance Optimization:
```sql
-- Rebuild indexes
REINDEX;

-- Analyze query plans
ANALYZE;

-- Check table statistics
SELECT name, tbl_name FROM sqlite_master WHERE type='table';
```

## 🚀 Production Deployment

### AWS RDS Migration:
For production deployment, the application supports PostgreSQL migration:

```python
# Production configuration
DATABASE_URL = "postgresql://user:pass@rds-endpoint:5432/production_db"
```

### Migration Process:
1. Export SQLite data: `python migrate_sqlite_to_postgres.py`
2. Set up RDS PostgreSQL instance
3. Update environment variables
4. Deploy application with new database URL

## 🛠️ Development Tools

### Database Inspection Tools:
```bash
# SQLite CLI
sqlite3 investment_research.db

# Python inspection
python check_database_structure.py
python analyze_db_structure.py
```

### Testing Database:
```bash
# Create test database
python test_database.py

# Verify connections
python test_startup.py
```

## 📈 Database Statistics

### Current Usage (September 17, 2025):
```
Primary Database:     135 KB (investment_research.db)
ML/AI System:         151 KB (ml_ai_system.db) 
Risk Management:       16 KB (risk_management.db)
ML Dashboard:          36 KB (ml_dashboard.db)
Testing:               24 KB (test.db)
Total Storage:        362 KB
```

### Growth Projections:
- **Light Usage**: ~1-2 MB/month
- **Medium Usage**: ~5-10 MB/month  
- **Heavy Usage**: ~20-50 MB/month

## 🔐 Security Considerations

### Database Security:
- SQLite files should be protected with file system permissions
- Regular backups stored securely
- No sensitive data in plain text
- API keys encrypted in database

### Access Control:
```python
# Database access is controlled through application layer
# No direct SQLite access in production
# All queries go through SQLAlchemy ORM
```

## 🆘 Troubleshooting

### Common Issues:

#### Database Locked Error:
```bash
# Solution: Check for running processes
ps aux | grep python
# Kill hanging processes and restart
```

#### Corruption Recovery:
```bash
# Create recovery database
sqlite3 corrupted.db ".dump" | sqlite3 recovered.db
```

#### Missing Tables:
```bash
# Reinitialize database
python init_database.py
python create_tables_if_not_exists.py
```

## 📞 Support Information

**Database Administrator**: Development Team  
**Last Updated**: September 17, 2025  
**Version**: 2.3 Production Ready  
**Environment**: Windows/AWS EC2 Compatible

---

## 🎯 Quick Reference

**Primary Database**: `investment_research.db`  
**Configuration**: `config.py` line 23  
**Backup Schedule**: Daily recommended  
**Migration Path**: SQLite → PostgreSQL for production  
**Total Files**: 9 database files (5 active, 4 unused)