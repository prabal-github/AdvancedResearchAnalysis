# Deploying to AWS with PostgreSQL

This app supports PostgreSQL via SQLAlchemy. SQLite-only code paths were removed or made DB-agnostic.

## Prerequisites

- PostgreSQL (AWS RDS is recommended)
- Set the environment variable `DATABASE_URL` like:
  - `postgresql://<username>:<password>@<host>:5432/<db_name>`
- Install requirements (includes `psycopg2-binary` and `Flask-Migrate`).

## App configuration

- `config.py` normalizes `postgres://` to `postgresql://` automatically.
- `.env.example` includes a Postgres example URL.

## Create schema

- Start the app once so `db.create_all()` runs, or set up Flask-Migrate and run migrations.

## Migrate existing data from SQLite

1. Ensure target schema exists on Postgres (run the app once).
2. Set `DATABASE_URL` to your Postgres URL.
3. Run the migration script:

```powershell
$env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
python migrate_sqlite_to_postgres.py -SourceSqlitePath "instance/investment_research.db"
```

Optional flags:

- `--skip-tables table1 table2` to skip specific tables.

### Migrate all .db files at once

To migrate all detected SQLite `.db` files (e.g., `investment_research.db`, `reports.db`, `research_reports.db`) in one go:

```powershell
$env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
python migrate_all_sqlite_to_postgres.py
```

List candidates without migrating:

```powershell
python migrate_all_sqlite_to_postgres.py --dry-run
```

## Running on AWS

- EC2 + systemd or Docker is fine. Ensure these env vars are set in the service:
  - `FLASK_DEBUG=false`
  - `APP_PORT=80`
  - `DATABASE_URL=postgresql://...`
  - `SECRET_KEY=<strong-random>`

## Notes

- The `/fix_database` and startup schema checks are DB-agnostic now.
- For complex schema changes, prefer Flask-Migrate over ad-hoc DDL.
