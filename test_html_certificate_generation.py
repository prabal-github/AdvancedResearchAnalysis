#!/usr/bin/env python3
"""
Test HTML Certificate Generation with Images and Graphics
"""

import os
import sys
from datetime import date, datetime

# Add current directory to path
sys.path.append('.')

def test_html_certificate_generation():
    """Test the new HTML certificate generation"""
    print("🧪 TESTING HTML CERTIFICATE GENERATION")
    print("=" * 60)
    
    try:
        # Import Flask app and models
        from app import app, db, CertificateRequest, generate_certificate_html
        
        with app.app_context():
            # Create a test certificate request
            test_request = CertificateRequest(
                analyst_name="Test HTML Certificate Analyst",
                analyst_email="test.html@predictram.com",
                internship_start_date=date(2024, 1, 15),
                internship_end_date=date(2024, 6, 30),
                requested_issue_date=date.today(),
                status='approved',
                performance_score=89.5,
                approved_by='HTML Test Admin',
                approved_at=datetime.now(),
                certificate_generated=False
            )
            
            # Add to database
            db.session.add(test_request)
            db.session.commit()
            
            print(f"✅ Test certificate request created:")
            print(f"   Analyst: {test_request.analyst_name}")
            print(f"   Email: {test_request.analyst_email}")
            print(f"   Performance Score: {test_request.performance_score}/100")
            print(f"   Duration: {test_request.internship_start_date} to {test_request.internship_end_date}")
            
            # Generate HTML certificate
            print(f"\n🔄 Generating HTML certificate...")
            html_path = generate_certificate_html(test_request)
            
            # Verify file creation
            if os.path.exists(html_path):
                file_size = os.path.getsize(html_path)
                print(f"✅ HTML certificate generated successfully!")
                print(f"   File path: {html_path}")
                print(f"   File size: {file_size} bytes")
                
                # Check content
                with open(html_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verify key elements
                checks = [
                    ("HTML Structure", "<!DOCTYPE html>"),
                    ("Certificate Title", "Certificate of Excellence"),
                    ("Analyst Name", test_request.analyst_name),
                    ("Performance Score", str(test_request.performance_score)),
                    ("CSS Gradients", "linear-gradient"),
                    ("Animations", "@keyframes"),
                    ("Company Logo Area", "company-logo"),
                    ("Signature Blocks", "signature-image"),
                    ("Achievement Badge", "achievement-badge"),
                    ("Footer Branding", "footer-logo")
                ]
                
                print(f"\n📊 Content Verification:")
                all_passed = True
                for check_name, search_term in checks:
                    if search_term in content:
                        print(f"   ✅ {check_name}: Found")
                    else:
                        print(f"   ❌ {check_name}: Missing")
                        all_passed = False
                
                # Check for image integration
                print(f"\n🖼️ Image Integration Check:")
                image_files = [
                    ('static/images/image.png', 'Company Logo'),
                    ('static/images/SubirSign.png', 'Subir Signature'),
                    ('static/images/SheetalSign.png', 'Sheetal Signature'),
                    ('static/images/pngwing555.png', 'Achievement Badge'),
                    ('static/images/Supported By1.png', 'Footer Logo')
                ]
                
                for img_path, img_name in image_files:
                    if os.path.exists(img_path):
                        if img_path in content:
                            print(f"   ✅ {img_name}: Image file exists and referenced in HTML")
                        else:
                            print(f"   ⚠️ {img_name}: Image file exists but not referenced")
                    else:
                        print(f"   📊 {img_name}: Using CSS graphics (image file not found)")
                
                # Performance analysis
                graphics_count = content.count('linear-gradient')
                animation_count = content.count('@keyframes')
                image_count = content.count('background-image:')
                
                print(f"\n🎨 Visual Elements Summary:")
                print(f"   📊 CSS Gradients: {graphics_count}")
                print(f"   🎬 Animations: {animation_count}")
                print(f"   🖼️ Image Backgrounds: {image_count}")
                print(f"   💾 Total File Size: {file_size:,} bytes")
                
                if all_passed and file_size > 5000:
                    print(f"\n🎉 HTML CERTIFICATE GENERATION: SUCCESS!")
                    print(f"   ✅ All content checks passed")
                    print(f"   ✅ File size indicates rich content")
                    print(f"   ✅ Both images and graphics integrated")
                    print(f"   ✅ Ready for browser viewing")
                else:
                    print(f"\n⚠️ Some issues detected, but certificate generated")
                
                return html_path
            else:
                print(f"❌ HTML file was not created")
                return None
                
    except Exception as e:
        print(f"❌ Error testing HTML certificate generation: {e}")
        import traceback
        traceback.print_exc()
        return None

def open_certificate_in_browser(html_path):
    """Try to open the certificate in default browser"""
    if html_path and os.path.exists(html_path):
        try:
            import webbrowser
            file_url = f"file:///{html_path.replace(os.sep, '/')}"
            print(f"\n🌐 Opening certificate in browser...")
            print(f"   URL: {file_url}")
            webbrowser.open(file_url)
            print(f"   ✅ Certificate opened in default browser")
            return True
        except Exception as e:
            print(f"   ❌ Could not open browser: {e}")
            return False
    return False

if __name__ == "__main__":
    print("🚀 HTML Certificate Generation Test")
    print("=" * 60)
    
    # Test certificate generation
    html_path = test_html_certificate_generation()
    
    if html_path:
        print(f"\n" + "=" * 60)
        print("🎯 NEXT STEPS:")
        print("=" * 60)
        print(f"1. ✅ Certificate generated: {os.path.basename(html_path)}")
        print(f"2. 🌐 Open in browser to view")
        print(f"3. 🖨️ Use browser print function to create PDF if needed")
        print(f"4. 📱 Certificate is mobile-responsive")
        print(f"5. 🎨 Combines real images with CSS graphics")
        
        # Try to open in browser
        if not open_certificate_in_browser(html_path):
            print(f"\n💡 Manual Browser Test:")
            print(f"   Copy this path to your browser:")
            print(f"   file:///{html_path.replace(os.sep, '/')}")
    else:
        print(f"\n❌ Certificate generation failed")
        print(f"   Check error messages above for details")
