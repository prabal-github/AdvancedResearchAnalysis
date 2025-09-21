#!/usr/bin/env python3
"""
PredictRAM Model Publishing Permission Fixer
Diagnoses and fixes directory permission issues for ML model publishing
"""

import os
import stat
import tempfile
import sys
from pathlib import Path
import subprocess

def check_permissions():
    """Check current permission status"""
    print("🔍 PredictRAM Permission Diagnostics")
    print("=" * 50)
    
    app_dir = Path.cwd()
    artifacts_dir = app_dir / 'secure_artifacts'
    
    print(f"📂 App Directory: {app_dir}")
    print(f"📦 Artifacts Directory: {artifacts_dir}")
    print(f"👤 Current User: {os.getenv('USER', 'unknown')}")
    print(f"🆔 User ID: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
    
    # Check directory existence and permissions
    directories_to_check = [
        app_dir,
        artifacts_dir,
        Path.home() / '.predictram_artifacts',
        Path('/tmp') / 'predictram_artifacts'
    ]
    
    writable_dirs = []
    
    for directory in directories_to_check:
        print(f"\n📁 Checking: {directory}")
        
        if directory.exists():
            print(f"   ✅ Exists: Yes")
            
            # Check if it's a directory
            if directory.is_dir():
                print(f"   📂 Is Directory: Yes")
                
                # Check read permission
                if os.access(directory, os.R_OK):
                    print(f"   👁️ Read Access: Yes")
                else:
                    print(f"   ❌ Read Access: No")
                
                # Check write permission
                if os.access(directory, os.W_OK):
                    print(f"   ✏️ Write Access: Yes")
                    writable_dirs.append(directory)
                else:
                    print(f"   ❌ Write Access: No")
                
                # Check execute permission
                if os.access(directory, os.X_OK):
                    print(f"   🏃 Execute Access: Yes")
                else:
                    print(f"   ❌ Execute Access: No")
                
                # Show numeric permissions
                try:
                    permissions = oct(directory.stat().st_mode)[-3:]
                    print(f"   🔢 Permissions: {permissions}")
                except Exception as e:
                    print(f"   ⚠️ Cannot read permissions: {e}")
                    
            else:
                print(f"   ❌ Is Directory: No")
        else:
            print(f"   ❌ Exists: No")
    
    return writable_dirs

def test_write_access(directory):
    """Test actual write access by creating a file"""
    try:
        test_file = directory / '.write_test'
        test_file.write_text('test write access')
        test_file.unlink()
        return True
    except Exception as e:
        print(f"   ❌ Write test failed: {e}")
        return False

def fix_permissions():
    """Attempt to fix permissions"""
    print("\n🔧 Attempting Permission Fixes")
    print("=" * 50)
    
    app_dir = Path.cwd()
    artifacts_dir = app_dir / 'secure_artifacts'
    
    # Try to create artifacts directory
    try:
        artifacts_dir.mkdir(exist_ok=True)
        print(f"✅ Created/verified artifacts directory")
    except Exception as e:
        print(f"❌ Could not create artifacts directory: {e}")
    
    # Try to set permissions
    if artifacts_dir.exists():
        try:
            # Set directory permissions: owner=rwx, group=rwx, others=rx
            os.chmod(artifacts_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            print(f"✅ Set permissions on artifacts directory")
        except Exception as e:
            print(f"⚠️ Could not set permissions: {e}")
    
    # Test write access
    if artifacts_dir.exists():
        if test_write_access(artifacts_dir):
            print(f"✅ Primary artifacts directory is writable")
            return artifacts_dir
    
    # Try alternative locations
    alternative_locations = [
        Path.home() / '.predictram_artifacts',
        Path('/tmp') / 'predictram_artifacts',
        Path(tempfile.gettempdir()) / 'predictram_artifacts'
    ]
    
    for alt_dir in alternative_locations:
        try:
            alt_dir.mkdir(exist_ok=True)
            if test_write_access(alt_dir):
                print(f"✅ Alternative directory is writable: {alt_dir}")
                return alt_dir
        except Exception as e:
            print(f"❌ Alternative {alt_dir} failed: {e}")
    
    print(f"❌ No writable directory found")
    return None

def suggest_solutions():
    """Suggest solutions based on the environment"""
    print("\n💡 Suggested Solutions")
    print("=" * 50)
    
    print("1. 🔧 Manual Permission Fix:")
    print("   sudo chmod 775 secure_artifacts")
    print("   sudo chown $USER:$USER secure_artifacts")
    
    print("\n2. 🏠 Use Home Directory:")
    print("   mkdir -p ~/.predictram_artifacts")
    print("   chmod 755 ~/.predictram_artifacts")
    
    print("\n3. 🐳 For Docker/Container Environments:")
    print("   chmod 777 secure_artifacts")
    
    print("\n4. 🌐 For Web Server Environments:")
    print("   sudo chown www-data:www-data secure_artifacts")
    print("   sudo chmod 775 secure_artifacts")
    
    print("\n5. 🔒 For Production Servers:")
    print("   Create /opt/predictram/artifacts with proper ownership")
    print("   sudo mkdir -p /opt/predictram/artifacts")
    print("   sudo chown $USER:www-data /opt/predictram/artifacts")
    print("   sudo chmod 775 /opt/predictram/artifacts")

def main():
    """Main function"""
    print("🚀 PredictRAM Model Publishing Permission Checker")
    print("=" * 60)
    
    # Check current permissions
    writable_dirs = check_permissions()
    
    # Try to fix permissions
    working_dir = fix_permissions()
    
    if working_dir:
        print(f"\n✅ SUCCESS: Found writable directory: {working_dir}")
        print("Your Flask application should now be able to publish models!")
    else:
        print(f"\n❌ FAILED: No writable directory found")
        suggest_solutions()
        
        print(f"\n⚠️ The application will attempt to use temporary directories,")
        print(f"but published models may not persist across restarts.")
    
    print(f"\n🔄 To apply changes, restart your Flask application")

if __name__ == "__main__":
    main()
