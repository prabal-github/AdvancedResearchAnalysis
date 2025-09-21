#!/bin/bash

# Fix PredictRAM Model Publishing Permissions
# This script fixes permission issues for ML model publishing on Ubuntu servers

echo "🔧 PredictRAM Permission Fix Script"
echo "=================================="

# Get the current working directory (where the Flask app runs)
APP_DIR=$(pwd)
ARTIFACTS_DIR="$APP_DIR/secure_artifacts"

echo "📁 Application Directory: $APP_DIR"
echo "📦 Artifacts Directory: $ARTIFACTS_DIR"

# Create secure_artifacts directory if it doesn't exist
if [ ! -d "$ARTIFACTS_DIR" ]; then
    echo "📂 Creating artifacts directory..."
    mkdir -p "$ARTIFACTS_DIR"
else
    echo "✅ Artifacts directory already exists"
fi

# Fix ownership and permissions for the artifacts directory
echo "🔐 Setting proper permissions..."

# Method 1: Try to fix permissions for current user
if [ -w "$APP_DIR" ]; then
    echo "✅ Current user has write access to app directory"
    
    # Set directory permissions: owner=rwx, group=rwx, others=rx
    chmod 775 "$ARTIFACTS_DIR" 2>/dev/null
    
    # Set default permissions for new files/directories
    chmod g+s "$ARTIFACTS_DIR" 2>/dev/null
    
    echo "✅ Permissions set for artifacts directory"
else
    echo "⚠️ Limited write access to app directory"
fi

# Method 2: Alternative location in user home directory
HOME_ARTIFACTS="$HOME/.predictram_artifacts"
echo "📂 Creating fallback directory: $HOME_ARTIFACTS"
mkdir -p "$HOME_ARTIFACTS"
chmod 755 "$HOME_ARTIFACTS"

# Method 3: System-wide directory with proper permissions
SYSTEM_ARTIFACTS="/opt/predictram/artifacts"
if [ "$EUID" -eq 0 ]; then
    echo "🔧 Running as root - creating system-wide directory"
    mkdir -p "$SYSTEM_ARTIFACTS"
    chown -R www-data:www-data "$SYSTEM_ARTIFACTS" 2>/dev/null || chown -R ubuntu:ubuntu "$SYSTEM_ARTIFACTS"
    chmod -R 775 "$SYSTEM_ARTIFACTS"
else
    echo "ℹ️ Not running as root - using user directories"
fi

# Create test file to verify write permissions
echo "🧪 Testing write permissions..."

test_locations=("$ARTIFACTS_DIR" "$HOME_ARTIFACTS" "/tmp/predictram_test")

for location in "${test_locations[@]}"; do
    mkdir -p "$location" 2>/dev/null
    
    if touch "$location/test_write.tmp" 2>/dev/null; then
        echo "✅ $location - Write access OK"
        rm -f "$location/test_write.tmp"
    else
        echo "❌ $location - No write access"
    fi
done

# Environment-specific fixes
echo "🌐 Environment-specific fixes..."

# Fix for Apache/Nginx web servers
if [ -f "/etc/apache2/apache2.conf" ] || [ -f "/etc/nginx/nginx.conf" ]; then
    echo "🌐 Web server detected - adjusting permissions for web user"
    
    # Common web server users
    for webuser in www-data nginx apache; do
        if id "$webuser" &>/dev/null; then
            echo "👤 Found web server user: $webuser"
            sudo chown -R "$webuser:$webuser" "$ARTIFACTS_DIR" 2>/dev/null || true
            sudo chmod -R 775 "$ARTIFACTS_DIR" 2>/dev/null || true
            break
        fi
    done
fi

# Fix for Docker containers
if [ -f "/.dockerenv" ]; then
    echo "🐳 Docker container detected"
    chmod -R 777 "$ARTIFACTS_DIR" 2>/dev/null || true
    echo "✅ Relaxed permissions for Docker environment"
fi

# Create startup script for automatic permission fixing
STARTUP_SCRIPT="$APP_DIR/fix_permissions.py"
cat > "$STARTUP_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Automatic permission fixer for PredictRAM model publishing
Run this before starting the Flask application
"""

import os
import stat
import tempfile
from pathlib import Path

def fix_permissions():
    """Fix directory permissions for model publishing"""
    app_dir = Path.cwd()
    artifacts_dir = app_dir / 'secure_artifacts'
    
    print(f"🔧 Fixing permissions for: {artifacts_dir}")
    
    try:
        # Create directory if it doesn't exist
        artifacts_dir.mkdir(exist_ok=True)
        
        # Set permissions
        os.chmod(artifacts_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        
        # Test write access
        test_file = artifacts_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        
        print(f"✅ Permissions fixed successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not fix permissions: {e}")
        
        # Try alternative locations
        alt_locations = [
            Path.home() / '.predictram_artifacts',
            Path('/tmp') / 'predictram_artifacts'
        ]
        
        for alt_dir in alt_locations:
            try:
                alt_dir.mkdir(exist_ok=True)
                test_file = alt_dir / '.write_test'
                test_file.write_text('test')
                test_file.unlink()
                print(f"✅ Alternative location working: {alt_dir}")
                return True
            except Exception:
                continue
        
        print(f"❌ No writable location found")
        return False

if __name__ == "__main__":
    fix_permissions()
EOF

chmod +x "$STARTUP_SCRIPT"
echo "📝 Created automatic permission fixer: $STARTUP_SCRIPT"

# Final status check
echo ""
echo "🎯 Permission Fix Summary"
echo "========================"

if [ -w "$ARTIFACTS_DIR" ]; then
    echo "✅ Primary artifacts directory is writable"
elif [ -w "$HOME_ARTIFACTS" ]; then
    echo "✅ Home artifacts directory is writable"
elif [ -w "/tmp" ]; then
    echo "✅ Temporary directory fallback available"
else
    echo "❌ No writable directories found - contact system administrator"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Restart your Flask application"
echo "2. Test model publishing from admin panel"
echo "3. If issues persist, run: python fix_permissions.py"
echo ""
echo "📍 The application will automatically use the best available directory"
