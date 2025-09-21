#!/usr/bin/env python3
"""
Debug Certificate Generation and Download Issues
"""

import os
import sys
sys.path.append('.')

from app import app, db, CertificateRequest
from datetime import datetime, date

def debug_certificate_system():
    """Debug certificate system issues"""
    with app.app_context():
        print("🔍 Certificate System Debugging")
        print("=" * 50)
        
        # Check if ReportLab is available
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            print("✅ ReportLab is available")
        except ImportError as e:
            print(f"❌ ReportLab not available: {e}")
            return
        
        # Check certificate requests
        cert_requests = CertificateRequest.query.all()
        print(f"\n📊 Total Certificate Requests: {len(cert_requests)}")
        
        if not cert_requests:
            print("No certificate requests found. Creating a test request...")
            # Create a test certificate request
            test_request = CertificateRequest(
                analyst_name="Test Analyst",
                internship_start_date=date(2024, 1, 1),
                internship_end_date=date(2024, 6, 30),
                requested_issue_date=date.today(),
                status='approved',
                performance_score=85,
                approved_by='Admin',
                approved_date=datetime.now()
            )
            db.session.add(test_request)
            db.session.commit()
            cert_requests = [test_request]
            print("✅ Test certificate request created")
        
        # Check each request
        for i, req in enumerate(cert_requests, 1):
            print(f"\n📋 Certificate Request #{i}")
            print(f"   Analyst: {req.analyst_name}")
            print(f"   Status: {req.status}")
            print(f"   Generated: {req.certificate_generated}")
            print(f"   File Path: {req.certificate_file_path}")
            print(f"   Unique ID: {req.certificate_unique_id}")
            
            if req.status == 'approved':
                print(f"   Performance Score: {req.performance_score}")
                
                # Check if certificate file exists
                if req.certificate_file_path:
                    if os.path.exists(req.certificate_file_path):
                        file_size = os.path.getsize(req.certificate_file_path)
                        print(f"   ✅ Certificate file exists ({file_size} bytes)")
                    else:
                        print(f"   ❌ Certificate file missing: {req.certificate_file_path}")
                else:
                    print("   ⚠️  No certificate file path set")
        
        # Check certificates directory
        cert_dir = os.path.join('static', 'certificates')
        print(f"\n📁 Certificate Directory: {cert_dir}")
        print(f"   Exists: {os.path.exists(cert_dir)}")
        
        if os.path.exists(cert_dir):
            files = os.listdir(cert_dir)
            print(f"   Files: {len(files)}")
            for file in files:
                file_path = os.path.join(cert_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"     - {file} ({file_size} bytes)")
        
        # Test PDF generation for approved requests
        approved_requests = [req for req in cert_requests if req.status == 'approved' and not req.certificate_generated]
        if approved_requests:
            print(f"\n🧪 Testing PDF generation for {len(approved_requests)} approved requests...")
            
            from app import generate_certificate_pdf
            
            for req in approved_requests:
                try:
                    print(f"\n   Generating PDF for {req.analyst_name}...")
                    pdf_path = generate_certificate_pdf(req)
                    print(f"   ✅ PDF generated: {pdf_path}")
                    
                    if os.path.exists(pdf_path):
                        file_size = os.path.getsize(pdf_path)
                        print(f"   ✅ File verified ({file_size} bytes)")
                    else:
                        print(f"   ❌ Generated file not found: {pdf_path}")
                        
                except Exception as e:
                    print(f"   ❌ Error generating PDF: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Check required images
        print(f"\n🖼️  Checking Required Images:")
        image_paths = [
            'static/images/image.png',
            'static/images/pngwing555.png', 
            'static/images/signature1.png',
            'static/images/signature2.png',
            'static/images/Supported By1.png'
        ]
        
        for img_path in image_paths:
            exists = os.path.exists(img_path)
            print(f"   {img_path}: {'✅' if exists else '❌'}")
        
        print("\n" + "=" * 50)
        print("Debug Complete!")

if __name__ == "__main__":
    debug_certificate_system()
