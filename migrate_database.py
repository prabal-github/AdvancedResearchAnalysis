#!/usr/bin/env python3
"""
Database Migration and Setup Script
Creates all required tables and adds sample investor account
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, InvestorAccount, AnalystProfile, FundamentalAnalysis, BacktestingResult, AnalystPerformanceMetrics
from werkzeug.security import generate_password_hash
import random

def create_tables():
    """Create all database tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ All database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

def create_sample_investor():
    """Create a sample investor account for testing"""
    with app.app_context():
        try:
            # Check if sample investor already exists
            existing = InvestorAccount.query.filter_by(email='demo@investor.com').first()
            if existing:
                print("✅ Sample investor account already exists")
                print(f"   Email: demo@investor.com")
                print(f"   Password: demo123")
                print(f"   Investor ID: {existing.id}")
                return True
            
            # Create new sample investor
            investor_id = f"INV{random.randint(100000, 999999)}"
            sample_investor = InvestorAccount(
                id=investor_id,
                name="Demo Investor",
                email="demo@investor.com",
                password_hash=generate_password_hash("demo123"),
                created_by_admin="system"
            )
            
            db.session.add(sample_investor)
            db.session.commit()
            
            print("✅ Sample investor account created successfully")
            print(f"   Email: demo@investor.com")
            print(f"   Password: demo123")
            print(f"   Investor ID: {investor_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample investor: {e}")
            db.session.rollback()
            return False

def create_sample_analyst():
    """Create a sample analyst profile"""
    with app.app_context():
        try:
            # Check if sample analyst exists
            existing = AnalystProfile.query.filter_by(name='SampleAnalyst').first()
            if existing:
                print("✅ Sample analyst profile already exists")
                return True
            
            # Create sample analyst
            sample_analyst = AnalystProfile(
                name='SampleAnalyst',
                full_name='Sample Research Analyst',
                email='analyst@sample.com',
                university_name='Sample University',
                age=28,
                department='Finance',
                specialization='Equity Research',
                experience_years=3,
                certifications='["CFA Level 1", "FRM Part 1"]',
                sebi_registration='INH000000123',
                bio='Sample analyst for demonstration purposes',
                corporate_field='Equity Research',
                field_specialization='Technology Sector',
                talent_program_level='Intermediate Level',
                total_reports=5,
                avg_quality_score=75.5
            )
            
            db.session.add(sample_analyst)
            db.session.commit()
            
            print("✅ Sample analyst profile created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample analyst: {e}")
            db.session.rollback()
            return False

def main():
    """Main migration function"""
    print("🚀 Starting database migration and setup...")
    print("-" * 50)
    
    # Create tables
    if not create_tables():
        return False
    
    # Create sample data
    create_sample_investor()
    create_sample_analyst()
    
    print("-" * 50)
    print("✅ Database migration and setup completed successfully!")
    print("\n📝 Quick Access Information:")
    print("   Main Dashboard: http://localhost:80/")
    print("   Investor Login: http://localhost:80/investor_dashboard")
    print("   Demo Investor: demo@investor.com / demo123")
    print("   Admin Panel: http://localhost:80/admin_dashboard?admin_key=admin123")
    print("   Sample Analyst Profile: http://localhost:80/analyst/SampleAnalyst/profile")
    print("\n🎯 New Features Added:")
    print("   • Investor Authentication System")
    print("   • Admin Panel for Investor Management") 
    print("   • Detailed Fundamental Analysis for Indian Stocks")
    print("   • Backtesting Results Tracking")
    print("   • Enhanced Analyst Profiles with Performance Metrics")
    
    return True

if __name__ == '__main__':
    main()
