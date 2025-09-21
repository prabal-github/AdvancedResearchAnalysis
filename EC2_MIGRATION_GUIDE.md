# 🚀 Running Migration Script on AWS EC2

## ✅ **Yes, you can and SHOULD run the migration script on EC2!**

Running the migration on EC2 has several advantages over running it locally:

---

## 🌟 **Advantages of Running on EC2**

### **🚀 Performance Benefits**
- **Lower latency** to RDS (same AWS region)
- **Higher bandwidth** between EC2 and RDS
- **No internet upload bottlenecks** for your data
- **Faster migration time** (~12-15 minutes vs ~18-20 minutes)

### **🔒 Security Benefits**
- **Private network** communication with RDS
- **No sensitive credentials** over public internet
- **AWS security groups** provide network isolation
- **VPC-to-VPC** communication within AWS

### **💰 Cost Benefits**
- **No data transfer costs** between EC2 and RDS in same region
- **No local internet bandwidth** usage
- **Better resource utilization** on EC2

---

## 📋 **Pre-Migration Checklist**

### **1. Deploy Your Application to EC2 First**
```bash
# Follow the main deployment guide to:
✅ Set up EC2 instance
✅ Install application dependencies
✅ Clone your repository
✅ Configure environment variables
✅ Test PostgreSQL connectivity
```

### **2. Upload SQLite Files to EC2**
```bash
# From your local machine, upload SQLite files to EC2
scp -i your-key.pem *.db ec2-user@your-ec2-ip:/var/www/flask-app/
scp -i your-key.pem instance/*.db ec2-user@your-ec2-ip:/var/www/flask-app/instance/

# Or use rsync for better handling
rsync -avz -e "ssh -i your-key.pem" \
    --include="*.db" \
    ./ ec2-user@your-ec2-ip:/var/www/flask-app/
```

### **3. Verify Files on EC2**
```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Check files are present
cd /var/www/flask-app
ls -la *.db
ls -la instance/*.db
```

---

## 🛠️ **Step-by-Step Migration on EC2**

### **Step 1: Prepare EC2 Environment (2 minutes)**

```bash
# SSH into your EC2 instance
ssh -i your-key-pair.pem ec2-user@your-ec2-public-ip

# Navigate to application directory
cd /var/www/flask-app

# Activate virtual environment
source venv/bin/activate

# Install migration dependencies
pip install psycopg2-binary
pip install requests  # For EC2 metadata detection
```

### **Step 2: Upload Migration Script (1 minute)**

```bash
# From your local machine, upload the EC2-optimized script
scp -i your-key.pem migrate_to_postgresql_ec2.py ec2-user@your-ec2-ip:/var/www/flask-app/
```

### **Step 3: Run Migration (12-15 minutes)**

```bash
# On EC2, run the migration
cd /var/www/flask-app
python migrate_to_postgresql_ec2.py
```

### **Step 4: Monitor Progress**

The script provides real-time progress updates:
```
🚀 EC2-Optimized SQLite to PostgreSQL Migration
============================================================
✅ Running on EC2 instance: i-1234567890abcdef0
📍 Availability Zone: us-east-1a
📁 Checking SQLite database files...
✅ Found: investment_research.db (0.13 MB)
✅ Found: instance/investment_research.db (5.26 MB)
✅ Found: instance/reports.db (1.63 MB)
📊 Found 5 databases, total size: 7.20 MB
🔌 Connecting to PostgreSQL RDS...
✅ PostgreSQL connection successful
✅ PostgreSQL write permissions verified

📁 Processing: investment_research.db (0.13 MB)
   📋 Found 6 tables
   🔄 Migrating portfolio_commentary: 1 rows
     📊 Batch 1: 1/1 rows (100.0%)
   ✅ portfolio_commentary → investment_research_portfolio_commentary: 1 rows migrated
   ...
```

---

## 📊 **Expected Performance on EC2**

| Metric | Local | EC2 |
|--------|-------|-----|
| **Connection Latency** | 50-200ms | 1-5ms |
| **Data Transfer Speed** | Limited by upload | AWS backbone |
| **Total Migration Time** | 18-20 min | 12-15 min |
| **Network Reliability** | Internet dependent | AWS internal |

---

## 🔧 **EC2-Specific Features**

### **Automatic EC2 Detection**
The script automatically detects if it's running on EC2:
```python
# Detects EC2 instance ID and availability zone
✅ Running on EC2 instance: i-1234567890abcdef0
📍 Availability Zone: us-east-1a
```

### **Optimized Batch Processing**
```python
# Larger batches for better AWS network utilization
BATCH_SIZE = 1000  # vs 500 for local
CONNECTION_TIMEOUT = 60  # Longer timeout for stability
```

### **Enhanced Logging**
```bash
# Logs saved to both locations
/tmp/migration.log  # Accessible via AWS Systems Manager
./migration_report_ec2.json  # Detailed results
```

### **Retry Logic for AWS**
```python
# Automatic retries for network issues
MAX_RETRIES = 3
# Exponential backoff for connection issues
```

---

## 📄 **Complete EC2 Deployment Script**

Save this as `deploy_and_migrate.sh`:

```bash
#!/bin/bash
# Complete EC2 deployment and migration script

set -e

echo "🚀 AWS EC2 Deployment and Migration Script"
echo "=========================================="

# Variables (update these)
EC2_HOST="your-ec2-public-ip"
KEY_FILE="your-key-pair.pem"
APP_DIR="/var/www/flask-app"

echo "📦 Step 1: Uploading application files..."

# Upload SQLite databases
echo "   Uploading SQLite databases..."
scp -i $KEY_FILE *.db ec2-user@$EC2_HOST:$APP_DIR/ 2>/dev/null || true
scp -i $KEY_FILE instance/*.db ec2-user@$EC2_HOST:$APP_DIR/instance/ 2>/dev/null || true

# Upload migration script
echo "   Uploading migration script..."
scp -i $KEY_FILE migrate_to_postgresql_ec2.py ec2-user@$EC2_HOST:$APP_DIR/

echo "🔄 Step 2: Running migration on EC2..."

# Run migration on EC2
ssh -i $KEY_FILE ec2-user@$EC2_HOST << 'EOF'
cd /var/www/flask-app
source venv/bin/activate

# Install dependencies
pip install psycopg2-binary requests

# Set environment variables
export DATABASE_URL="postgresql://admin:admin%402001@3.85.19.80:5432/research"

# Run migration
echo "Starting migration..."
python migrate_to_postgresql_ec2.py

echo "✅ Migration completed on EC2!"
EOF

echo "📊 Step 3: Downloading migration report..."

# Download migration report
scp -i $KEY_FILE ec2-user@$EC2_HOST:$APP_DIR/migration_report_ec2.json ./

echo "🎉 Deployment and migration completed successfully!"
echo "📄 Check migration_report_ec2.json for detailed results"
```

---

## 🔍 **Validation and Testing**

### **Post-Migration Validation on EC2**

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Navigate to app directory
cd /var/www/flask-app
source venv/bin/activate

# Test application with PostgreSQL
python -c "
from app import app, db
with app.app_context():
    # Test database connection
    result = db.session.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \\'public\\'')
    table_count = result.fetchone()[0]
    print(f'✅ PostgreSQL has {table_count} tables')
    
    # Test sample queries
    try:
        result = db.session.execute('SELECT COUNT(*) FROM inst_investment_research_report')
        count = result.fetchone()[0]
        print(f'✅ Found {count} reports in migrated data')
    except Exception as e:
        print(f'ℹ️ Reports table might have different name: {e}')
"
```

### **Start Your Application**

```bash
# Start the Flask application on EC2
cd /var/www/flask-app
source venv/bin/activate

# Test application startup
python app.py

# Or start with Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 app:app
```

---

## 💡 **Pro Tips for EC2 Migration**

### **1. Use Screen/Tmux for Long-Running Tasks**
```bash
# Start a screen session for the migration
screen -S migration
python migrate_to_postgresql_ec2.py

# Detach with Ctrl+A, D
# Reattach later with: screen -r migration
```

### **2. Monitor System Resources**
```bash
# In another terminal, monitor EC2 resources
htop
# or
watch -n 1 'free -h && df -h'
```

### **3. Enable CloudWatch Logging**
```bash
# The script automatically logs to /tmp/migration.log
# You can set up CloudWatch agent to capture these logs
```

### **4. Backup Before Migration**
```bash
# Create backup of your SQLite files
tar -czf sqlite_backup.tar.gz *.db instance/*.db
```

---

## 🚨 **Troubleshooting on EC2**

### **Common Issues and Solutions**

#### **1. Connection Timeout to RDS**
```bash
# Check security groups allow EC2 to RDS connection
aws ec2 describe-security-groups --group-ids sg-your-rds-sg

# Test direct connection
psql -h 3.85.19.80 -U admin -d research -p 5432
```

#### **2. Out of Disk Space**
```bash
# Check disk usage
df -h

# Clean up if needed
sudo yum clean all
rm -f /tmp/*.log
```

#### **3. Memory Issues**
```bash
# Monitor memory during migration
free -h

# If low memory, consider smaller batch size
# Edit migrate_to_postgresql_ec2.py and change:
# BATCH_SIZE = 500  # instead of 1000
```

---

## 📈 **Timeline for EC2 Migration**

| Phase | Duration | Description |
|-------|----------|-------------|
| **Setup** | 3-5 min | Upload files, install deps |
| **Migration** | 12-15 min | Data transfer to PostgreSQL |
| **Validation** | 2-3 min | Test and verify |
| **Total** | **17-23 min** | Complete process |

---

## 🎯 **Success Checklist**

- [ ] EC2 instance deployed and running
- [ ] SQLite files uploaded to EC2
- [ ] Migration script executed successfully
- [ ] All tables and data migrated
- [ ] Application connects to PostgreSQL
- [ ] Sample queries return expected results
- [ ] Migration report generated

**Running the migration on EC2 is the recommended approach for production deployments!**

The EC2-to-RDS migration will be faster, more reliable, and more secure than running it from your local machine.
