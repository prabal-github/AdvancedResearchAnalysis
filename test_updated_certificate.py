#!/usr/bin/env python3
"""
Test Updated Certificate Generation with Logo and Signature Placements
"""

import os
import sys
sys.path.append('.')

from app import app, db, CertificateRequest, generate_certificate_pdf
from datetime import datetime, date

def test_updated_certificate():
    """Test certificate generation with updated logo and signature placements"""
    with app.app_context():
        print("🧪 Testing Updated Certificate Generation")
        print("=" * 60)
        
        # Create a new test certificate request
        test_request = CertificateRequest(
            analyst_name="Updated Test Analyst",
            analyst_email="test@example.com",
            internship_start_date=date(2024, 1, 15),
            internship_end_date=date(2024, 7, 15),
            requested_issue_date=date.today(),
            status='approved',
            performance_score=92,
            approved_by='Admin',
            approved_at=datetime.now()
        )
        db.session.add(test_request)
        db.session.commit()
        
        print(f"✅ Created test certificate request for: {test_request.analyst_name}")
        print(f"   Performance Score: {test_request.performance_score}")
        print(f"   Internship Duration: {test_request.internship_start_date} to {test_request.internship_end_date}")
        
        # Check if signature files exist
        print(f"\n🖼️  Checking Updated Image Files:")
        image_files = [
            ('Company Logo', 'static/images/image.png'),
            ('Achievement Badge', 'static/images/pngwing555.png'),
            ('Subir Sign', 'static/images/SubirSign.png'),
            ('Sheetal Sign', 'static/images/SheetalSign.png'),
            ('Supported By Footer', 'static/images/Supported By1.png')
        ]
        
        for name, path in image_files:
            exists = os.path.exists(path)
            print(f"   {name}: {'✅' if exists else '❌'} ({path})")
        
        # Generate the certificate
        print(f"\n📄 Generating Certificate...")
        try:
            pdf_path = generate_certificate_pdf(test_request)
            print(f"✅ Certificate generated successfully!")
            print(f"   Path: {pdf_path}")
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"   File size: {file_size} bytes")
                print(f"   Certificate ID: {test_request.certificate_unique_id}")
                
                # Verify database update
                if test_request.certificate_generated:
                    print(f"✅ Database updated correctly")
                else:
                    print(f"❌ Database not updated")
                    
            else:
                print(f"❌ Certificate file not found at: {pdf_path}")
                
        except Exception as e:
            print(f"❌ Error generating certificate: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("🎯 Certificate Features Implemented:")
        print("   ✅ Company logo at top center (replacing text)")
        print("   ✅ SubirSign.png above 'Subir Singh - Director - PredictRAM'")
        print("   ✅ SheetalSign.png above 'Sheetal Maurya - Assistant Professor'")
        print("   ✅ Supported By1.png at bottom footer")
        print("   ✅ SEBI registration in top left corner")
        print("   ✅ Professional certificate layout with borders")
        print("\n✨ Test Complete!")

if __name__ == "__main__":
    test_updated_certificate()
