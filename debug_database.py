from app import app, db, AnalystProfile, InvestorAccount
from werkzeug.security import check_password_hash
import sqlite3

def check_database_records():
    """Check what's actually in the database"""
    print("🔍 Database Investigation")
    print("=" * 50)
    
    with app.app_context():
        # Check analyst profiles
        print("📊 ANALYST PROFILES:")
        print("-" * 30)
        analysts = AnalystProfile.query.all()
        print(f"Total analysts found: {len(analysts)}")
        
        for analyst in analysts:
            print(f"\n  ID: {analyst.id}")
            print(f"  Name: {analyst.name}")
            print(f"  Full Name: {analyst.full_name}")
            print(f"  Email: {analyst.email}")
            print(f"  Analyst ID: {analyst.analyst_id}")
            print(f"  Active: {analyst.is_active}")
            print(f"  Has Password Hash: {'Yes' if analyst.password_hash else 'No'}")
            if analyst.password_hash:
                # Test password
                test_pass = check_password_hash(analyst.password_hash, 'analyst123')
                print(f"  Password 'analyst123' Valid: {test_pass}")
        
        # Check investor accounts
        print("\n💰 INVESTOR ACCOUNTS:")
        print("-" * 30)
        investors = InvestorAccount.query.all()
        print(f"Total investors found: {len(investors)}")
        
        for investor in investors:
            print(f"\n  ID: {investor.id}")
            print(f"  Email: {investor.email}")
            print(f"  Active: {investor.is_active}")
            print(f"  Has Password Hash: {'Yes' if investor.password_hash else 'No'}")
            if investor.password_hash:
                # Test password
                test_pass = check_password_hash(investor.password_hash, 'investor123')
                print(f"  Password 'investor123' Valid: {test_pass}")

def check_database_schema():
    """Check the actual database schema"""
    print("\n🏗️ DATABASE SCHEMA CHECK")
    print("=" * 50)
    
    # Connect directly to SQLite
    conn = sqlite3.connect('investment_research.db')
    cursor = conn.cursor()
    
    # Check analyst_profile table
    print("📊 analyst_profile table structure:")
    cursor.execute("PRAGMA table_info(analyst_profile)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - Nullable: {not col[3]}")
    
    print("\n📊 analyst_profile data:")
    cursor.execute("SELECT id, name, email, password_hash, is_active FROM analyst_profile")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Has Hash: {'Yes' if row[3] else 'No'}, Active: {row[4]}")
    
    # Check investor_account table
    print("\n💰 investor_account table structure:")
    cursor.execute("PRAGMA table_info(investor_account)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - Nullable: {not col[3]}")
    
    print("\n💰 investor_account data:")
    cursor.execute("SELECT id, email, password_hash, is_active FROM investor_account")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  ID: {row[0]}, Email: {row[1]}, Has Hash: {'Yes' if row[2] else 'No'}, Active: {row[3]}")
    
    conn.close()

def test_manual_login():
    """Test login manually with exact database data"""
    print("\n🧪 MANUAL LOGIN TEST")
    print("=" * 50)
    
    with app.app_context():
        # Test analyst login logic
        print("Testing analyst login logic:")
        email = 'analyst@demo.com'
        password = 'analyst123'
        
        analyst = AnalystProfile.query.filter_by(email=email, is_active=True).first()
        if analyst:
            print(f"  ✅ Analyst found: {analyst.name}")
            print(f"  Email match: {analyst.email == email}")
            print(f"  Is active: {analyst.is_active}")
            if analyst.password_hash:
                password_valid = check_password_hash(analyst.password_hash, password)
                print(f"  Password valid: {password_valid}")
            else:
                print("  ❌ No password hash stored")
        else:
            print("  ❌ No analyst found with that email and active status")
        
        # Test investor login logic
        print("\nTesting investor login logic:")
        email = 'investor@demo.com'
        password = 'investor123'
        
        investor = InvestorAccount.query.filter_by(email=email, is_active=True).first()
        if investor:
            print(f"  ✅ Investor found")
            print(f"  Email match: {investor.email == email}")
            print(f"  Is active: {investor.is_active}")
            if investor.password_hash:
                password_valid = check_password_hash(investor.password_hash, password)
                print(f"  Password valid: {password_valid}")
            else:
                print("  ❌ No password hash stored")
        else:
            print("  ❌ No investor found with that email and active status")

if __name__ == "__main__":
    check_database_records()
    check_database_schema()
    test_manual_login()
