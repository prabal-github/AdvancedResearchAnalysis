#!/usr/bin/env python3
"""
Debug the specific file creation issue
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def debug_file_creation():
    """Debug the specific file creation issue"""
    cert_dir = os.path.join('static', 'certificates')
    
    # Test 1: Simple file creation
    test_path = os.path.join(cert_dir, 'debug_test.txt')
    print(f"Test 1: Creating text file at {test_path}")
    try:
        with open(test_path, 'w') as f:
            f.write("test")
        print("✅ Text file created successfully")
        os.remove(test_path)
    except Exception as e:
        print(f"❌ Text file creation failed: {e}")
        return
    
    # Test 2: PDF with absolute path
    abs_path = os.path.abspath(os.path.join(cert_dir, 'debug_abs.pdf'))
    print(f"Test 2: Creating PDF with absolute path: {abs_path}")
    try:
        c = canvas.Canvas(abs_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF with absolute path")
        c.save()
        print("✅ PDF with absolute path created successfully")
        os.remove(abs_path)
    except Exception as e:
        print(f"❌ PDF with absolute path failed: {e}")
    
    # Test 3: PDF with relative path
    rel_path = os.path.join(cert_dir, 'debug_rel.pdf')
    print(f"Test 3: Creating PDF with relative path: {rel_path}")
    try:
        c = canvas.Canvas(rel_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF with relative path")
        c.save()
        print("✅ PDF with relative path created successfully")
        if os.path.exists(rel_path):
            os.remove(rel_path)
    except Exception as e:
        print(f"❌ PDF with relative path failed: {e}")
    
    # Test 4: PDF with normalized path
    norm_path = os.path.normpath(os.path.join(cert_dir, 'debug_norm.pdf'))
    print(f"Test 4: Creating PDF with normalized path: {norm_path}")
    try:
        c = canvas.Canvas(norm_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF with normalized path")
        c.save()
        print("✅ PDF with normalized path created successfully")
        if os.path.exists(norm_path):
            os.remove(norm_path)
    except Exception as e:
        print(f"❌ PDF with normalized path failed: {e}")

if __name__ == "__main__":
    debug_file_creation()
