"""
Fix datetime.utcnow() deprecation warnings in ml_models_postgres.py
"""

import re

# Read the file
with open('ml_models_postgres.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace datetime import to include timezone
if 'from datetime import datetime' in content:
    content = content.replace(
        'from datetime import datetime',
        'from datetime import datetime, timezone'
    )

# Replace all datetime.utcnow() with datetime.now(timezone.utc)
content = re.sub(r'\bdatetime\.utcnow\b', 'datetime.now(timezone.utc)', content)

# Write the updated content back
with open('ml_models_postgres.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Count replacements made
matches = re.findall(r'datetime\.now\(timezone\.utc\)', content)
print(f"✅ Fixed {len(matches)} datetime.utcnow() occurrences in ml_models_postgres.py")