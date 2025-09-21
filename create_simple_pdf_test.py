#!/usr/bin/env python3
"""
Create a Simple, Clear PDF Test with Visible Images and Text
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
import traceback

def create_basic_text_pdf():
    """Create a basic PDF with just text to test PDF viewer"""
    print("📄 Creating basic text-only PDF...")
    
    pdf_path = "basic_text_test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.blue)
    c.drawCentredString(width/2, height - 80, "BASIC PDF VIEWER TEST")
    
    # Instructions
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    
    text_lines = [
        "This is a simple text-only PDF to test your PDF viewer.",
        "",
        "If you can see this text clearly, your PDF viewer works for text.",
        "",
        "🔍 Check the following:",
        "   ✓ Can you see this text?",
        "   ✓ Are the colors correct? (Blue title, black text)",
        "   ✓ Is the formatting preserved?",
        "",
        "If YES to all above, the issue is specifically with images,",
        "not with PDF generation or viewing in general.",
        "",
        "Next step: Test the image PDF below."
    ]
    
    y_pos = height - 150
    for line in text_lines:
        c.drawString(50, y_pos, line)
        y_pos -= 20
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawString(50, 50, f"Generated on: {os.getcwd()}")
    c.drawString(50, 30, "If you can read this, basic PDF viewing works!")
    
    c.save()
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def create_detailed_image_test():
    """Create a detailed image test with multiple approaches"""
    print("🖼️ Creating detailed image test PDF...")
    
    pdf_path = "detailed_image_test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.red)
    c.drawCentredString(width/2, height - 50, "IMAGE VISIBILITY TEST")
    
    # Test each image individually
    images_to_test = [
        'static/images/image.png',
        'static/images/SubirSign.png',
        'static/images/SheetalSign.png',
        'static/images/pngwing555.png',
        'static/images/Supported By1.png'
    ]
    
    y_start = height - 100
    
    for i, img_path in enumerate(images_to_test):
        y_pos = y_start - (i * 120)
        
        # Image label
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(50, y_pos, f"Image {i+1}: {os.path.basename(img_path)}")
        
        # Image details
        c.setFont("Helvetica", 10)
        try:
            if os.path.exists(img_path):
                file_size = os.path.getsize(img_path)
                c.setFillColor(colors.green)
                c.drawString(50, y_pos - 15, f"✓ File exists ({file_size} bytes)")
                
                # Try to get image info
                try:
                    with Image.open(img_path) as pil_img:
                        c.drawString(50, y_pos - 30, f"✓ Format: {pil_img.format}, Size: {pil_img.size}, Mode: {pil_img.mode}")
                        
                        # Try to draw the image
                        try:
                            c.drawImage(img_path, 300, y_pos - 80, width=150, height=60, preserveAspectRatio=True)
                            c.setFillColor(colors.green)
                            c.drawString(50, y_pos - 45, f"✓ Image drawn successfully")
                        except Exception as draw_error:
                            c.setFillColor(colors.red)
                            c.drawString(50, y_pos - 45, f"✗ Draw error: {str(draw_error)[:50]}")
                            
                except Exception as pil_error:
                    c.setFillColor(colors.orange)
                    c.drawString(50, y_pos - 30, f"⚠ PIL error: {str(pil_error)[:50]}")
            else:
                c.setFillColor(colors.red)
                c.drawString(50, y_pos - 15, f"✗ File not found")
                
        except Exception as e:
            c.setFillColor(colors.red)
            c.drawString(50, y_pos - 15, f"✗ Error: {str(e)[:50]}")
    
    # Instructions at bottom
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.blue)
    bottom_text = [
        "INSTRUCTIONS:",
        "1. If you see colored rectangles/images on the right side → Images work!",
        "2. If you only see text but no images → Image display issue",
        "3. Check each ✓/✗ status to identify specific problems"
    ]
    
    for i, line in enumerate(bottom_text):
        c.drawString(50, 80 - (i * 15), line)
    
    c.save()
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def create_simple_colored_shapes():
    """Create PDF with simple colored shapes instead of images"""
    print("🎨 Creating colored shapes test...")
    
    pdf_path = "colored_shapes_test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "COLORED SHAPES TEST")
    
    # Draw various shapes
    shapes = [
        ("Red Rectangle", colors.red, (100, height-150, 150, 50)),
        ("Blue Circle", colors.blue, (300, height-150, 50, 50)),
        ("Green Triangle", colors.green, (450, height-150, 60, 50)),
        ("Orange Square", colors.orange, (100, height-250, 80, 80)),
        ("Purple Oval", colors.purple, (250, height-250, 120, 60))
    ]
    
    c.setFont("Helvetica", 10)
    
    for name, color, (x, y, w, h) in shapes:
        # Draw shape
        c.setFillColor(color)
        c.rect(x, y, w, h, fill=1, stroke=0)
        
        # Label
        c.setFillColor(colors.black)
        c.drawString(x, y - 20, name)
    
    # Instructions
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    instructions = [
        "If you can see colored shapes above:",
        "✓ Your PDF viewer supports basic graphics",
        "✓ Colors and positioning work correctly",
        "",
        "If shapes are missing or wrong colors:",
        "✗ PDF viewer has rendering issues"
    ]
    
    y_pos = height - 350
    for line in instructions:
        c.drawString(100, y_pos, line)
        y_pos -= 20
    
    c.save()
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def test_actual_certificate_images():
    """Test the actual certificate generation with current setup"""
    print("📋 Testing actual certificate with images...")
    
    try:
        # Import certificate function
        import sys
        sys.path.append('.')
        from app import generate_certificate_pdf, app, db, CertificateRequest
        from datetime import date, datetime
        
        with app.app_context():
            # Create test certificate
            test_cert = CertificateRequest(
                analyst_name="TEST IMAGE ANALYST",
                analyst_email="test@imagetest.com",
                internship_start_date=date(2024, 1, 1),
                internship_end_date=date(2024, 6, 30),
                requested_issue_date=date.today(),
                status='approved',
                performance_score=95.0,
                approved_by='Image Test Admin',
                approved_at=datetime.now()
            )
            
            db.session.add(test_cert)
            db.session.commit()
            
            print(f"✅ Test certificate created: {test_cert.analyst_name}")
            
            # Generate certificate
            cert_path = generate_certificate_pdf(test_cert)
            
            if os.path.exists(cert_path):
                file_size = os.path.getsize(cert_path)
                print(f"✅ Certificate PDF generated: {cert_path}")
                print(f"   File size: {file_size} bytes")
                
                # Analyze PDF content
                with open(cert_path, 'rb') as f:
                    content = f.read()
                    
                # Count image objects
                image_count = content.count(b'/Image')
                xobject_count = content.count(b'/XObject')
                png_count = content.count(b'PNG')
                
                print(f"   📊 PDF Analysis:")
                print(f"      Image objects: {image_count}")
                print(f"      XObjects: {xobject_count}")
                print(f"      PNG references: {png_count}")
                
                if file_size > 5000 and image_count > 0:
                    print(f"   ✅ Certificate appears to have embedded images")
                else:
                    print(f"   ⚠️ Certificate may not have images embedded properly")
                
                return cert_path
            else:
                print(f"❌ Certificate file not created")
                return None
                
    except Exception as e:
        print(f"❌ Error creating certificate: {e}")
        traceback.print_exc()
        return None

def main():
    print("🧪 COMPREHENSIVE PDF VISIBILITY TESTING")
    print("=" * 60)
    
    # Test 1: Basic text PDF
    print("\n📋 TEST 1: Basic Text PDF")
    basic_pdf = create_basic_text_pdf()
    
    # Test 2: Colored shapes
    print("\n📋 TEST 2: Colored Shapes PDF")
    shapes_pdf = create_simple_colored_shapes()
    
    # Test 3: Detailed image test
    print("\n📋 TEST 3: Detailed Image Test PDF")
    image_pdf = create_detailed_image_test()
    
    # Test 4: Actual certificate
    print("\n📋 TEST 4: Actual Certificate PDF")
    cert_pdf = test_actual_certificate_images()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_files = [
        ("Basic Text PDF", basic_pdf),
        ("Colored Shapes PDF", shapes_pdf),
        ("Image Test PDF", image_pdf),
        ("Certificate PDF", cert_pdf)
    ]
    
    for name, path in test_files:
        if path and os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} ({size} bytes)")
        else:
            print(f"❌ {name}: Failed to create")
    
    print(f"\n💡 TESTING INSTRUCTIONS:")
    print(f"1. Open each PDF file in your PDF viewer")
    print(f"2. Check basic_text_test.pdf first - can you see text?")
    print(f"3. Check colored_shapes_test.pdf - can you see colored rectangles?")
    print(f"4. Check detailed_image_test.pdf - can you see actual images?")
    print(f"5. Check the certificate PDF - are images visible?")
    print(f"\n🔍 If text works but images don't, it's a viewer compatibility issue.")
    print(f"🔍 Try opening PDFs in: Chrome browser, Edge, Adobe Reader")

if __name__ == "__main__":
    main()
