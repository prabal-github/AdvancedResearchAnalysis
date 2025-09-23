# 📋 AWS EC2 Deployment Checklist

## Quick Start Guide for Developers

### 🚀 **STEP 1: Apply Critical Fixes**

```bash
# Run the automated fix script
python apply_aws_fixes.py
```

### 🔧 **STEP 2: Pre-Deployment Setup**

#### A. **Set Up RDS Database**

- [ ] Create PostgreSQL RDS instance
- [ ] Configure security groups (allow port 5432 from EC2)
- [ ] Note down database endpoint and credentials

#### B. **Prepare EC2 Instance**

- [ ] Launch EC2 instance (t3.medium or larger recommended)
- [ ] Install Python 3.9+, pip, git
- [ ] Create application directory: `/opt/flask-app`
- [ ] Clone your repository to EC2

#### C. **Configure Environment**

- [ ] Copy `.env.production` to `.env` on EC2
- [ ] Fill in actual values in `.env`:
  ```bash
  DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname
  SECRET_KEY=your-256-bit-random-key
  DOMAIN_NAME=your-ec2-public-ip-or-domain
  # ... other required values
  ```

### 🗄️ **STEP 3: Database Initialization**

```bash
# On EC2 instance
cd /opt/flask-app
pip3 install -r requirements.txt
python3 aws_database_setup.py
```

### ✅ **STEP 4: Start Application**

```bash
# Test run
python3 app.py

# For production, use systemd service (see guide)
sudo systemctl start flask-app
sudo systemctl enable flask-app
```

### 🔍 **STEP 5: Validation**

```bash
# Test endpoints
curl http://your-ec2-ip:80/health
curl http://your-ec2-ip:80/config-check

# Should return status: "healthy" and "ready"
```

---

## 🚨 **Critical Issues Fixed**

✅ **Database Configuration**: Unified SQLite/PostgreSQL handling  
✅ **Environment Detection**: Automatic AWS vs local detection  
✅ **Hardcoded URLs**: Dynamic URL generation based on environment  
✅ **Connection Pooling**: Production-ready database settings  
✅ **Health Checks**: Monitoring endpoints for load balancers  
✅ **Error Handling**: Graceful fallbacks for missing dependencies

---

## 🔗 **Quick Links**

- 📖 **Full Guide**: `AWS_DEPLOYMENT_FIXES_GUIDE.md`
- 🔧 **Auto-Fix Script**: `python apply_aws_fixes.py`
- 🗄️ **Database Setup**: `python3 aws_database_setup.py`
- 🌐 **Health Check**: `http://your-domain/health`
- ⚙️ **Config Check**: `http://your-domain/config-check`

---

## 📞 **Need Help?**

**Database Connection Issues:**

```bash
# Test database connectivity
python3 -c "
from config import Config
from sqlalchemy import create_engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
engine.execute('SELECT 1')
print('✅ Database OK')
"
```

**Application Won't Start:**

1. Check logs: `journalctl -u flask-app -f`
2. Verify environment: `python3 -c "import os; print(os.getenv('DATABASE_URL'))"`
3. Test imports: `python3 -c "from app import app; print('✅ App loads OK')"`

**Performance Issues:**

- Monitor: `curl http://your-domain/health`
- Check DB pool: Set `DB_POOL_SIZE=20` in environment
- Enable monitoring: AWS CloudWatch or custom solution

---

⚠️ **Remember**: Always test in staging environment first!
