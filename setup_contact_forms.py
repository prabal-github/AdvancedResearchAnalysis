"""
Contact Form System Database Setup
Run this script to create the necessary database tables for the contact form system.
"""
import os
import sys

# Add the app directory to the path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from app import app, db, ContactForm, ContactFormSubmission

def setup_contact_form_tables():
    """Create the contact form tables and add sample data"""
    
    print("🚀 Setting up Contact Form System...")
    
    with app.app_context():
        try:
            # Create tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if sample forms already exist
            existing_forms = ContactForm.query.count()
            if existing_forms > 0:
                print(f"📝 Found {existing_forms} existing forms. Skipping sample data creation.")
                return
            
            # Create sample contact forms
            print("📝 Creating sample contact forms...")
            
            sample_forms = [
                {
                    'form_title': 'Contact Us',
                    'form_subject': 'General Inquiry',
                    'form_description': 'Get in touch with our team for any questions or support.',
                    'form_slug': 'contact_us',
                    'require_phone': True,
                    'success_message': 'Thank you for contacting us! Our team will get back to you within 24 hours.',
                    'created_by': 'system'
                },
                {
                    'form_title': 'Newsletter Signup',
                    'form_subject': 'Newsletter Subscription',
                    'form_description': 'Subscribe to our newsletter to receive the latest market insights and research updates.',
                    'form_slug': 'newsletter',
                    'require_phone': False,
                    'success_message': 'Welcome to our newsletter! You will receive our latest updates and insights.',
                    'created_by': 'system'
                },
                {
                    'form_title': 'Know About Our Services',
                    'form_subject': 'Service Information Request',
                    'form_description': 'Learn more about our financial research and analytics services.',
                    'form_slug': 'services_info',
                    'require_phone': True,
                    'success_message': 'Thank you for your interest! Our team will contact you to discuss our services in detail.',
                    'created_by': 'system'
                },
                {
                    'form_title': 'Investment Consultation',
                    'form_subject': 'Investment Advisory Request',
                    'form_description': 'Schedule a consultation with our certified investment advisors.',
                    'form_slug': 'investment_consultation',
                    'require_phone': True,
                    'success_message': 'Your consultation request has been received. Our advisor will contact you to schedule a meeting.',
                    'created_by': 'system'
                },
                {
                    'form_title': 'Partnership Inquiry',
                    'form_subject': 'Business Partnership',
                    'form_description': 'Interested in partnering with us? Let us know how we can work together.',
                    'form_slug': 'partnership',
                    'require_phone': True,
                    'success_message': 'Thank you for your partnership inquiry. Our business development team will be in touch.',
                    'created_by': 'system'
                }
            ]
            
            for form_data in sample_forms:
                form = ContactForm(**form_data)
                db.session.add(form)
            
            db.session.commit()
            print(f"✅ Created {len(sample_forms)} sample contact forms!")
            
            # Display the created forms
            print("\n📋 Available Contact Forms:")
            print("-" * 50)
            for form in ContactForm.query.all():
                print(f"📄 {form.form_title}")
                print(f"   URL: /form/{form.form_slug}")
                print(f"   Subject: {form.form_subject}")
                print(f"   Phone Required: {'Yes' if form.require_phone else 'No'}")
                print()
            
            print("🌐 Admin Access:")
            print("   Forms Management: /admin/contact_forms")
            print("   Create New Form: /admin/contact_forms/create")
            print()
            print("🎉 Contact Form System setup complete!")
            
        except Exception as e:
            print(f"❌ Error setting up contact form system: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    setup_contact_form_tables()
