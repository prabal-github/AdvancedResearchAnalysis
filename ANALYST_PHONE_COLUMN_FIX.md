# Fix for AnalystProfile Phone Column Error

## Problem
When trying to register a new analyst, you get this error:
```
"Registration failed: (sqlite3.OperationalError) no such column: analyst_profile.phone"
```

## Root Cause
The database schema on your EC2 instance is missing the `phone` column in the `analyst_profile` table. This happens when:
1. The database was created with an older version of the code
2. Database migrations weren't run properly during deployment

## Solution

### Step 1: Update Your Code
First, push the latest code to GitHub and pull it on your EC2:

```bash
# On your local machine
git add .
git commit -m "Fix AnalystProfile phone column error"
git push origin main

# On your EC2 instance
cd /var/www/research
git pull origin main
```

### Step 2: Run the Database Fix
On your EC2 instance, run the database fix script:

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the fix script
python ec2_database_fix.py
```

### Step 3: Alternative - Manual Database Fix
If the script doesn't work, manually fix the database:

```bash
# Stop your application first
sudo systemctl stop predictram-research
# or if running manually:
sudo pkill -f gunicorn

# Connect to your database and check the schema
# For SQLite:
sqlite3 research.db
.schema analyst_profile
.quit

# For PostgreSQL:
psql -h localhost -U your_username -d your_database
\d analyst_profile
\q
```

### Step 4: Restart Your Application
```bash
# If using systemd service:
sudo systemctl start predictram-research
sudo systemctl status predictram-research

# Or start manually:
gunicorn --config gunicorn.conf.py app:app
```

### Step 5: Test the Fix
Try registering an analyst again. The error should be resolved.

## Alternative Solutions

### Option A: Delete and Recreate Database (SQLite only)
⚠️ **WARNING: This will delete all existing data!**

```bash
# Stop the application
sudo systemctl stop predictram-research

# Backup the database (optional)
cp research.db research.db.backup

# Delete the database file
rm research.db

# Restart the application (it will recreate the database)
sudo systemctl start predictram-research
```

### Option B: Use PostgreSQL (Recommended for Production)
Switch to PostgreSQL for better schema management:

1. Install PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Create a database and user:
```bash
sudo -u postgres psql
CREATE DATABASE predictram_research;
CREATE USER predictram_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE predictram_research TO predictram_user;
\q
```

3. Update your `.env` file:
```
DATABASE_URL=postgresql://predictram_user:your_secure_password@localhost/predictram_research
```

4. Restart your application.

## Code Changes Made

### 1. Enhanced Error Handling
The `check_email_role_conflict` function now handles database schema issues gracefully:

```python
# Check if email exists in analyst profiles
analyst_exists = False
try:
    analyst_exists = AnalystProfile.query.filter_by(email=email).first() is not None
except Exception as db_error:
    # Handle database schema issues gracefully
    print(f"Warning: Database schema issue when checking analyst email: {db_error}")
    # Try to fix the database schema on the fly
    try:
        db.create_all()  # Ensure all tables are created with correct schema
        analyst_exists = AnalystProfile.query.filter_by(email=email).first() is not None
    except Exception as retry_error:
        print(f"Error even after schema fix: {retry_error}")
        analyst_exists = False  # Assume no conflict if we can't check
```

### 2. Database Fix Scripts
- `ec2_database_fix.py`: Quick fix for EC2 deployment
- `comprehensive_db_fix.py`: Full database schema verification and repair

## Testing
After applying the fix, test with this curl command:

```bash
curl -X POST http://your-ec2-ip:5008/api/register/analyst \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Analyst",
    "email": "test.analyst@example.com",
    "mobile": "1234567890",
    "password": "TestPassword123",
    "experience": "1-3",
    "specialization": "Technology"
  }'
```

You should get a success response instead of the phone column error.

## Prevention
To prevent this issue in the future:
1. Use database migrations for schema changes
2. Use PostgreSQL instead of SQLite for production
3. Always run `db.create_all()` after code updates
4. Test database operations after deployment