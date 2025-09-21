#!/usr/bin/env python3
"""
Fix all deprecated datetime.utcnow() usages in app.py
"""

import re

def fix_datetime_utcnow():
    """Replace all datetime.utcnow() with datetime.now(timezone.utc)"""
    
    file_path = r"c:\PythonProjectTestCopy\FinalDashboard12\Copy5AllRDS - Copy2 - Copy12AWSBEDROCK - Copy (10)3 - Copy2\app.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count original occurrences
    original_count = len(re.findall(r'datetime\.utcnow\(\)', content))
    print(f"Found {original_count} occurrences of datetime.utcnow()")
    
    # Replace datetime.utcnow() with datetime.now(timezone.utc)
    updated_content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(timezone.utc)', content)
    
    # Count updated occurrences
    remaining_count = len(re.findall(r'datetime\.utcnow\(\)', updated_content))
    fixed_count = original_count - remaining_count
    
    print(f"Fixed {fixed_count} occurrences")
    print(f"Remaining {remaining_count} occurrences")
    
    # Write the updated content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ File updated successfully")

if __name__ == "__main__":
    fix_datetime_utcnow()