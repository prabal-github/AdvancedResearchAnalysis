#!/usr/bin/env python3
"""
Create a working certificate using the exact same approach that worked in simple_cert_test.py
"""

import os
import sys
sys.path.append('.')

from app import app, db, CertificateRequest
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import date

def create_working_certificate():
    """Create a certificate using the working approach"""
    
    with app.app_context():
        print("🔧 Creating Working Certificate")
        print("=" * 50)
        
        # Get the first approved request
        cert_request = CertificateRequest.query.filter_by(status='approved').first()
        if not cert_request:
            print("❌ No approved certificate requests found")
            return
        
        print(f"📋 Processing: {cert_request.analyst_name}")
        
        # Use the exact same directory and naming approach that worked
        cert_dir = os.path.join('static', 'certificates')
        
        # Simple, guaranteed unique filename
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        pdf_filename = f"certificate_{timestamp}.pdf"
        pdf_path = os.path.join(cert_dir, pdf_filename)
        
        print(f"📁 Creating: {pdf_path}")
        print(f"📏 Path length: {len(pdf_path)}")
        
        try:
            # Create PDF using exact same approach as simple_cert_test.py
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            
            # Simple border
            c.setStrokeColor(colors.darkblue)
            c.setLineWidth(3)
            c.rect(20, 20, width - 40, height - 40)
            
            # SEBI Registration in top left
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.darkblue)
            c.drawString(30, height - 50, "SEBI Registered Research Analyst")
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.black)
            c.drawString(30, height - 65, "INH000022400")
            
            # Company name
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(width / 2, height - 100, "PredictRAM")
            c.setFont("Helvetica", 12)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, height - 120, "Params Data Provider Pvt Ltd")
            
            # Certificate title
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(width / 2, height - 180, "CERTIFICATE OF INTERNSHIP")
            
            # Content
            c.setFont("Helvetica", 12)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, height - 220, "This certifies that")
            
            c.setFont("Helvetica-Oblique", 20)
            c.drawCentredString(width / 2, height - 250, cert_request.analyst_name)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 300, "has successfully completed the Financial Analyst Internship program")
            c.drawString(50, height - 320, f"at PredictRAM with a performance score of {cert_request.performance_score}/100.")
            
            # Dates
            start_date = cert_request.internship_start_date.strftime('%d-%m-%Y')
            end_date = cert_request.internship_end_date.strftime('%d-%m-%Y')
            c.drawString(50, height - 350, f"Duration: {start_date} to {end_date}")
            
            # Certificate ID
            cert_id = f"PRED-{cert_request.analyst_name[:3].upper()}-{timestamp}"
            c.drawString(50, height - 380, f"Certificate ID: {cert_id}")
            
            # Signatures
            c.drawString(50, height - 450, "Subir Singh")
            c.drawString(50, height - 470, "Director - PredictRAM")
            
            c.drawString(width - 200, height - 450, "Sheetal Maurya")
            c.drawString(width - 200, height - 470, "Assistant Professor")
            
            c.showPage()
            c.save()
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Certificate created successfully!")
                print(f"📊 File size: {file_size} bytes")
                
                # Update the certificate request
                cert_request.certificate_generated = True
                cert_request.certificate_file_path = pdf_path
                cert_request.certificate_unique_id = cert_id
                db.session.commit()
                
                print(f"✅ Database updated")
                return pdf_path
            else:
                print(f"❌ File was not created")
                return None
                
        except Exception as e:
            print(f"❌ Error creating certificate: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    create_working_certificate()
