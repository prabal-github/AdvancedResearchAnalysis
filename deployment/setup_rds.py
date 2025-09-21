# AWS RDS Database Setup Script

import psycopg2
import os
from urllib.parse import urlparse

def setup_rds_database():
    """
    Set up PostgreSQL database on AWS RDS
    """
    
    # RDS Configuration (update these with your actual RDS details)
    RDS_CONFIG = {
        'host': 'your-rds-endpoint.amazonaws.com',
        'port': 5432,
        'database': 'research',
        'username': 'research_admin',
        'password': 'your_secure_password'  # Use AWS Secrets Manager in production
    }
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=RDS_CONFIG['host'],
            port=RDS_CONFIG['port'],
            database='postgres',  # Connect to default database first
            user=RDS_CONFIG['username'],
            password=RDS_CONFIG['password']
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create research database if it doesn't exist
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'research'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE research")
            print("✅ Research database created")
        else:
            print("✅ Research database already exists")
        
        cursor.close()
        conn.close()
        
        # Connect to research database and create tables
        conn = psycopg2.connect(
            host=RDS_CONFIG['host'],
            port=RDS_CONFIG['port'],
            database='research',
            user=RDS_CONFIG['username'],
            password=RDS_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # Create extensions
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")
        print("✅ PostgreSQL extensions created")
        
        # Database URL for .env file
        database_url = f"postgresql://{RDS_CONFIG['username']}:{RDS_CONFIG['password']}@{RDS_CONFIG['host']}:{RDS_CONFIG['port']}/research"
        
        print("✅ RDS Database setup completed!")
        print(f"Database URL: {database_url}")
        print("Update your .env file with this DATABASE_URL")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error setting up RDS database: {e}")
        print("Make sure your RDS instance is running and accessible")

if __name__ == "__main__":
    setup_rds_database()