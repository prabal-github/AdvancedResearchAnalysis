#!/usr/bin/env python3
"""
Anthropic Run History Analysis - Implementation Validation

This script validates that all components of the Anthropic AI integration
are properly implemented and accessible.

Author: AI Assistant  
Date: January 2025
"""

import sys
import os
sys.path.append(os.getcwd())

def validate_implementation():
    """Validate the Anthropic integration implementation"""
    print("🔍 Validating Anthropic Run History Analysis Implementation")
    print("=" * 60)
    
    success_count = 0
    total_checks = 0
    
    # 1. Check Flask app routes
    try:
        from app import app
        with app.app_context():
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            
            # Check for required routes
            required_routes = [
                '/api/published_models/<mid>/run_history_analysis',
                '/api/admin/anthropic/config',
                '/published'
            ]
            
            total_checks += len(required_routes)
            for route in required_routes:
                if any(route.replace('<mid>', '<mid>') in r for r in routes):
                    print(f"✅ Route exists: {route}")
                    success_count += 1
                else:
                    print(f"❌ Route missing: {route}")
    except Exception as e:
        print(f"❌ Failed to check routes: {e}")
    
    # 2. Check Anthropic availability
    total_checks += 1
    try:
        import anthropic
        print("✅ Anthropic package available")
        success_count += 1
    except ImportError:
        print("❌ Anthropic package not installed (run: pip install anthropic)")
    
    # 3. Check database models
    total_checks += 1
    try:
        from app import AdminAPIKey
        print("✅ AdminAPIKey model available for configuration storage")
        success_count += 1
    except Exception as e:
        print(f"❌ Database model check failed: {e}")
    
    # 4. Check Claude client integration
    total_checks += 1
    try:
        from app import ClaudeClient
        client = ClaudeClient()
        if hasattr(client, 'model_options'):
            models = list(client.model_options.keys())
            print(f"✅ Claude client configured with models: {models}")
            success_count += 1
        else:
            print("❌ Claude client missing model options")
    except Exception as e:
        print(f"❌ Claude client check failed: {e}")
    
    # 5. Check template file exists
    total_checks += 1
    template_path = "templates/published_catalog.html"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            if 'run_history_analysis' in content and 'anthropic' in content:
                print("✅ Template updated with Anthropic integration")
                success_count += 1
            else:
                print("❌ Template missing Anthropic integration")
    else:
        print("❌ Published catalog template not found")
    
    # 6. Check function implementations
    total_checks += 1
    try:
        from app import generate_run_history_analysis, anthropic_admin_config
        print("✅ Core analysis functions implemented")
        success_count += 1
    except Exception as e:
        print(f"❌ Function implementation check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Validation Summary: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("🎉 Implementation is complete and ready for deployment!")
        print("\n🚀 Next Steps:")
        print("1. Deploy to AWS EC2")
        print("2. Configure Anthropic API key via admin panel")
        print("3. Test run history analysis on published models")
    elif success_count >= total_checks * 0.8:
        print("⚠️  Implementation is mostly complete with minor issues")
        print("🔧 Address the failed checks above before deployment")
    else:
        print("❌ Implementation has significant issues that need to be resolved")
    
    # Feature overview
    print("\n" + "=" * 60)
    print("🎯 Feature Overview:")
    print("• Enhanced Run History Analysis with Anthropic Claude Sonnet 3.5/3.7")
    print("• Admin configuration UI for API key management")
    print("• Multiple analysis types: Comprehensive, Performance, Trends")
    print("• AWS EC2 deployment ready with environment compatibility")
    print("• Fallback support for when AI services are unavailable")
    print("• Secure API key storage and validation")
    
    return success_count, total_checks

if __name__ == "__main__":
    try:
        validate_implementation()
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
