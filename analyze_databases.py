import sqlite3
import os
import glob

# Find all .db files in current directory and subdirectories
db_files = glob.glob('**/*.db', recursive=True)
print('Found .db files:')
for db_file in db_files:
    print(f'  {db_file}')

print('\nAnalyzing database schemas:')
for db_file in db_files:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f'\n{db_file}:')
            for table in tables:
                print(f'  - {table[0]}')
            conn.close()
        except Exception as e:
            print(f'  Error reading {db_file}: {e}')
