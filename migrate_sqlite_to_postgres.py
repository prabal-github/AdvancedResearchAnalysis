"""
One-time data migration from SQLite to PostgreSQL.

Usage (PowerShell):
  # Ensure target DB schema exists (run app once or run migrations)
  $env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
  python migrate_sqlite_to_postgres.py -SourceSqlitePath "instance/investment_research.db"

Notes:
  - Requires psycopg2-binary installed.
  - Creates connections to SQLite (source) and Postgres (target) via SQLAlchemy.
  - Reflects tables and copies rows table-by-table.
  - Attempts to reset Postgres sequences for integer primary keys after insert.
"""

from __future__ import annotations
import argparse
import os
from typing import List

from sqlalchemy import create_engine, MetaData, Table, inspect, text as sa_text
from sqlalchemy.engine import Engine


def build_sqlite_url(path: str) -> str:
    # Accept absolute or relative path
    if path.startswith("sqlite://"):
        return path
    # Normalize backslashes
    normalized = path.replace("\\", "/")
    if not (normalized.startswith("/") or ":/" in normalized):
        # relative
        return f"sqlite:///{normalized}"
    return f"sqlite:///{normalized}"


def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Copy data from SQLite to Postgres")
    p.add_argument("-SourceSqlitePath", required=True, help="Path to SQLite DB file or sqlite:/// URL")
    p.add_argument("-TargetUrl", default=os.getenv("DATABASE_URL", ""), help="Postgres SQLAlchemy URL; defaults to env DATABASE_URL")
    p.add_argument("--skip-tables", nargs="*", default=[], help="Table names to skip during copy")
    return p.parse_args()


def normalize_pg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def reflect_metadata(engine: Engine) -> MetaData:
    md = MetaData()
    md.reflect(bind=engine)
    return md


def create_missing_tables_on_target_from_source(source_md: MetaData, target_engine: Engine) -> int:
    """
    For any tables present in source_md but missing on target, create them on the target
    using SQLAlchemy's to_metadata to copy table definitions. Returns number of tables created.
    Note: This is best-effort and may not fully capture DB-specific features like sequences
    or constraints beyond what SQLAlchemy reflects; adequate for typical SQLite -> Postgres.
    """
    created = 0
    target_md = MetaData()
    # Reflect current target to know existing tables
    current_target = reflect_metadata(target_engine)
    for tbl_name, src_tbl in source_md.tables.items():
        if tbl_name not in current_target.tables:
            # Copy table definition into a new MetaData bound to target
            src_tbl.to_metadata(target_md)
            created += 1
    if created:
        target_md.create_all(bind=target_engine)
    return created


def copy_table(source_engine: Engine, target_engine: Engine, table: Table, skip: bool) -> int:
    if skip:
        return 0
    src_conn = source_engine.connect()
    tgt_conn = target_engine.connect()
    rows_copied = 0
    trans = tgt_conn.begin()
    try:
        result = src_conn.execute(table.select())
        rows = result.fetchall()
        if rows:
            # Convert Row objects to plain dicts
            dict_rows = [dict(r._mapping) for r in rows]
            tgt_conn.execute(table.insert(), dict_rows)
            rows_copied = len(rows)
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        src_conn.close()
        tgt_conn.close()
    return rows_copied


def reset_serial_sequences(target_engine: Engine, tables: List[Table]):
    # Best effort: set sequence to max(id) for tables having 'id' integer PK
    try:
        with target_engine.begin() as conn:
            for t in tables:
                # Heuristic: integer primary key named 'id'
                pk_cols = [c for c in t.columns if c.primary_key]
                if len(pk_cols) == 1 and pk_cols[0].name == 'id' and str(pk_cols[0].type).lower().startswith('integer'):
                    try:
                        conn.execute(sa_text(
                            "SELECT setval(pg_get_serial_sequence(:tbl, 'id'), COALESCE((SELECT MAX(id) FROM "
                            + t.name + "), 1))"
                        ), {"tbl": t.name})
                    except Exception:
                        # Ignore if not a serial/identity table
                        pass
    except Exception:
        pass


def main():
    args = get_args()
    if not args.TargetUrl:
        raise SystemExit("TargetUrl not provided and DATABASE_URL not set")

    src_url = build_sqlite_url(args.SourceSqlitePath)
    tgt_url = normalize_pg_url(args.TargetUrl)

    print(f"Source: {src_url}")
    print(f"Target: {tgt_url}")

    source_engine = create_engine(src_url)
    target_engine = create_engine(tgt_url)

    # Ensure target has schema created, creating any missing tables from source if needed
    target_inspector = inspect(target_engine)
    if not target_inspector.get_table_names():
        print("Target has no tables; attempting to create schema from source metadata…")
        created = create_missing_tables_on_target_from_source(reflect_metadata(source_engine), target_engine)
        print(f"Created {created} tables on target from source metadata.")
    else:
        # Create any tables present in source but missing on target
        created = create_missing_tables_on_target_from_source(reflect_metadata(source_engine), target_engine)
        if created:
            print(f"Created {created} missing tables on target.")

    src_md = reflect_metadata(source_engine)
    tgt_md = reflect_metadata(target_engine)

    skipped = set(args.skip_tables or [])

    total = 0
    for tbl_name, table in src_md.tables.items():
        if tbl_name not in tgt_md.tables:
            print(f"Skipping {tbl_name}: not present on target")
            continue
        print(f"Copying {tbl_name}…", end=" ")
        try:
            count = copy_table(source_engine, target_engine, tgt_md.tables[tbl_name], tbl_name in skipped)
            total += count
            print(f"{count} rows")
        except Exception as e:
            print(f"FAILED: {e}")

    # Try to reset sequences for common id columns
    reset_serial_sequences(target_engine, list(tgt_md.tables.values()))

    print(f"Done. Rows copied: {total}")


if __name__ == "__main__":
    main()
