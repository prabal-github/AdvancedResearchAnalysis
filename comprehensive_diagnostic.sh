#!/bin/bash

# Comprehensive EC2 Port 80 Diagnostic Script
# Run this ON your EC2 instance to diagnose the connectivity issue

echo "🔍 COMPREHENSIVE PORT 80 CONNECTIVITY DIAGNOSTIC"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 System Information:${NC}"
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime | cut -d',' -f1)"

# Check if we're on EC2
echo -e "\n${BLUE}🔍 EC2 Instance Information:${NC}"
INSTANCE_ID=$(curl -s --connect-timeout 5 http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
if [ -n "$INSTANCE_ID" ]; then
    echo "Instance ID: $INSTANCE_ID"
    echo "Public IP: $(curl -s --connect-timeout 5 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)"
    echo "Local IP: $(curl -s --connect-timeout 5 http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null)"
    echo "Region: $(curl -s --connect-timeout 5 http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)"
else
    echo "❌ Not running on EC2 or metadata service unavailable"
fi

echo -e "\n${BLUE}🔍 Service Status Check:${NC}"

# Check systemd services
services=("nginx" "predictram-research")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅ $service is running${NC}"
        echo "   Status: $(systemctl is-active $service)"
        echo "   Since: $(systemctl show $service --property=ActiveEnterTimestamp --value)"
    else
        echo -e "${RED}❌ $service is NOT running${NC}"
        echo "   Status: $(systemctl is-active $service)"
        echo "   Recent logs:"
        journalctl -u "$service" --no-pager -n 3 --since "10 minutes ago"
    fi
done

echo -e "\n${BLUE}🔌 Port Listening Status:${NC}"

# Check what's listening on our ports
echo "Processes listening on ports 80 and 5008:"
ss -tlnp | grep -E ':80 |:5008 ' || echo "No processes found on ports 80 or 5008"

echo -e "\nAll listening ports:"
ss -tlnp | head -10

echo -e "\n${BLUE}🧪 Local Connectivity Tests:${NC}"

# Test local connections
test_local_url() {
    local url=$1
    local name=$2
    echo -n "Testing $name ($url): "
    
    if curl -s --connect-timeout 10 --max-time 10 -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Success${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
}

test_local_url "http://127.0.0.1/" "Local port 80"
test_local_url "http://127.0.0.1/health" "Health endpoint"
test_local_url "http://127.0.0.1:5008/" "Flask direct"
test_local_url "http://localhost/" "Localhost port 80"

echo -e "\n${BLUE}🔥 Firewall and Network Configuration:${NC}"

# Check iptables rules
echo "IPTables status:"
if command -v iptables >/dev/null; then
    iptables -L -n | head -10
    echo "..."
    echo "Total iptables rules: $(iptables -L -n | wc -l)"
else
    echo "iptables not found"
fi

# Check if UFW is running
if command -v ufw >/dev/null; then
    echo -e "\nUFW Status:"
    ufw status
else
    echo -e "\nUFW not installed"
fi

echo -e "\n${BLUE}📡 Network Interface Configuration:${NC}"

# Show network interfaces
ip addr show | grep -A 2 -E "^[0-9]+: (eth0|ens|enp)" | head -10

echo -e "\n${BLUE}🌐 External Connectivity Test:${NC}"

# Test outbound connectivity
echo "Testing outbound connectivity:"
if curl -s --connect-timeout 10 http://checkip.amazonaws.com/ > /dev/null; then
    PUBLIC_IP=$(curl -s --connect-timeout 10 http://checkip.amazonaws.com/)
    echo -e "${GREEN}✅ Outbound connectivity working${NC}"
    echo "Detected public IP: $PUBLIC_IP"
else
    echo -e "${RED}❌ Outbound connectivity failed${NC}"
fi

echo -e "\n${BLUE}🔍 Nginx Configuration Check:${NC}"

if [ -f "/etc/nginx/sites-enabled/predictram" ]; then
    echo "Nginx site configuration:"
    echo "------------------------"
    head -20 /etc/nginx/sites-enabled/predictram
    echo "..."
else
    echo -e "${RED}❌ Nginx predictram site configuration not found${NC}"
fi

# Test nginx config
if command -v nginx >/dev/null; then
    echo -e "\nNginx configuration test:"
    nginx -t 2>&1
else
    echo -e "\n${RED}❌ Nginx not installed${NC}"
fi

echo -e "\n${BLUE}🚀 Process Information:${NC}"

# Show processes using ports 80 and 5008
echo "Processes using network ports:"
lsof -i :80 -i :5008 2>/dev/null || echo "lsof not available or no processes found"

echo -e "\n${BLUE}📋 System Resource Status:${NC}"

# Basic system resources
echo "Memory usage:"
free -h | head -2
echo -e "\nDisk usage:"
df -h / | tail -1
echo -e "\nLoad average: $(uptime | awk -F'load average:' '{print $2}')"

echo -e "\n${BLUE}🎯 DIAGNOSTIC SUMMARY:${NC}"
echo "======================================"

# Summary of findings
if systemctl is-active --quiet nginx && systemctl is-active --quiet predictram-research; then
    echo -e "${GREEN}✅ Both services are running${NC}"
else
    echo -e "${RED}❌ One or both services are not running${NC}"
fi

if ss -tlnp | grep -q ":80"; then
    echo -e "${GREEN}✅ Port 80 is listening${NC}"
else
    echo -e "${RED}❌ Nothing listening on port 80${NC}"
fi

if curl -s -f http://127.0.0.1/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Local HTTP access working${NC}"
else
    echo -e "${RED}❌ Local HTTP access failing${NC}"
fi

echo -e "\n${YELLOW}🔧 NEXT STEPS:${NC}"
echo "1. If services aren't running: sudo systemctl restart nginx predictram-research"
echo "2. If ports aren't listening: Check service logs with journalctl"
echo "3. If local access fails: Check nginx and flask configurations"
echo "4. If everything above works: The issue is network-level (ACLs, routing)"

echo -e "\n${BLUE}📞 Run this script and share the output for further diagnosis${NC}"