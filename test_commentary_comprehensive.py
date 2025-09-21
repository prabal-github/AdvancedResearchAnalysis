"""
Comprehensive test script to verify portfolio_commentary functionality with investor_id
"""

from flask import Flask
import sqlite3
import json
from app import app, db, PortfolioCommentary

def create_test_data():
    """Create test data for multiple investors"""
    with app.app_context():
        db_path = 'instance/investment_research.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== Creating test data for portfolio commentary ===")
        
        # Create test data for multiple investors
        test_data = [
            {
                "investor_id": "investor_1",
                "commentary_text": "Portfolio analysis for investor 1",
                "market_data": json.dumps({"market_index": "NIFTY", "change": 0.5}),
                "analysis_metadata": json.dumps({"stocks_analyzed": 10, "sectors": 5}),
                "improvements_made": "Added sector analysis"
            },
            {
                "investor_id": "investor_2",
                "commentary_text": "Portfolio analysis for investor 2",
                "market_data": json.dumps({"market_index": "SENSEX", "change": -0.2}),
                "analysis_metadata": json.dumps({"stocks_analyzed": 8, "sectors": 4}),
                "improvements_made": "Added technical indicators"
            },
            {
                "investor_id": "investor_3",
                "commentary_text": "Portfolio analysis for investor 3",
                "market_data": json.dumps({"market_index": "BSE500", "change": 0.3}),
                "analysis_metadata": json.dumps({"stocks_analyzed": 15, "sectors": 7}),
                "improvements_made": "Added risk metrics"
            }
        ]
        
        # Using SQLAlchemy to add the records
        for data in test_data:
            new_commentary = PortfolioCommentary(
                commentary_text=data["commentary_text"],
                market_data=data["market_data"],
                analysis_metadata=data["analysis_metadata"],
                improvements_made=data["improvements_made"],
                investor_id=data["investor_id"]
            )
            db.session.add(new_commentary)
        
        db.session.commit()
        print("✅ Test data created successfully")
        
        # Close the connection
        conn.close()

def verify_investor_filtering():
    """Verify that portfolio commentaries can be filtered by investor_id"""
    with app.app_context():
        db_path = 'instance/investment_research.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== Verifying investor filtering functionality ===")
        
        # Test filtering by investor_id
        for investor_id in ["investor_1", "investor_2", "investor_3"]:
            cursor.execute(
                "SELECT * FROM portfolio_commentary WHERE investor_id = ?", 
                (investor_id,)
            )
            results = cursor.fetchall()
            
            print(f"\nCommentaries for investor '{investor_id}':")
            if results:
                for row in results:
                    print(f"  ID: {row[0]}")
                    print(f"  Text: {row[1][:50]}...")
                    print(f"  Created at: {row[5]}")
                    print(f"  Investor ID: {row[6]}")
            else:
                print("  No commentaries found")
        
        # Verify that we can query all records
        cursor.execute("SELECT COUNT(*) FROM portfolio_commentary WHERE investor_id IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"\nTotal records with investor_id: {count}")
        
        # Close the connection
        conn.close()

def clean_test_data():
    """Remove test data"""
    with app.app_context():
        db_path = 'instance/investment_research.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== Cleaning up test data ===")
        
        # Delete test records
        cursor.execute(
            "DELETE FROM portfolio_commentary WHERE investor_id IN (?, ?, ?)",
            ("investor_1", "investor_2", "investor_3")
        )
        conn.commit()
        
        print(f"✅ Removed {cursor.rowcount} test records")
        
        # Close the connection
        conn.close()

if __name__ == "__main__":
    create_test_data()
    verify_investor_filtering()
    clean_test_data()
