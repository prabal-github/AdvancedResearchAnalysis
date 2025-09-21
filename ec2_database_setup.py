#!/usr/bin/env python3
"""
EC2 Database Setup Script
Fixes SQLite database file permissions and initialization issues for AWS EC2 deployment
"""

import os
import sys
import sqlite3
import stat
from pathlib import Path

def setup_database_directories():
    """Create and set proper permissions for database directories"""
    print("🔧 Setting up database directories...")
    
    # Get the application directory
    app_dir = Path("/var/www/financial-dashboard")
    
    # Create necessary directories
    directories = [
        app_dir / "instance",
        app_dir / "secure_artifacts", 
        app_dir / "logs",
        app_dir / "temp"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            # Set proper permissions (read/write for owner and group)
            directory.chmod(0o775)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def fix_database_permissions():
    """Fix SQLite database file permissions"""
    print("🔧 Fixing database file permissions...")
    
    app_dir = Path("/var/www/financial-dashboard")
    
    # Common database file locations
    db_files = [
        app_dir / "investment_research.db",
        app_dir / "instance" / "investment_research.db",
        app_dir / "reports.db",
        app_dir / "dashboard.db",
        app_dir / "ml_ai_system.db"
    ]
    
    for db_file in db_files:
        if db_file.exists():
            try:
                # Set read/write permissions for owner and group
                db_file.chmod(0o664)
                print(f"✅ Fixed permissions for: {db_file}")
            except Exception as e:
                print(f"❌ Failed to fix permissions for {db_file}: {e}")
        else:
            print(f"📝 Database file not found: {db_file}")

def initialize_database():
    """Initialize the main database with proper permissions"""
    print("🔧 Initializing main database...")
    
    # Import the Flask app to get the database configuration
    sys.path.append('/var/www/financial-dashboard')
    
    try:
        from app import app, db
        from config import Config
        
        with app.app_context():
            # Get the database URI
            db_uri = Config.SQLALCHEMY_DATABASE_URI
            print(f"📊 Database URI: {db_uri}")
            
            if db_uri.startswith('sqlite:///'):
                # Extract the database file path
                db_path = db_uri.replace('sqlite:///', '')
                db_file = Path(db_path)
                
                # Ensure the directory exists
                db_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create the database if it doesn't exist
                if not db_file.exists():
                    print(f"📝 Creating database file: {db_file}")
                    db_file.touch()
                
                # Set proper permissions
                db_file.chmod(0o664)
                
                # Initialize database tables
                db.create_all()
                print("✅ Database tables created successfully")
                
                # Test database connection
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    print(f"✅ Database connection test successful. Tables: {len(tables)}")
                except Exception as e:
                    print(f"❌ Database connection test failed: {e}")
                    return False
                    
            else:
                # PostgreSQL or other database
                print("📊 Using PostgreSQL/external database")
                db.create_all()
                print("✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def set_ownership():
    """Set proper ownership for application files"""
    print("🔧 Setting file ownership...")
    
    app_dir = "/var/www/financial-dashboard"
    
    try:
        # Change ownership to ubuntu:www-data
        os.system(f"sudo chown -R ubuntu:www-data {app_dir}")
        print(f"✅ Set ownership to ubuntu:www-data for {app_dir}")
        
        # Set proper permissions for the application directory
        os.system(f"sudo chmod -R 755 {app_dir}")
        print(f"✅ Set permissions to 755 for {app_dir}")
        
        # Set special permissions for database files and directories
        os.system(f"sudo find {app_dir} -name '*.db' -exec chmod 664 {{}} \\;")
        os.system(f"sudo find {app_dir} -type d -exec chmod 775 {{}} \\;")
        print("✅ Set special permissions for database files and directories")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to set ownership: {e}")
        return False

def create_admin_user():
    """Create an admin user if it doesn't exist"""
    print("🔧 Creating admin user...")
    
    try:
        sys.path.append('/var/www/financial-dashboard')
        from app import app, db
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Import User model dynamically
            try:
                from app import User
                
                # Check if admin user exists
                admin_user = User.query.filter_by(email='admin@demo.com').first()
                
                if not admin_user:
                    # Create admin user
                    admin_user = User(
                        email='admin@demo.com',
                        password_hash=generate_password_hash('admin123'),
                        role='admin',
                        is_verified=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Admin user created: admin@demo.com / admin123")
                else:
                    print("✅ Admin user already exists")
                
                return True
                
            except Exception as model_error:
                print(f"⚠️ Could not create admin user (model not found): {model_error}")
                return True  # Not a critical failure
                
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def run_database_migrations():
    """Run any pending database migrations"""
    print("🔧 Running database migrations...")
    
    migration_scripts = [
        "add_skill_learning_column.py",
        "add_anthropic_tables.py",
        "add_category_column.py",
        "add_description_column.py"
    ]
    
    app_dir = "/var/www/financial-dashboard"
    
    for script in migration_scripts:
        script_path = Path(app_dir) / script
        if script_path.exists():
            try:
                os.system(f"cd {app_dir} && python {script}")
                print(f"✅ Ran migration: {script}")
            except Exception as e:
                print(f"⚠️ Migration {script} failed: {e}")
        else:
            print(f"📝 Migration script not found: {script}")

def main():
    """Main setup function"""
    print("🚀 EC2 Database Setup Starting...")
    print("=" * 50)
    
    success = True
    
    # Step 1: Setup directories
    if not setup_database_directories():
        success = False
    
    # Step 2: Set ownership (requires sudo)
    if not set_ownership():
        success = False
    
    # Step 3: Fix permissions
    fix_database_permissions()
    
    # Step 4: Initialize database
    if not initialize_database():
        success = False
    
    # Step 5: Run migrations
    run_database_migrations()
    
    # Step 6: Create admin user
    create_admin_user()
    
    print("=" * 50)
    if success:
        print("✅ EC2 Database Setup Completed Successfully!")
        print("\n📋 Next steps:")
        print("1. Start the application: sudo systemctl start financial-dashboard")
        print("2. Check logs: sudo journalctl -u financial-dashboard -f")
        print("3. Test admin login: http://your-domain.com/admin_login")
        print("   Email: admin@demo.com")
        print("   Password: admin123")
    else:
        print("❌ EC2 Database Setup Failed!")
        print("Check the error messages above and fix the issues.")
    
    return success

if __name__ == "__main__":
    main()