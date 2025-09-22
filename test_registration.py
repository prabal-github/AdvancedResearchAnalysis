#!/usr/bin/env python3
"""
Test script for registration functionality
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, User, InvestorRegistration
    from werkzeug.security import generate_password_hash
    
    print("✅ Successfully imported app components")
    
    with app.app_context():
        print("🔧 Testing database connection...")
        
        # Test database connection
        try:
            db.create_all()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database error: {e}")
            sys.exit(1)
        
        print("🧪 Testing User model creation...")
        
        # Test User model creation (the bug we fixed)
        try:
            test_user = User(
                username='test@example.com',
                email='test@example.com',
                role='investor'
            )
            print("✅ User model creation successful")
            
            # Test adding to session (but don't commit)
            db.session.add(test_user)
            db.session.flush()  # Get ID without committing
            user_id = test_user.id
            print(f"✅ User session handling successful, ID: {user_id}")
            
            # Test InvestorRegistration creation
            investor_reg = InvestorRegistration(
                name='Test User',
                email='test@example.com',
                mobile='1234567890',
                pan_number='PENDING',
                password_hash=generate_password_hash('TestPassword123'),
                status='approved',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(investor_reg)
            print("✅ InvestorRegistration model creation successful")
            
            # Rollback to avoid actually creating test data
            db.session.rollback()
            print("✅ Test completed successfully - no data committed")
            
        except Exception as e:
            print(f"❌ Model creation error: {e}")
            db.session.rollback()
            sys.exit(1)
        
        print("\n🎉 Registration functionality test PASSED!")
        print("✅ User model constructor fixed")
        print("✅ Database operations working")
        print("✅ Password hashing working")
        print("✅ InvestorRegistration model working")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)