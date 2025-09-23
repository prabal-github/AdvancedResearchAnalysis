#!/usr/bin/env python3
"""
Test script to demonstrate certificate management workflow
"""

import sys
import os
from datetime import date, timedelta

# Add the parent directory to the path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, CertificateRequest, CertificateTemplate

def create_sample_certificate_request():
    """Create a sample certificate request for testing"""
    
    with app.app_context():
        try:
            # Check if sample request already exists
            existing_request = CertificateRequest.query.filter_by(
                analyst_name='Test Analyst John Doe'
            ).first()
            
            if existing_request:
                print(f"✅ Sample certificate request already exists: {existing_request.id}")
                return existing_request.id
            
            # Create sample certificate request
            start_date = date.today() - timedelta(days=90)  # 3 months ago
            end_date = date.today() - timedelta(days=7)     # 1 week ago
            issue_date = date.today()
            
            sample_request = CertificateRequest(
                analyst_name='Test Analyst John Doe',
                analyst_email='john.doe@predictram.com',
                internship_start_date=start_date,
                internship_end_date=end_date,
                requested_issue_date=issue_date,
                request_message='I have completed my internship program successfully and would like to request my certificate. During my internship, I worked on multiple research reports and learned financial analysis techniques.'
            )
            
            db.session.add(sample_request)
            db.session.commit()
            
            print(f"✅ Sample certificate request created: {sample_request.id}")
            print(f"   Analyst: {sample_request.analyst_name}")
            print(f"   Period: {sample_request.internship_start_date} to {sample_request.internship_end_date}")
            print(f"   Status: {sample_request.status}")
            
            return sample_request.id
            
        except Exception as e:
            print(f"❌ Error creating sample request: {e}")
            return None

def approve_sample_request(request_id):
    """Approve the sample request for testing"""
    
    with app.app_context():
        try:
            request = CertificateRequest.query.get(request_id)
            if not request:
                print(f"❌ Request {request_id} not found")
                return False
            
            if request.status == 'approved':
                print(f"✅ Request {request_id} already approved")
                return True
            
            # Approve the request
            from datetime import datetime
            request.status = 'approved'
            request.performance_score = 92.5
            request.admin_notes = 'Excellent performance during internship. Strong analytical skills and good report quality.'
            request.approved_by = 'Admin Test User'
            request.approved_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Certificate request approved!")
            print(f"   Performance Score: {request.performance_score}/100")
            print(f"   Admin Notes: {request.admin_notes}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error approving request: {e}")
            return False

def test_certificate_generation(request_id):
    """Test certificate generation"""
    
    with app.app_context():
        try:
            from app import generate_certificate_pdf
            
            request = CertificateRequest.query.get(request_id)
            if not request:
                print(f"❌ Request {request_id} not found")
                return False
            
            if request.status != 'approved':
                print(f"❌ Request must be approved before generating certificate")
                return False
            
            if request.certificate_generated:
                print(f"✅ Certificate already generated: {request.certificate_file_path}")
                print(f"   Certificate ID: {request.certificate_unique_id}")
                return True
            
            print(f"🔄 Generating certificate PDF...")
            
            # Generate certificate
            pdf_path = generate_certificate_pdf(request)
            
            print(f"✅ Certificate generated successfully!")
            print(f"   PDF Path: {pdf_path}")
            print(f"   Certificate ID: {request.certificate_unique_id}")
            print(f"   File exists: {os.path.exists(pdf_path)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating certificate: {e}")
            import traceback
            traceback.print_exc()
            return False

def show_certificate_system_status():
    """Show certificate system status"""
    
    with app.app_context():
        try:
            total_requests = CertificateRequest.query.count()
            pending_requests = CertificateRequest.query.filter_by(status='pending').count()
            approved_requests = CertificateRequest.query.filter_by(status='approved').count()
            rejected_requests = CertificateRequest.query.filter_by(status='rejected').count()
            generated_certificates = CertificateRequest.query.filter_by(certificate_generated=True).count()
            
            print(f"\n📊 Certificate System Status")
            print(f"   Total Requests: {total_requests}")
            print(f"   Pending: {pending_requests}")
            print(f"   Approved: {approved_requests}")
            print(f"   Rejected: {rejected_requests}")
            print(f"   Certificates Generated: {generated_certificates}")
            
            if total_requests > 0:
                print(f"\n📋 Recent Requests:")
                recent_requests = CertificateRequest.query.order_by(CertificateRequest.requested_at.desc()).limit(5).all()
                for req in recent_requests:
                    status_emoji = "✅" if req.status == "approved" else "⏳" if req.status == "pending" else "❌"
                    cert_info = f" (Cert: {req.certificate_unique_id})" if req.certificate_unique_id else ""
                    print(f"   {status_emoji} {req.analyst_name} - {req.status}{cert_info}")
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🧪 Certificate Management System Test")
    print("=" * 40)
    
    # Show initial status
    show_certificate_system_status()
    
    # Create sample request
    print(f"\n1. Creating sample certificate request...")
    request_id = create_sample_certificate_request()
    
    if request_id:
        # Approve sample request
        print(f"\n2. Approving sample request...")
        if approve_sample_request(request_id):
            
            # Test certificate generation
            print(f"\n3. Testing certificate generation...")
            if test_certificate_generation(request_id):
                
                print(f"\n4. Final status...")
                show_certificate_system_status()
                
                print(f"\n🎉 Certificate system test completed successfully!")
                print(f"\n🔗 Test the system at:")
                print(f"   📝 http://127.0.0.1:80/analyst/certificate_request")
                print(f"   📋 http://127.0.0.1:80/analyst/certificate_status")
                print(f"   ⚙️  http://127.0.0.1:80/admin/certificates")
            else:
                print(f"\n❌ Certificate generation test failed")
        else:
            print(f"\n❌ Approval test failed")
    else:
        print(f"\n❌ Sample request creation failed")
