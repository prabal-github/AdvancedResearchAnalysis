"""
Test script to verify portfolio_commentary table functionality
"""

from flask import Flask
import sqlite3
from app import app, db, PortfolioCommentary

def test_portfolio_commentary():
    with app.app_context():
        # Connect to the database directly to the instance folder
        db_path = 'instance/investment_research.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Connected to database at {db_path}")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(portfolio_commentary)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Display current data
        cursor.execute("SELECT * FROM portfolio_commentary")
        rows = cursor.fetchall()
        print("\nCurrent data:")
        if rows:
            for row in rows:
                print(f"  {row}")
        else:
            print("  No data found")
        
        # Add a test record with investor_id
        print("\nAdding a test record with investor_id...")
        
        # Using SQLAlchemy model
        new_commentary = PortfolioCommentary(
            commentary_text="Test commentary with investor_id",
            market_data="{'test': 'market_data'}",
            analysis_metadata="{'test': 'metadata'}",
            improvements_made="Test improvements",
            investor_id="test_investor_123"
        )
        
        db.session.add(new_commentary)
        db.session.commit()
        print("Record added via SQLAlchemy")
        
        # Verify the record was added with investor_id
        cursor.execute("SELECT * FROM portfolio_commentary WHERE investor_id='test_investor_123'")
        test_record = cursor.fetchone()
        
        if test_record:
            print(f"\nFound test record with investor_id: {test_record}")
        else:
            print("\nTest record not found!")
            
        # Clean up test data
        cursor.execute("DELETE FROM portfolio_commentary WHERE investor_id='test_investor_123'")
        conn.commit()
        print("\nTest record removed")
        
        # Close the connection
        conn.close()

if __name__ == "__main__":
    test_portfolio_commentary()
