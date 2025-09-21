#!/usr/bin/env python3
"""
Comprehensive Certificate Image Visibility Diagnosis
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from PIL import Image

def test_image_files():
    """Test if image files are valid and can be opened"""
    print("🔍 Testing Image File Validity")
    print("=" * 40)
    
    image_files = [
        'static/images/image.png',
        'static/images/SubirSign.png',
        'static/images/SheetalSign.png', 
        'static/images/pngwing555.png',
        'static/images/Supported By1.png'
    ]
    
    valid_images = []
    
    for img_path in image_files:
        print(f"\n📸 Testing: {img_path}")
        
        if not os.path.exists(img_path):
            print(f"   ❌ File not found")
            continue
            
        file_size = os.path.getsize(img_path)
        print(f"   📏 Size: {file_size} bytes")
        
        try:
            # Test with PIL
            with Image.open(img_path) as img:
                print(f"   🎨 Format: {img.format}")
                print(f"   📐 Size: {img.size}")
                print(f"   🌈 Mode: {img.mode}")
                print(f"   ✅ PIL can read the image")
                valid_images.append(img_path)
        except Exception as e:
            print(f"   ❌ PIL error: {e}")
            
            # Try to read as binary
            try:
                with open(img_path, 'rb') as f:
                    header = f.read(10)
                    print(f"   📄 File header: {header}")
                    if header.startswith(b'\x89PNG'):
                        print(f"   ⚠️  PNG header detected but PIL can't read")
                    else:
                        print(f"   ❌ Not a valid PNG file")
            except Exception as e2:
                print(f"   ❌ Cannot read file: {e2}")
    
    return valid_images

def test_reportlab_image_loading():
    """Test ReportLab's ability to load and render images"""
    print(f"\n🧪 Testing ReportLab Image Loading")
    print("=" * 40)
    
    # Create test PDF
    test_pdf = "image_visibility_test.pdf"
    c = canvas.Canvas(test_pdf, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "Image Visibility Test")
    
    # Test each image
    images_to_test = [
        ('Company Logo', 'static/images/image.png', (50, height - 150)),
        ('Subir Signature', 'static/images/SubirSign.png', (50, height - 250)),
        ('Sheetal Signature', 'static/images/SheetalSign.png', (300, height - 250)),
        ('Achievement Badge', 'static/images/pngwing555.png', (50, height - 350)),
        ('Footer Image', 'static/images/Supported By1.png', (50, height - 450))
    ]
    
    y_pos = height - 100
    successful_renders = 0
    
    for name, path, position in images_to_test:
        print(f"\n🖼️  Testing {name}: {path}")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, y_pos, f"{name}:")
        
        try:
            # Test if file exists and is readable
            if not os.path.exists(path):
                print(f"   ❌ File not found")
                c.setFillColor(colors.red)
                c.drawString(200, y_pos, "FILE NOT FOUND")
                c.setFillColor(colors.black)
            else:
                # Try to draw the image
                c.drawImage(path, position[0], position[1], 100, 50)
                print(f"   ✅ Successfully rendered")
                c.setFillColor(colors.green)
                c.drawString(200, y_pos, "SUCCESS")
                c.setFillColor(colors.black)
                successful_renders += 1
                
        except Exception as e:
            print(f"   ❌ ReportLab error: {e}")
            c.setFillColor(colors.red)
            c.drawString(200, y_pos, f"ERROR: {str(e)[:30]}")
            c.setFillColor(colors.black)
        
        y_pos -= 20
    
    c.showPage()
    c.save()
    
    if os.path.exists(test_pdf):
        file_size = os.path.getsize(test_pdf)
        print(f"\n✅ Test PDF created: {test_pdf} ({file_size} bytes)")
        print(f"📊 Success rate: {successful_renders}/{len(images_to_test)} images")
        return test_pdf
    else:
        print(f"\n❌ Failed to create test PDF")
        return None

def test_certificate_generation():
    """Test actual certificate generation with current images"""
    print(f"\n📄 Testing Actual Certificate Generation")
    print("=" * 45)
    
    try:
        # Import the app and test certificate generation
        import sys
        sys.path.append('.')
        from app import app, db, CertificateRequest, generate_certificate_pdf
        from datetime import datetime, date
        
        with app.app_context():
            # Create a test certificate request
            test_cert = CertificateRequest(
                analyst_name="Image Test Analyst",
                analyst_email="test@example.com",
                internship_start_date=date(2024, 1, 1),
                internship_end_date=date(2024, 6, 30),
                requested_issue_date=date.today(),
                status='approved',
                performance_score=88.5,
                approved_by='Test Admin',
                approved_at=datetime.now()
            )
            
            db.session.add(test_cert)
            db.session.commit()
            
            print(f"✅ Test certificate request created")
            print(f"   Analyst: {test_cert.analyst_name}")
            print(f"   Performance: {test_cert.performance_score}/100")
            
            # Generate the certificate
            pdf_path = generate_certificate_pdf(test_cert)
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Certificate generated: {pdf_path}")
                print(f"   File size: {file_size} bytes")
                
                # Check if PDF contains image data
                with open(pdf_path, 'rb') as f:
                    content = f.read(1000)
                    if b'/Image' in content or b'/XObject' in content:
                        print(f"   ✅ PDF contains image objects")
                    else:
                        print(f"   ⚠️  PDF may not contain embedded images")
                        
                return pdf_path
            else:
                print(f"❌ Certificate file not found")
                return None
                
    except Exception as e:
        print(f"❌ Error in certificate generation: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_app_image_paths():
    """Check the image paths in the app.py certificate function"""
    print(f"\n🔧 Checking Image Paths in Certificate Function")
    print("=" * 50)
    
    try:
        # Read the generate_certificate_pdf function
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find image-related lines
        lines = content.split('\n')
        image_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'drawImage' in line or 'static/images' in line or '.png' in line:
                if 'def ' not in line and 'import' not in line:
                    image_lines.append((i, line.strip()))
        
        print(f"Found {len(image_lines)} image-related lines:")
        for line_num, line in image_lines:
            print(f"   Line {line_num}: {line}")
            
        return image_lines
        
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return []

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE IMAGE VISIBILITY DIAGNOSIS")
    print("=" * 60)
    
    # Step 1: Test image files
    valid_images = test_image_files()
    print(f"\n📊 Valid images found: {len(valid_images)}")
    
    # Step 2: Test ReportLab rendering
    test_pdf = test_reportlab_image_loading()
    
    # Step 3: Check app.py image paths
    image_lines = check_app_image_paths()
    
    # Step 4: Test actual certificate generation
    cert_pdf = test_certificate_generation()
    
    print(f"\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"✅ Valid image files: {len(valid_images)}/5")
    if test_pdf:
        print(f"✅ ReportLab test PDF: {test_pdf}")
    if cert_pdf:
        print(f"✅ Certificate PDF: {cert_pdf}")
    print(f"📝 Image references in code: {len(image_lines)} found")
    
    if len(valid_images) == 5 and test_pdf and cert_pdf:
        print(f"\n🎉 All tests passed! Images should be visible.")
    else:
        print(f"\n⚠️  Issues detected. Check the individual test results above.")
        print(f"💡 Next steps:")
        if len(valid_images) < 5:
            print(f"   - Fix invalid image files")
        if not test_pdf:
            print(f"   - ReportLab image loading issues")
        if not cert_pdf:
            print(f"   - Certificate generation problems")
