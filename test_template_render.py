#!/usr/bin/env python3
"""
Simple Template Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from flask import render_template

def test_template():
    """Test rendering the template with actual data"""
    with app.test_request_context():
        try:
            # Create a mock profile object
            class MockProfile:
                def __init__(self):
                    self.name = "Test Analyst"
                    self.full_name = "Test Analyst Full Name"
                    self.email = "test@example.com"
                    self.phone = "123-456-7890"
                    self.date_of_birth = None
                    self.brief_description = ""
                    self.profile_image = ""
                    self.certification = ""
                    self.experience_years = 0
                    self.sebi_registration = ""
            
            profile = MockProfile()
            
            # Try to render the template
            result = render_template('edit_analyst_profile.html', profile=profile)
            print("✅ Template rendered successfully!")
            print(f"📄 Content length: {len(result)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🧪 TEMPLATE RENDERING TEST")
    print("=" * 50)
    success = test_template()
    sys.exit(0 if success else 1)
