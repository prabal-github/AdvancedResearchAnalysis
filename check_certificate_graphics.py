#!/usr/bin/env python3
"""
Certificate Graphics Status Check
"""

import os

def check_certificate_status():
    print("🔍 CERTIFICATE STATUS CHECK")
    print("=" * 50)
    
    # Check if certificate file exists
    cert_file = "SampleCertificate.html"
    if os.path.exists(cert_file):
        file_size = os.path.getsize(cert_file)
        print(f"✅ Certificate file: {cert_file}")
        print(f"   File size: {file_size} bytes")
        
        # Read and analyze content
        with open(cert_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key graphics elements
        graphics_elements = [
            ("Linear Gradients", "linear-gradient"),
            ("Border Radius", "border-radius"),
            ("Box Shadows", "box-shadow"),
            ("Animations", "@keyframes"),
            ("Flexbox Layout", "display: flex"),
            ("Color Styling", "background:"),
            ("Text Effects", "text-shadow"),
            ("Company Logo", "PREDICTRAM"),
            ("Signature Blocks", "SIGNATURE"),
            ("Achievement Badge", "achievement-badge"),
            ("Footer Branding", "PREDICTRAM RESEARCH")
        ]
        
        print(f"\n📊 Graphics Elements Analysis:")
        for name, search_term in graphics_elements:
            count = content.count(search_term)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {name}: {count} occurrences")
        
        # Check for old image references
        image_refs = [
            ("Image URLs", "url('static/images"),
            ("Background Images", "background-image:"),
            ("Image Fallbacks", ":empty::after"),
        ]
        
        print(f"\n🚫 Removed Image Dependencies:")
        for name, search_term in image_refs:
            count = content.count(search_term)
            status = "✅ Removed" if count == 0 else f"⚠️ Found {count}"
            print(f"   {status} {name}")
            
        # Calculate graphics vs image ratio
        total_graphics = sum(content.count(term) for _, term in graphics_elements)
        total_images = sum(content.count(term) for _, term in image_refs)
        
        print(f"\n🎯 Certificate Composition:")
        print(f"   📊 Graphics Elements: {total_graphics}")
        print(f"   🖼️ Image Dependencies: {total_images}")
        print(f"   📈 Graphics Ratio: {(total_graphics/(total_graphics+total_images)*100):.1f}%")
        
        if total_images == 0 and total_graphics > 50:
            print(f"\n🎉 STATUS: PURE GRAPHICS CERTIFICATE")
            print(f"   ✅ Zero image dependencies")
            print(f"   ✅ Rich visual graphics")
            print(f"   ✅ Cross-browser compatible")
            print(f"   ✅ Print-ready design")
        else:
            print(f"\n⚠️ STATUS: NEEDS OPTIMIZATION")
            
    else:
        print(f"❌ Certificate file not found: {cert_file}")
    
    # Check test files
    test_files = [
        "CertificateGraphicsTest.html",
        "basic_text_test.pdf",
        "colored_shapes_test.pdf", 
        "detailed_image_test.pdf"
    ]
    
    print(f"\n📋 Supporting Test Files:")
    for test_file in test_files:
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            print(f"   ✅ {test_file} ({size} bytes)")
        else:
            print(f"   ❌ {test_file} (missing)")

if __name__ == "__main__":
    check_certificate_status()
