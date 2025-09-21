# 🚀 Complete AWS Deployment Guide for research.predictram.com

## 📋 Overview
Deploy your AI-Powered Investment Research Platform to AWS with production-ready configuration at https://research.predictram.com

## 🛠️ Prerequisites
- AWS Account with admin permissions
- Domain: predictram.com (or subdomain control)
- AWS CLI installed and configured
- SSH key pair for EC2 access

---

## 🏗️ Step 1: AWS Infrastructure Setup

### 1.1 Create EC2 Instance
```bash
# Launch EC2 instance with these specs:
- AMI: Ubuntu 22.04 LTS (ami-0c7217cdde317cfec)
- Instance Type: t3.medium (minimum for ML models)
- Storage: 30GB+ GP3 SSD
- Key Pair: Your existing SSH key
```

### 1.2 Security Group Configuration
```bash
# Create security group: research-sg
- SSH (22): Your IP address only
- HTTP (80): 0.0.0.0/0 (for Let's Encrypt)
- HTTPS (443): 0.0.0.0/0
- Custom TCP (5008): 0.0.0.0/0 (temporary for testing)
```

### 1.3 Elastic IP (Optional but Recommended)
```bash
# Allocate Elastic IP for consistent domain mapping
aws ec2 allocate-address --domain vpc
# Associate with your EC2 instance
```

---

## 🌐 Step 2: Domain Configuration

### 2.1 Route 53 Setup
```bash
# Create hosted zone for predictram.com (if not exists)
aws route53 create-hosted-zone --name predictram.com --caller-reference $(date +%s)

# Create A record for research.predictram.com
# Point to your EC2 Elastic IP
```

### 2.2 DNS Record Example
```json
{
    "Type": "A",
    "Name": "research.predictram.com",
    "Value": "YOUR_EC2_ELASTIC_IP",
    "TTL": 300
}
```

---

## 🗄️ Step 3: RDS Database Setup

### 3.1 Create RDS PostgreSQL Instance
```bash
# RDS Configuration:
- Engine: PostgreSQL 15.x
- Instance Class: db.t3.micro (can scale up)
- Storage: 20GB GP3 (auto-scaling enabled)
- Multi-AZ: No (for cost, enable for HA)
- Public Access: No
- VPC Security Group: Allow port 5432 from EC2 security group
```

### 3.2 Database Setup Commands
```bash
# Run on your local machine or EC2:
aws rds create-db-instance \
    --db-instance-identifier research-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username research_admin \
    --master-user-password YOUR_SECURE_PASSWORD \
    --allocated-storage 20 \
    --storage-type gp3 \
    --db-name research \
    --no-publicly-accessible \
    --vpc-security-group-ids sg-YOUR_DB_SECURITY_GROUP
```

---

## 🚀 Step 4: Application Deployment

### 4.1 Connect to EC2 Instance
```bash
ssh -i your-key.pem ubuntu@research.predictram.com
```

### 4.2 Run Deployment Script
```bash
# Copy and run the deployment script
wget https://raw.githubusercontent.com/your-repo/deployment/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

### 4.3 Upload Your Application Files
```bash
# Option 1: Using Git (recommended)
sudo -u research git clone https://github.com/your-repo/research-platform.git /var/www/research/

# Option 2: Using SCP/SFTP
# Upload your entire application directory to /var/www/research/
```

### 4.4 Set File Permissions
```bash
sudo chown -R research:research /var/www/research/
sudo chmod 755 /var/www/research/
sudo chmod 600 /var/www/research/.env
```

---

## ⚙️ Step 5: Environment Configuration

### 5.1 Update Production Environment
```bash
# Edit the environment file
sudo -u research nano /var/www/research/.env

# Use the .env.production template provided
# Update these critical values:
- SECRET_KEY: Generate with python -c "import secrets; print(secrets.token_hex(32))"
- DATABASE_URL: Your RDS PostgreSQL connection string
- ANTHROPIC_API_KEY: Your Claude API key
- AWS credentials
- Domain settings
```

### 5.2 Initialize Database
```bash
sudo -u research bash
cd /var/www/research
source venv/bin/activate
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

---

## 🔒 Step 6: SSL and Security Setup

### 6.1 Install SSL Certificate
```bash
# Run the SSL setup script
sudo ./deployment/setup_ssl.sh

# Update email in the script before running:
# Replace: your-email@example.com with your actual email
```

### 6.2 Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### 6.3 Security Hardening
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh

# Set up fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## ▶️ Step 7: Start Services

### 7.1 Start Application Services
```bash
# Start the research application
sudo systemctl start research
sudo systemctl enable research

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status research
sudo systemctl status nginx
```

### 7.2 Verify Deployment
```bash
# Check if application is running
curl -I http://localhost:5008/

# Check SSL certificate
curl -I https://research.predictram.com/

# View logs
sudo journalctl -u research -f
```

---

## 🧪 Step 8: Testing and Monitoring

### 8.1 Application Testing
```bash
# Test main endpoints:
curl https://research.predictram.com/
curl https://research.predictram.com/api/health
curl https://research.predictram.com/ai_research_assistant
```

### 8.2 Set Up Monitoring
```bash
# Install CloudWatch agent (optional)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### 8.3 Log Monitoring
```bash
# Create log directory
sudo mkdir -p /var/log/research
sudo chown research:research /var/log/research

# Set up log rotation
sudo tee /etc/logrotate.d/research << 'LOGROTATE'
/var/log/research/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 research research
    postrotate
        systemctl reload research
    endscript
}
LOGROTATE
```

---

## 🔧 Step 9: Post-Deployment Configuration

### 9.1 Performance Optimization
```bash
# Optimize PostgreSQL connection pooling
# Update .env with:
SQLALCHEMY_ENGINE_OPTIONS={
    "pool_size": 10,
    "pool_recycle": 3600,
    "pool_pre_ping": true
}
```

### 9.2 Backup Strategy
```bash
# Set up automated RDS backups
aws rds modify-db-instance \
    --db-instance-identifier research-db \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

---

## 🚨 Troubleshooting

### Common Issues:

1. **Application won't start:**
   ```bash
   sudo journalctl -u research -n 50
   # Check environment variables and database connection
   ```

2. **SSL certificate issues:**
   ```bash
   sudo certbot renew --dry-run
   sudo nginx -t
   ```

3. **Database connection errors:**
   ```bash
   # Check RDS security group allows EC2 connection
   # Verify DATABASE_URL in .env file
   ```

4. **Permission issues:**
   ```bash
   sudo chown -R research:research /var/www/research/
   sudo systemctl restart research
   ```

---

## 📊 Step 10: Final Verification

### 10.1 Complete Feature Test
1. Visit https://research.predictram.com/
2. Test user registration/login
3. Upload a research report
4. Test AI analysis features
5. Verify real-time market data
6. Check admin dashboard

### 10.2 Performance Check
```bash
# Load testing (install apache2-utils)
sudo apt install apache2-utils
ab -n 100 -c 10 https://research.predictram.com/
```

---

## 🎉 Deployment Complete!

Your AI-Powered Investment Research Platform is now live at:
**https://research.predictram.com**

### Key URLs:
- Main Dashboard: https://research.predictram.com/
- AI Research Assistant: https://research.predictram.com/ai_research_assistant
- Admin Panel: https://research.predictram.com/admin/research_topics
- API Documentation: https://research.predictram.com/api/

### Maintenance Commands:
```bash
# Restart application
sudo systemctl restart research

# View logs
sudo journalctl -u research -f

# Update application
cd /var/www/research && git pull && sudo systemctl restart research

# Renew SSL certificate
sudo certbot renew
```

## 📞 Support
For issues or questions:
- Check logs: `sudo journalctl -u research -f`
- Verify environment: `sudo -u research cat /var/www/research/.env`
- Test database: Connect to RDS and verify tables exist