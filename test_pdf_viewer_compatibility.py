#!/usr/bin/env python3
"""
PDF Viewer Compatibility Test for Image Visibility
"""

import os
import webbrowser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def create_simple_image_test_pdf():
    """Create a simple PDF with images for viewer testing"""
    print("📄 Creating Simple Image Test PDF")
    print("=" * 40)
    
    pdf_path = "simple_image_test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width/2, height - 50, "IMAGE VISIBILITY TEST")
    
    # Instructions
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 80, "If you can see the images below, your PDF viewer supports embedded images")
    
    # Test each image with labels
    test_images = [
        ("Company Logo", "static/images/image.png", 100, height - 150),
        ("Subir Signature", "static/images/SubirSign.png", 100, height - 250), 
        ("Sheetal Signature", "static/images/SheetalSign.png", 350, height - 250),
        ("Achievement Badge", "static/images/pngwing555.png", 100, height - 350),
        ("Footer Image", "static/images/Supported By1.png", 100, height - 450)
    ]
    
    rendered_count = 0
    
    for label, img_path, x, y in test_images:
        # Draw label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y + 60, label + ":")
        
        try:
            if os.path.exists(img_path):
                # Try to draw the image
                if "Footer" in label:
                    c.drawImage(img_path, x, y, 300, 50)  # Smaller footer
                else:
                    c.drawImage(img_path, x, y, 100, 50)   # Standard size
                
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.green)
                c.drawString(x, y - 10, "✓ Image embedded successfully")
                c.setFillColor(colors.black)
                rendered_count += 1
                print(f"   ✅ {label}: Embedded successfully")
            else:
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.red)
                c.drawString(x, y, "✗ Image file not found")
                c.setFillColor(colors.black)
                print(f"   ❌ {label}: File not found")
                
        except Exception as e:
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.red)
            c.drawString(x, y, f"✗ Error: {str(e)[:30]}")
            c.setFillColor(colors.black)
            print(f"   ❌ {label}: Error - {e}")
    
    # Summary
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width/2, 100, f"Images Embedded: {rendered_count}/5")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, 80, "If images don't appear, try a different PDF viewer:")
    c.drawCentredString(width/2, 65, "• Adobe Acrobat Reader")
    c.drawCentredString(width/2, 50, "• Google Chrome browser")
    c.drawCentredString(width/2, 35, "• Microsoft Edge")
    c.drawCentredString(width/2, 20, "• Firefox browser")
    
    c.showPage()
    c.save()
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ Test PDF created: {pdf_path} ({file_size} bytes)")
        return pdf_path
    else:
        print(f"❌ Failed to create test PDF")
        return None

def test_certificate_with_debug_info():
    """Generate a certificate with debug information"""
    print(f"\n📋 Creating Certificate with Debug Info")
    print("=" * 45)
    
    try:
        import sys
        sys.path.append('.')
        from app import app, db, CertificateRequest, generate_certificate_pdf
        from datetime import datetime, date
        
        with app.app_context():
            # Create test certificate
            test_cert = CertificateRequest(
                analyst_name="Debug Test Analyst",
                analyst_email="debug@example.com", 
                internship_start_date=date(2024, 1, 1),
                internship_end_date=date(2024, 6, 30),
                requested_issue_date=date.today(),
                status='approved',
                performance_score=95.0,
                approved_by='Debug Admin',
                approved_at=datetime.now()
            )
            
            db.session.add(test_cert)
            db.session.commit()
            
            print(f"✅ Debug certificate request created")
            
            # Generate certificate
            pdf_path = generate_certificate_pdf(test_cert)
            
            if pdf_path and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Debug certificate: {pdf_path}")
                print(f"   File size: {file_size} bytes")
                
                # Analyze PDF content
                with open(pdf_path, 'rb') as f:
                    content = f.read()
                    
                # Check for image markers
                image_indicators = [
                    (b'/Image', 'Image objects'),
                    (b'/XObject', 'External objects'),
                    (b'/DCTDecode', 'JPEG compression'),
                    (b'/FlateDecode', 'PNG compression'),
                    (b'PNG', 'PNG format')
                ]
                
                print(f"   📊 PDF Analysis:")
                for marker, description in image_indicators:
                    count = content.count(marker)
                    if count > 0:
                        print(f"     ✅ {description}: {count} found")
                    else:
                        print(f"     ⚠️  {description}: Not found")
                
                return pdf_path
            else:
                print(f"❌ Certificate generation failed")
                return None
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def provide_viewer_solutions():
    """Provide solutions for PDF viewer issues"""
    print(f"\n💡 PDF VIEWER TROUBLESHOOTING")
    print("=" * 40)
    print("If images are not visible in the PDF, try these solutions:")
    print()
    print("1. 🌐 Open PDF in different viewers:")
    print("   • Chrome: Drag PDF into browser window")
    print("   • Edge: Right-click PDF → Open with → Microsoft Edge")
    print("   • Adobe Reader: Download and install if not available")
    print("   • Firefox: Drag PDF into Firefox window")
    print()
    print("2. 🔧 Check PDF viewer settings:")
    print("   • Enable image display in viewer preferences")
    print("   • Disable 'fast web view' mode")
    print("   • Enable 'show images' option")
    print()
    print("3. 📱 Try online PDF viewers:")
    print("   • Google Drive PDF viewer")
    print("   • Adobe Online PDF viewer")
    print("   • SmallPDF viewer")
    print()
    print("4. 🖥️ System-specific solutions:")
    print("   • Windows: Try Windows 10/11 built-in PDF viewer")
    print("   • Update your current PDF viewer to latest version")
    print("   • Clear PDF viewer cache/temporary files")

if __name__ == "__main__":
    print("🔍 PDF IMAGE VISIBILITY TROUBLESHOOTING")
    print("=" * 50)
    
    # Create simple test PDF
    test_pdf = create_simple_image_test_pdf()
    
    # Create debug certificate
    debug_cert = test_certificate_with_debug_info()
    
    # Provide solutions
    provide_viewer_solutions()
    
    print(f"\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if test_pdf:
        print(f"✅ Simple test PDF: {test_pdf}")
        print(f"   Use this to verify your PDF viewer can display images")
    
    if debug_cert:
        print(f"✅ Debug certificate: {debug_cert}")
        print(f"   This contains the same images as the main certificates")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Open the test PDFs in different viewers")
    print(f"2. If images show in some viewers but not others, it's a viewer issue")
    print(f"3. If images don't show in any viewer, there may be a generation issue")
    print(f"4. Try the troubleshooting solutions provided above")
    
    # Try to open the test PDF automatically
    if test_pdf:
        try:
            print(f"\n🚀 Attempting to open test PDF in default browser...")
            webbrowser.open(f"file://{os.path.abspath(test_pdf)}")
        except:
            print(f"   Could not auto-open. Please open manually: {test_pdf}")
