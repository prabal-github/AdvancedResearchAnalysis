#!/usr/bin/env python3
"""
Test the enhanced performance PDF generation
"""

import os
import sys
from datetime import datetime, date

# Add the current directory to the path to import the app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the app and function
    from app import app, generate_performance_analysis_pdf
    
    print("🔄 Testing enhanced performance PDF generation...")
    
    with app.app_context():
        # Test with a sample analyst name
        test_analyst = "TestAnalyst"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 9, 16)
        
        print(f"Generating PDF for analyst: {test_analyst}")
        
        try:
            pdf_path = generate_performance_analysis_pdf(
                analyst_name=test_analyst,
                start_date=start_date,
                end_date=end_date
            )
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ PDF generated successfully!")
                print(f"📄 File path: {pdf_path}")
                print(f"📊 File size: {file_size:,} bytes")
                print(f"🕒 Created: {datetime.fromtimestamp(os.path.getctime(pdf_path))}")
            else:
                print(f"❌ PDF file not found at expected path: {pdf_path}")
                
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
    
except ImportError as e:
    print(f"❌ Error importing app: {e}")
    print("Make sure you're running this from the app directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running test: {e}")
    sys.exit(1)