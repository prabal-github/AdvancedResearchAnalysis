# Flask Investment Research Application - AWS EC2 Deployment Quick Start Guide

## 🚀 Quick Deployment (One-Command Solution)

```bash
# Make deployment script executable and run
chmod +x complete_aws_deployment.sh
./complete_aws_deployment.sh
```

This script will:
1. ✅ Check prerequisites (AWS CLI, credentials)
2. 🔧 Get your deployment preferences
3. 📦 Package your application
4. ☁️ Deploy AWS infrastructure
5. 🖥️ Configure EC2 instance
6. 🚀 Deploy and start your application
7. 🔒 Setup SSL (if domain provided)
8. ✅ Verify deployment

## 📋 Prerequisites

### 1. AWS Setup
```bash
# Install AWS CLI (if not installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

### 2. Create EC2 Key Pair
```bash
# Create a new key pair
aws ec2 create-key-pair --key-name flask-app-key --query 'KeyMaterial' --output text > flask-app-key.pem
chmod 400 flask-app-key.pem
```

### 3. Domain Setup (Optional)
- Purchase domain from Route 53 or external provider
- Update nameservers to point to AWS Route 53 (if using external domain)

## 🎯 Manual Deployment Steps

If you prefer manual control:

### Step 1: Deploy Infrastructure
```bash
aws cloudformation deploy \
  --template-file aws-infrastructure.yaml \
  --stack-name flask-investment-app \
  --parameter-overrides \
    ParameterKey=KeyPairName,ParameterValue=flask-app-key \
    ParameterKey=InstanceType,ParameterValue=t3.medium \
    ParameterKey=DomainName,ParameterValue=your-domain.com \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### Step 2: Get Instance Information
```bash
# Get public IP
PUBLIC_IP=$(aws cloudformation describe-stacks \
  --stack-name flask-investment-app \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
  --output text)

echo "Public IP: $PUBLIC_IP"
```

### Step 3: Deploy Application
```bash
# Upload files to server
scp -i flask-app-key.pem app.py ubuntu@$PUBLIC_IP:/tmp/
scp -i flask-app-key.pem *.db ubuntu@$PUBLIC_IP:/tmp/
scp -i flask-app-key.pem deploy_to_ec2.sh ubuntu@$PUBLIC_IP:/tmp/

# Connect and deploy
ssh -i flask-app-key.pem ubuntu@$PUBLIC_IP
sudo chmod +x /tmp/deploy_to_ec2.sh
sudo /tmp/deploy_to_ec2.sh
```

## ⚙️ Configuration

### Environment Variables (.env.production)
```bash
# SSH to server and edit
ssh -i flask-app-key.pem ubuntu@$PUBLIC_IP
sudo nano /opt/flask-app/.env.production
```

Required updates:
```env
SECRET_KEY=your-super-secure-production-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
CLAUDE_API_KEY=your-claude-api-key
SES_SENDER_EMAIL=support@yourdomain.com
```

### SSL Certificate Setup
```bash
# For custom domain
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test certificate renewal
sudo certbot renew --dry-run
```

## 🔧 Management Commands

### Service Management
```bash
# Start/Stop/Restart application
sudo systemctl start flask-investment-app
sudo systemctl stop flask-investment-app
sudo systemctl restart flask-investment-app

# Check status
sudo systemctl status flask-investment-app

# Enable auto-start on boot
sudo systemctl enable flask-investment-app
```

### Log Monitoring
```bash
# Application logs
sudo tail -f /var/log/flask-app/error.log
sudo tail -f /var/log/flask-app/access.log

# System logs
sudo journalctl -u flask-investment-app -f
```

### Database Management
```bash
# Backup databases
sudo -u flask-app /opt/flask-app/scripts/backup.sh

# Check database integrity
sudo -u flask-app sqlite3 /opt/flask-app/data/investment_research.db "PRAGMA integrity_check;"

# View backup files
ls -la /opt/flask-app/backups/
```

### Performance Monitoring
```bash
# System resources
htop
df -h
free -h

# Application health check
curl http://localhost:5008/health

# Nginx status
sudo systemctl status nginx
sudo nginx -t  # Test configuration
```

## 🚨 Troubleshooting

### Application Not Starting
```bash
# Check service status
sudo systemctl status flask-investment-app

# Check logs for errors
sudo journalctl -u flask-investment-app --no-pager -l

# Verify Gunicorn config
sudo -u flask-app /opt/flask-app/venv/bin/gunicorn --check-config gunicorn.conf.py

# Test manual start
sudo -u flask-app /opt/flask-app/venv/bin/python /opt/flask-app/wsgi.py
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

### Database Issues
```bash
# Check database permissions
ls -la /opt/flask-app/data/

# Fix permissions if needed
sudo chown -R flask-app:flask-app /opt/flask-app/data/
sudo chmod 644 /opt/flask-app/data/*.db

# Test database connection
sudo -u flask-app python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/flask-app/data/investment_research.db')
print('Database connection successful')
conn.close()
"
```

### Network Issues
```bash
# Check port availability
sudo netstat -tlnp | grep :5008
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Test internal connectivity
curl -I http://localhost:5008/health

# Check firewall (if enabled)
sudo ufw status
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Automated health check
sudo -u flask-app /opt/flask-app/scripts/health_check.sh

# Set up monitoring cron job
sudo crontab -e
# Add: */5 * * * * /opt/flask-app/scripts/monitor.sh
```

### Regular Maintenance
```bash
# Weekly backup (add to cron)
0 2 * * 0 /opt/flask-app/scripts/backup.sh

# Daily log rotation (already configured)
# Monthly system updates
0 3 1 * * apt update && apt upgrade -y

# Disk space monitoring
df -h | awk '$5 > "80%" {print $0}' | mail -s "Disk Space Alert" admin@yourdomain.com
```

## 🔐 Security Best Practices

### 1. Update System Regularly
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot  # If kernel updates
```

### 2. Configure Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### 3. Monitor Access Logs
```bash
# Check for suspicious activity
sudo tail -f /var/log/nginx/access.log | grep -E "(404|500|suspicious)"

# Set up fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 4. Backup Strategy
```bash
# Automated S3 backup script
aws s3 sync /opt/flask-app/backups/ s3://your-backup-bucket/flask-app-backups/
```

## 📱 Mobile & API Access

Your application will be accessible at:
- **Web Interface**: `https://your-domain.com`
- **API Endpoints**: `https://your-domain.com/api/`
- **Health Check**: `https://your-domain.com/health`

## 🆘 Support & Resources

### Log Locations
- Application Logs: `/var/log/flask-app/`
- Nginx Logs: `/var/log/nginx/`
- System Logs: `journalctl -u flask-investment-app`

### Configuration Files
- App Config: `/opt/flask-app/.env.production`
- Gunicorn: `/opt/flask-app/gunicorn.conf.py`
- Nginx: `/etc/nginx/sites-available/flask-investment-app`
- Systemd: `/etc/systemd/system/flask-investment-app.service`

### Performance Optimization
- **Database**: Regular VACUUM and ANALYZE
- **Memory**: Monitor with `free -h`
- **CPU**: Monitor with `htop`
- **Disk**: Regular cleanup of old logs and backups

## 🎉 Success Verification

After deployment, verify these endpoints:
1. **Main App**: `https://your-domain.com/` - Should show investment dashboard
2. **VS Terminal MLClass**: `https://your-domain.com/vs_terminal_MLClass` - Agentic AI system
3. **Health Check**: `https://your-domain.com/health` - Should return "OK"
4. **API Status**: `https://your-domain.com/api/status` - Should return JSON status

Your Flask Investment Research Application with MLClass Agentic AI is now running 24/7 on AWS EC2! 🚀