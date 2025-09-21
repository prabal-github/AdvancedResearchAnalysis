"""
Script to update the PortfolioCommentary table by adding the investor_id column.
This is a one-time fix to update the database schema.
"""

import sqlite3
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, PortfolioCommentary

def update_portfolio_commentary_schema():
    """Update the portfolio_commentary table to add investor_id column if it doesn't exist"""
    print("Checking PortfolioCommentary table schema...")
    
    try:
        with app.app_context():
            # Get database file path from app config
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Connect directly to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if investor_id column exists
            cursor.execute("PRAGMA table_info(portfolio_commentary)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'investor_id' not in column_names:
                print("Adding investor_id column to portfolio_commentary table...")
                cursor.execute("ALTER TABLE portfolio_commentary ADD COLUMN investor_id INTEGER")
                conn.commit()
                print("✅ Successfully added investor_id column")
            else:
                print("investor_id column already exists in the table")
            
            conn.close()
            
            # Now recreate all tables to ensure schema is up-to-date
            print("Recreating all database tables to ensure schema is up-to-date...")
            db.create_all()
            print("✅ Database schema updated successfully")
            
    except Exception as e:
        print(f"❌ Error updating database schema: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    update_portfolio_commentary_schema()
