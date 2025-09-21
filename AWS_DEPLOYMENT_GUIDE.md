# 🚀 AWS Production Deployment Guide
## Flask Investment Research Platform - research.predictram.com

### 📋 **Pre-Deployment Requirements**

**✅ Infrastructure Ready:**
- **Domain**: `research.predictram.com` (DNS pointing to your EC2 instance)
- **Database**: PostgreSQL RDS at `3.85.19.80:5432/research`
- **Credentials**: `admin:admin@2001`
- **SSL Certificate**: Will be auto-generated with Let's Encrypt

---

## 🎯 **Step-by-Step Deployment Process**

### **1️⃣ Prepare Your EC2 Instance**

**Launch EC2 Instance:**
```bash
# Minimum Requirements:
# - Instance Type: t3.medium or larger (2 vCPU, 4GB RAM)
# - Storage: 20GB+ SSD
# - Security Groups: Allow ports 22, 80, 443, 5000
# - OS: Ubuntu 22.04 LTS
```

**Connect to your instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

### **2️⃣ Initial Server Setup**

**Run the setup script:**
```bash
# Upload and run the setup script
chmod +x deploy-setup.sh
./deploy-setup.sh
```

**Or run manually:**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx and Certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Reboot to apply group changes
sudo reboot
```

---

### **3️⃣ Deploy Your Application**

**Clone/Upload your application:**
```bash
# Create app directory
sudo mkdir -p /opt/research-app
sudo chown $USER:$USER /opt/research-app

# Upload your application files to /opt/research-app
# Include all the files we created: Dockerfile, docker-compose.yml, etc.
```

**Set up environment variables:**
```bash
cd /opt/research-app

# Copy and edit the production environment file
cp .env.production .env

# Edit with your actual values
nano .env
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://admin:admin%402001@3.85.19.80:5432/research

# Security
SECRET_KEY=your-super-secret-production-key-256-chars-long
SESSION_COOKIE_SECURE=true

# AWS SES (for emails)
SES_ACCESS_KEY_ID=your-ses-access-key
SES_SECRET_ACCESS_KEY=your-ses-secret-key
SES_SENDER_EMAIL=support@predictram.com

# Razorpay (for payments)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# GitHub (for reports)
GITHUB_TOKEN=your-github-token
GITHUB_USERNAME=your-github-username
```

---

### **4️⃣ Initialize Database**

**Create database tables:**
```bash
# Set environment variable
export DATABASE_URL="postgresql://admin:admin%402001@3.85.19.80:5432/research"

# Install Python dependencies locally (for init script)
pip3 install flask flask-sqlalchemy psycopg2-binary

# Initialize database
python3 init_db.py
```

---

### **5️⃣ Start the Application**

**Build and start containers:**
```bash
# Build and start
sudo docker-compose up -d --build

# Check status
sudo docker-compose ps
sudo docker-compose logs -f
```

**Test the application:**
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test main application
curl http://localhost:5000
```

---

### **6️⃣ Configure Nginx & SSL**

**Set up Nginx:**
```bash
# Copy Nginx configuration
sudo cp nginx-research.conf /etc/nginx/sites-available/research
sudo ln -sf /etc/nginx/sites-available/research /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Obtain SSL Certificate:**
```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d research.predictram.com -d www.research.predictram.com

# Set up auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

### **7️⃣ Final Configuration**

**Restart services:**
```bash
sudo systemctl restart nginx
sudo docker-compose restart
```

**Test the deployment:**
```bash
# Test HTTPS
curl https://research.predictram.com/health

# Check SSL
curl -I https://research.predictram.com
```

---

## 🔧 **Production Monitoring & Maintenance**

### **Monitoring Commands:**
```bash
# Check application logs
sudo docker-compose logs -f web

# Check Nginx logs
sudo tail -f /var/log/nginx/research_access.log
sudo tail -f /var/log/nginx/research_error.log

# Check system resources
htop
df -h
free -h

# Check SSL certificate expiry
sudo certbot certificates
```

### **Maintenance Commands:**
```bash
# Update application
cd /opt/research-app
git pull  # If using Git
sudo docker-compose up -d --build

# Restart services
sudo docker-compose restart
sudo systemctl restart nginx

# Database backup
pg_dump "postgresql://admin:admin%402001@3.85.19.80:5432/research" > backup.sql

# View real-time logs
sudo docker-compose logs -f --tail=100
```

---

## 🔒 **Security Checklist**

- ✅ **SSL Certificate**: Auto-configured with Let's Encrypt
- ✅ **Security Headers**: Configured in Nginx
- ✅ **Database Security**: PostgreSQL with authentication
- ✅ **Environment Variables**: Stored securely in `.env`
- ✅ **Firewall**: Only essential ports open (22, 80, 443)
- ✅ **Container Security**: Non-root user in Docker
- ✅ **Session Security**: Secure cookies over HTTPS

---

## 🚨 **Troubleshooting**

### **Common Issues:**

**1. Database Connection Failed:**
```bash
# Test database connectivity
pg_isready -h 3.85.19.80 -p 5432 -U admin

# Check firewall rules on RDS
# Ensure EC2 security group allows connection to RDS
```

**2. Application Won't Start:**
```bash
# Check logs
sudo docker-compose logs web

# Check environment variables
sudo docker-compose exec web env | grep DATABASE_URL
```

**3. SSL Certificate Issues:**
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --dry-run
```

**4. High Memory Usage:**
```bash
# Monitor containers
sudo docker stats

# Restart if needed
sudo docker-compose restart
```

---

## 📊 **Performance Optimization**

### **Production Tuning:**
```bash
# Increase worker processes in gunicorn
# Edit docker-compose.yml:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# Enable Nginx caching for static files
# Already configured in nginx-research.conf

# Database connection pooling
# Already configured in config.py
```

---

## 🎯 **Final Verification**

After deployment, verify these endpoints:

1. **🌐 Main Site**: https://research.predictram.com
2. **💓 Health Check**: https://research.predictram.com/health
3. **📊 Investor Dashboard**: https://research.predictram.com/investor_dashboard
4. **🔐 Login System**: https://research.predictram.com/login
5. **🤖 ML Models**: https://research.predictram.com/subscribed_ml_models

---

## 📞 **Support & Monitoring**

**Application Health**: Monitor `/health` endpoint
**Database Status**: Check RDS metrics in AWS Console
**SSL Certificate**: Auto-renews every 90 days
**Logs**: Centralized in `/var/log/nginx/` and Docker logs

---

**🚀 Your Flask Investment Research Platform is now live at:**
## **https://research.predictram.com**

**All 87 database models are configured and ready for production use!** 🎉
