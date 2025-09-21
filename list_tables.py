"""
Script to check database tables
"""

import sqlite3

def list_tables():
    conn = sqlite3.connect('instance/investment_research.db')
    cursor = conn.cursor()
    
    print("Checking tables in database...")
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    
    print('Tables in the database:')
    for table in tables:
        print(f'  {table[0]}')
    
    conn.close()

if __name__ == "__main__":
    list_tables()
