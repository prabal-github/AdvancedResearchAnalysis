Support Admin Account

This project includes a helper script to ensure an admin account exists that logs in via credentials only (no direct-link login).

Default credentials
- Email: support@predictram.com
- Password: Subir@aug@2025

Usage
1) Ensure dependencies and database are ready.
2) Run the script:
   python create_support_admin_account.py

This will create or update the admin with the above credentials. You can then log in at /admin_login using the form or via JSON POST.

Security note
- Do not commit real production credentials. For production, set env vars ADMIN_EMAIL and ADMIN_PASSWORD before running the script.
