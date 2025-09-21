#!/usr/bin/env python3
"""
Database migration script to add certificate management tables
"""

import sys
import os

# Add the parent directory to the path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, CertificateRequest, CertificateTemplate

def create_certificate_tables():
    """Create certificate management tables"""
    print("🗄️  Creating Certificate Management Tables...")
    
    with app.app_context():
        try:
            # Create all tables (this is safe - will only create missing tables)
            db.create_all()
            
            # Create default certificate template if it doesn't exist
            default_template = CertificateTemplate.query.filter_by(template_name='Default Internship').first()
            
            if not default_template:
                default_template = CertificateTemplate(
                    template_name='Default Internship',
                    template_type='internship',
                    title='CERTIFICATE OF INTERNSHIP',
                    subtitle='Financial Analyst',
                    description_template="""has successfully completed the Financial Analyst Internship program at PredictRAM.
Intern conducted in-depth analysis, tracked market data, and provided forecasts on economic
events. Intern developed research reports on national economic conditions and financial trends,
while contributing to secondary financial research to support team outputs. Additionally, Intern
utilized python for predictive analysis.""",
                    logo_path='image.png',
                    badge_path='pngwing555.png',
                    signature1_path='signature1.png',
                    signature2_path='signature2.png',
                    footer_path='Supported By1.png',
                    signature1_name='Subir Singh',
                    signature1_title='Director - PredictRAM',
                    signature2_name='Sheetal Maurya',
                    signature2_title='Assistant Professor'
                )
                
                db.session.add(default_template)
                db.session.commit()
                print("✅ Default certificate template created")
            else:
                print("✅ Default certificate template already exists")
            
            print("✅ Certificate management tables created successfully!")
            
            # Show table info
            certificate_requests = CertificateRequest.query.count()
            certificate_templates = CertificateTemplate.query.count()
            
            print(f"📊 Database Status:")
            print(f"   - Certificate Requests: {certificate_requests}")
            print(f"   - Certificate Templates: {certificate_templates}")
            
        except Exception as e:
            print(f"❌ Error creating certificate tables: {e}")
            return False
    
    return True

def show_certificate_info():
    """Show information about certificate system"""
    print("\n🎓 CERTIFICATE MANAGEMENT SYSTEM")
    print("=" * 50)
    print("Features:")
    print("✅ Analyst certificate requests")
    print("✅ Admin approval workflow")
    print("✅ Performance score assignment")
    print("✅ PDF certificate generation")
    print("✅ Unique certificate IDs")
    print("✅ Digital signatures and branding")
    print("✅ Download and sharing capabilities")
    
    print("\n🔗 Access URLs:")
    print("   📝 Request Certificate: /analyst/certificate_request")
    print("   📋 Certificate Status: /analyst/certificate_status")
    print("   ⚙️  Admin Management: /admin/certificates")
    
    print("\n📋 Workflow:")
    print("1. Analyst submits certificate request with dates")
    print("2. Admin reviews and approves with performance score")
    print("3. System generates PDF certificate with unique ID")
    print("4. Both analyst and admin can download certificate")

if __name__ == "__main__":
    print("🚀 Certificate Management System Setup")
    print("=" * 40)
    
    if create_certificate_tables():
        show_certificate_info()
        print(f"\n🎉 Certificate system is ready!")
    else:
        print(f"\n❌ Setup failed. Please check the errors above.")
