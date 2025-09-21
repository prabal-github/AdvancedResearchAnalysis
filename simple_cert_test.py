#!/usr/bin/env python3
"""
Simple certificate test with minimal PDF generation
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def create_simple_certificate():
    """Create a simple test certificate"""
    
    # Create certificates directory if it doesn't exist
    cert_dir = os.path.join('static', 'certificates')
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir, exist_ok=True)
    
    # PDF filename
    pdf_filename = "test_certificate.pdf"
    pdf_path = os.path.join(cert_dir, pdf_filename)
    
    print(f"Creating PDF at: {pdf_path}")
    print(f"Directory exists: {os.path.exists(cert_dir)}")
    print(f"Directory writable: {os.access(cert_dir, os.W_OK)}")
    
    try:
        # Create PDF
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
        c.drawCentredString(width / 2, height - 250, "Demo Analyst")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 300, "has successfully completed the Financial Analyst Internship program")
        c.drawString(50, height - 320, "at PredictRAM with a performance score of 85/100.")
        
        # Signatures
        c.drawString(50, height - 400, "Subir Singh")
        c.drawString(50, height - 420, "Director - PredictRAM")
        
        c.drawString(width - 200, height - 400, "Sheetal Maurya")
        c.drawString(width - 200, height - 420, "Assistant Professor")
        
        c.showPage()
        c.save()
        
        print(f"✅ PDF created successfully: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_simple_certificate()
