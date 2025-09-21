#!/usr/bin/env python3
"""
Debug the certificate request ID issue
"""

import os
import sys
sys.path.append('.')

from app import app, db, CertificateRequest

def debug_certificate_ids():
    """Debug certificate request IDs"""
    with app.app_context():
        print("🔍 Certificate Request ID Debugging")
        print("=" * 50)
        
        cert_requests = CertificateRequest.query.all()
        print(f"📊 Total Certificate Requests: {len(cert_requests)}")
        
        for i, req in enumerate(cert_requests, 1):
            print(f"\n📋 Certificate Request #{i}")
            print(f"   ID: {req.id} (type: {type(req.id)})")
            print(f"   Analyst: {req.analyst_name}")
            print(f"   Status: {req.status}")
            
            # Test certificate ID generation
            if req.id:
                try:
                    cert_id = f"PRED-{req.analyst_name[:3].upper()}-{str(req.id)[:8]}"
                    print(f"   Cert ID: {cert_id}")
                    
                    # Test filename generation
                    safe_analyst_name = req.analyst_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    pdf_filename = f"cert_{cert_id}_{safe_analyst_name[:10]}.pdf"
                    print(f"   Filename: {pdf_filename}")
                    
                    # Test full path
                    cert_dir = os.path.join('static', 'certificates')
                    pdf_path = os.path.join(cert_dir, pdf_filename)
                    print(f"   Full path: {pdf_path}")
                    print(f"   Path length: {len(pdf_path)}")
                    
                    # Check for any problematic characters
                    problematic_chars = ['<', '>', ':', '"', '|', '?', '*']
                    has_problems = any(char in pdf_path for char in problematic_chars)
                    print(f"   Has problematic chars: {has_problems}")
                    
                    # Test if we can create a simple file with this name
                    test_path = pdf_path.replace('.pdf', '_test.txt')
                    try:
                        with open(test_path, 'w') as f:
                            f.write("test")
                        os.remove(test_path)
                        print("   ✅ Path is valid and writable")
                    except Exception as e:
                        print(f"   ❌ Path issue: {e}")
                        
                except Exception as e:
                    print(f"   ❌ Error processing: {e}")
            else:
                print("   ⚠️  ID is None")

if __name__ == "__main__":
    debug_certificate_ids()
