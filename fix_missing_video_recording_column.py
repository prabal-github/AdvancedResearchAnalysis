"""One-off repair script to ensure session_bookings.video_recording_url exists.
Usage (PowerShell):

  python fix_missing_video_recording_column.py

Steps:
 1. Checks if column exists.
 2. If missing, tries simple ALTER TABLE.
 3. Verifies; if still missing, rebuilds table preserving data.
 4. Prints final schema.

Safe to re-run; will no-op if column already present.
"""
from app import db, app  # noqa
from sqlalchemy import text
import time


def column_exists_sqlite(engine, table: str, column: str) -> bool:
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})")
        return any(r[1] == column for r in rows)


def print_sqlite_cols(engine, table: str):
    with engine.connect() as conn:
        cols = [r[1] for r in conn.exec_driver_sql(f"PRAGMA table_info({table})")]
    print(f"Columns in {table}: {cols}")
    return cols


def attempt_alter(engine):
    try:
        print("Attempting ALTER TABLE add column ...")
        db.session.execute(text("ALTER TABLE session_bookings ADD COLUMN video_recording_url VARCHAR(500)"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"ALTER failed: {e}")


def rebuild_table(engine):
    ts = int(time.time())
    old_name = f"session_bookings_old_{ts}"
    print(f"Rebuilding table: renaming session_bookings -> {old_name}")
    with engine.connect() as conn:
        conn.exec_driver_sql(f"ALTER TABLE session_bookings RENAME TO {old_name}")
    create_sql = """
    CREATE TABLE session_bookings (
        id INTEGER PRIMARY KEY,
        investor_id VARCHAR(32) NOT NULL,
        analyst_id INTEGER NOT NULL,
        start_utc DATETIME NOT NULL,
        end_utc DATETIME NOT NULL,
        status VARCHAR(20),
        price_quote FLOAT,
        video_join_url VARCHAR(500),
        video_host_url VARCHAR(500),
        provider_meeting_id VARCHAR(120),
        created_at DATETIME,
        updated_at DATETIME,
        video_recording_url VARCHAR(500),
        UNIQUE(analyst_id, start_utc, end_utc)
    );
    """
    with engine.connect() as conn:
        conn.exec_driver_sql(create_sql)
        old_cols = [r[1] for r in conn.exec_driver_sql(f"PRAGMA table_info({old_name})")]
    copy_cols = [c for c in ['id','investor_id','analyst_id','start_utc','end_utc','status','price_quote','video_join_url','video_host_url','provider_meeting_id','created_at','updated_at'] if c in old_cols]
    with engine.begin() as conn:
        conn.exec_driver_sql(f"INSERT INTO session_bookings ({','.join(copy_cols)}) SELECT {','.join(copy_cols)} FROM {old_name}")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_session_bookings_investor_id ON session_bookings (investor_id)")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_session_bookings_analyst_id ON session_bookings (analyst_id)")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_session_bookings_start_utc ON session_bookings (start_utc)")
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_session_bookings_status ON session_bookings (status)")
    print("Rebuild complete.")


def main():
    engine = db.engine  # Requires app context
    if not engine:
        print("No engine bound; aborting.")
        return
    if engine.dialect.name != 'sqlite':
        print("This repair script is for SQLite only. For other DBs use a standard migration.")
        return
    print_sqlite_cols(engine, 'session_bookings')
    if column_exists_sqlite(engine, 'session_bookings', 'video_recording_url'):
        print("Column already present. Nothing to do.")
        return
    attempt_alter(engine)
    if column_exists_sqlite(engine, 'session_bookings', 'video_recording_url'):
        print("Column added via ALTER.")
        print_sqlite_cols(engine, 'session_bookings')
        return
    print("ALTER did not add column. Proceeding with rebuild.")
    rebuild_table(engine)
    print_sqlite_cols(engine, 'session_bookings')
    if column_exists_sqlite(engine, 'session_bookings', 'video_recording_url'):
        print("SUCCESS: video_recording_url present after rebuild.")
    else:
        print("FAILED: Column still missing after rebuild.")


if __name__ == '__main__':
    with app.app_context():
        main()
