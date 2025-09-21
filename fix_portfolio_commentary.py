"""
This script properly fixes the database schema issue with the PortfolioCommentary table.
It does this by:
1. Extracting existing data
2. Recreating the table with the correct schema
3. Reinserting the data
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import json
import os
from datetime import datetime

# Import app and models
from app import app, db, PortfolioCommentary

def migrate_portfolio_commentary():
    """Properly migrate the PortfolioCommentary table to include investor_id column"""
    print("Starting migration of PortfolioCommentary table...")
    
    try:
        with app.app_context():
            # Get SQLite database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print(f"Database file not found: {db_path}")
                return
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_commentary'")
            if not cursor.fetchone():
                print("Table 'portfolio_commentary' doesn't exist. Creating it...")
                # Just create the table via SQLAlchemy
                db.create_all()
                conn.close()
                print("✅ Table created successfully")
                return
            
            # Check if investor_id column exists
            cursor.execute("PRAGMA table_info(portfolio_commentary)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'investor_id' in column_names:
                print("investor_id column already exists. No migration needed.")
                conn.close()
                return
            
            print("Backing up existing portfolio_commentary data...")
            cursor.execute("SELECT * FROM portfolio_commentary")
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            
            # Create backup records
            backup_records = []
            for row in rows:
                record = {}
                for i, col_name in enumerate(column_names):
                    record[col_name] = row[i]
                backup_records.append(record)
                
            print(f"Backed up {len(backup_records)} records")
            
            # Drop the existing table
            print("Dropping existing table...")
            cursor.execute("DROP TABLE portfolio_commentary")
            conn.commit()
            
            # Create the new table with SQLAlchemy
            print("Creating new table with updated schema...")
            db.create_all()
            
            # Reinsert the data
            print("Reinserting data...")
            for record in backup_records:
                # Convert created_at back to datetime if it's a string
                if isinstance(record.get('created_at'), str):
                    record['created_at'] = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                
                commentary = PortfolioCommentary(
                    id=record.get('id'),
                    commentary_text=record.get('commentary_text', ''),
                    market_data=record.get('market_data'),
                    analysis_metadata=record.get('analysis_metadata'),
                    improvements_made=record.get('improvements_made'),
                    created_at=record.get('created_at'),
                    investor_id=None  # Default to None for existing records
                )
                db.session.add(commentary)
            
            # Commit the changes
            db.session.commit()
            conn.close()
            
            print(f"✅ Successfully migrated {len(backup_records)} records to the updated schema")
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_portfolio_commentary()
