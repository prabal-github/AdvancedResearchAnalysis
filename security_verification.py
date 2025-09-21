#!/usr/bin/env python3
"""
Security Verification Script
Scans the codebase to ensure no hardcoded credentials remain
"""

import os
import re
import glob

def scan_for_hardcoded_credentials():
    """Scan all Python files for potential hardcoded credentials"""
    
    # Patterns to look for
    patterns = [
        r'admin%402001',  # Our specific password
        r'postgresql://.*:.*@.*:.*/',  # PostgreSQL URLs with credentials
        r'password\s*=\s*["\'][^"\']+["\']',  # password assignments
        r'secret\s*=\s*["\'][^"\']+["\']',  # secret assignments
    ]
    
    # Files to scan
    python_files = glob.glob('**/*.py', recursive=True)
    config_files = glob.glob('**/*.yml', recursive=True) + glob.glob('**/*.yaml', recursive=True)
    docker_files = ['Dockerfile', 'docker-compose.yml']
    
    all_files = python_files + config_files + docker_files
    
    print("🔍 Security Credential Scan Results")
    print("=" * 50)
    
    issues_found = 0
    
    for filepath in all_files:
        if not os.path.exists(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments and documentation
                        if line.strip().startswith('#') or 'example' in line.lower() or '.md' in filepath:
                            continue
                            
                        print(f"⚠️  {filepath}:{line_num}")
                        print(f"   Line: {line.strip()}")
                        issues_found += 1
                        
        except Exception as e:
            continue
    
    print(f"\n📊 Scan Complete:")
    print(f"   Files scanned: {len(all_files)}")
    print(f"   Issues found: {issues_found}")
    
    if issues_found == 0:
        print("✅ No hardcoded credentials found - Security scan PASSED! 🎉")
    else:
        print("❌ Hardcoded credentials still found - Security scan FAILED!")
        
    return issues_found == 0

def verify_environment_variables():
    """Verify that required environment variables are available"""
    
    print("\n🔍 Environment Variables Check")
    print("=" * 50)
    
    required_vars = [
        'ML_DATABASE_URL',
        'SECRET_KEY'
    ]
    
    optional_vars = [
        'DATABASE_URL',
        'RDS_HOST',
        'RDS_USER',
        'RDS_PASSWORD'
    ]
    
    all_good = True
    
    print("Required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"⚪ {var}: not set")
    
    return all_good

if __name__ == "__main__":
    print("🔒 SECURITY VERIFICATION TOOL")
    print("=" * 60)
    
    # Scan for hardcoded credentials
    credentials_secure = scan_for_hardcoded_credentials()
    
    # Check environment variables
    env_vars_ok = verify_environment_variables()
    
    print("\n" + "=" * 60)
    print("🔒 FINAL SECURITY STATUS:")
    
    if credentials_secure and env_vars_ok:
        print("✅ SECURITY CHECK PASSED - Ready for production deployment! 🚀")
    else:
        print("❌ SECURITY CHECK FAILED - Please fix issues before deployment")
        
        if not credentials_secure:
            print("   - Fix hardcoded credentials")
        if not env_vars_ok:
            print("   - Set required environment variables")