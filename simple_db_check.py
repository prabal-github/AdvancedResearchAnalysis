import sqlite3

try:
    conn = sqlite3.connect('ml_platform.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Available tables:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")