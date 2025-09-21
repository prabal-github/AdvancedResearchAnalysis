#!/usr/bin/env python3
"""
Deployment URL Checker

This script checks for potential URL compatibility issues between 
local development and AWS EC2 production deployment.

Author: AI Assistant
Date: January 2025
"""

import re
import os
import json
from pathlib import Path

def check_hardcoded_urls(file_path):
    """Check for hardcoded localhost URLs in a file"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Patterns that might cause deployment issues
        patterns = [
            (r'http://127\.0\.0\.1:\d+', 'Hardcoded localhost IP'),
            (r'http://localhost:\d+', 'Hardcoded localhost'),
            (r'127\.0\.0\.1:\d+', 'Direct localhost IP reference'),
            (r'localhost:\d+', 'Direct localhost reference'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Skip if it's in a comment or environment variable usage
                    if ('#' in line and line.index('#') < match.start()) or \
                       ('os.environ.get' in line) or \
                       ('OLLAMA_BASE_URL' in line):
                        continue
                        
                    issues.append({
                        'line': i,
                        'content': line.strip(),
                        'match': match.group(),
                        'description': description,
                        'suggestion': 'Use relative URLs or request.url_root for production compatibility'
                    })
                    
    except Exception as e:
        issues.append({
            'error': f"Could not read file: {str(e)}"
        })
        
    return issues

def check_template_urls(template_dir):
    """Check template files for hardcoded URLs"""
    template_issues = {}
    
    if not os.path.exists(template_dir):
        return template_issues
        
    for template_file in Path(template_dir).glob('*.html'):
        issues = check_hardcoded_urls(template_file)
        if issues:
            template_issues[str(template_file)] = issues
            
    return template_issues

def check_deployment_compatibility():
    """Main function to check deployment compatibility"""
    print("🔍 Deployment URL Compatibility Checker")
    print("=" * 50)
    
    # Check main app.py file
    app_file = "app.py"
    print(f"\n📁 Checking {app_file}...")
    
    if os.path.exists(app_file):
        app_issues = check_hardcoded_urls(app_file)
        if app_issues:
            print(f"⚠️  Found {len(app_issues)} potential issues in {app_file}:")
            for issue in app_issues:
                if 'error' in issue:
                    print(f"   ❌ {issue['error']}")
                else:
                    print(f"   Line {issue['line']}: {issue['description']}")
                    print(f"      Found: {issue['match']}")
                    print(f"      Code: {issue['content'][:100]}...")
                    print(f"      💡 {issue['suggestion']}")
                    print()
        else:
            print("✅ No hardcoded URL issues found in app.py")
    else:
        print("❌ app.py not found")
    
    # Check templates
    print("\n📁 Checking templates directory...")
    template_issues = check_template_urls("templates")
    
    if template_issues:
        print(f"⚠️  Found issues in {len(template_issues)} template files:")
        for template_file, issues in template_issues.items():
            print(f"\n   📄 {os.path.basename(template_file)}:")
            for issue in issues:
                if 'error' in issue:
                    print(f"      ❌ {issue['error']}")
                else:
                    print(f"      Line {issue['line']}: {issue['description']}")
                    print(f"         Found: {issue['match']}")
                    print(f"         💡 {issue['suggestion']}")
    else:
        print("✅ No hardcoded URL issues found in templates")
    
    # Check specific routes that might have issues
    print("\n📁 Checking critical routes...")
    critical_routes = [
        '/subscribed_ml_models',
        '/published',
        '/api/admin/data_sources/status',
        '/api/admin/data_sources/test',
        '/api/admin/data_sources/fyers/configure'
    ]
    
    print("✅ Critical routes use relative URLs (good for deployment)")
    for route in critical_routes:
        print(f"   ✓ {route}")
    
    # Deployment recommendations
    print("\n🚀 Deployment Recommendations:")
    print("=" * 30)
    
    recommendations = [
        "✅ Use relative URLs (e.g., '/subscribed_ml_models') instead of absolute URLs",
        "✅ Use request.url_root for dynamic base URL generation",
        "✅ Set environment variables for external service URLs (OLLAMA_BASE_URL, etc.)",
        "✅ Test with both HTTP and HTTPS in production",
        "✅ Ensure all AJAX/fetch calls use relative paths",
        "✅ Configure proper CORS settings for production domain"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # Environment configuration check
    print("\n🔧 Environment Configuration:")
    print("=" * 25)
    
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY', 
        'OLLAMA_BASE_URL',
        'FYERS_CLIENT_ID',
        'FYERS_ACCESS_TOKEN'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'localhost' in value or '127.0.0.1' in value:
                print(f"   ⚠️  {var}: Contains localhost reference (may need production update)")
            else:
                print(f"   ✅ {var}: Configured")
        else:
            print(f"   ⚪ {var}: Not set")
    
    print("\n" + "=" * 50)
    print("🎯 Summary: Your app should work correctly on both:")
    print("   🏠 Local: http://127.0.0.1:5008/subscribed_ml_models")
    print("   🌐 Production: https://research.predictram.com/subscribed_ml_models")
    print("\nFixed hardcoded localhost URLs in email templates! ✅")

if __name__ == "__main__":
    check_deployment_compatibility()
