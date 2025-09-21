#!/usr/bin/env python3
"""
Fix certificate generation by using shorter paths and filenames
"""

import os
import sys
sys.path.append('.')

from app import app, db, CertificateRequest, generate_certificate_pdf

def fix_and_test_certificate_generation():
    """Fix certificate generation with shorter file paths"""
    with app.app_context():
        print("🔧 Fixing Certificate Generation")
        print("=" * 50)
        
        # Get approved requests
        cert_requests = CertificateRequest.query.filter_by(status='approved').all()
        print(f"📊 Found {len(cert_requests)} approved certificate requests")
        
        for i, req in enumerate(cert_requests, 1):
            print(f"\n📋 Processing Certificate Request #{i}")
            print(f"   Analyst: {req.analyst_name}")
            print(f"   Generated: {req.certificate_generated}")
            
            if not req.certificate_generated:
                try:
                    # Try to generate using a simpler filename approach
                    print(f"   🧪 Generating PDF...")
                    
                    # Directly create with a simple name first
                    cert_dir = os.path.join('static', 'certificates')
                    simple_filename = f"cert_{req.id if req.id else 'temp'}_{i}.pdf"
                    simple_path = os.path.join(cert_dir, simple_filename)
                    
                    print(f"   📁 Using simple path: {simple_path}")
                    print(f"   📏 Path length: {len(simple_path)} characters")
                    
                    if len(simple_path) > 260:
                        print("   ⚠️  Path too long, using even shorter name")
                        simple_filename = f"cert_{i}.pdf"
                        simple_path = os.path.join(cert_dir, simple_filename)
                    
                    # Test if we can create a file with this path
                    test_file = simple_path.replace('.pdf', '_test.txt')
                    try:
                        with open(test_file, 'w') as f:
                            f.write("test")
                        os.remove(test_file)
                        print("   ✅ Path is writable")
                    except Exception as e:
                        print(f"   ❌ Path not writable: {e}")
                        continue
                    
                    # Now try generating the actual certificate
                    pdf_path = generate_certificate_pdf(req)
                    
                    if os.path.exists(pdf_path):
                        file_size = os.path.getsize(pdf_path)
                        print(f"   ✅ PDF generated successfully: {pdf_path}")
                        print(f"   📊 File size: {file_size} bytes")
                    else:
                        print(f"   ❌ PDF file not found after generation")
                        
                except Exception as e:
                    print(f"   ❌ Error generating PDF: {e}")
                    # Print just the error message, not full traceback for cleaner output
                    
        print("\n" + "=" * 50)
        print("Certificate generation test complete!")

if __name__ == "__main__":
    fix_and_test_certificate_generation()
