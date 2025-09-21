"""
Bulk-migrate all detected SQLite .db files in this workspace to the configured Postgres DATABASE_URL.

It will:
- Find .db files under the project root and instance/ folder
- For each DB, create missing tables on the target (best-effort) and copy rows

Usage (PowerShell):
  $env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
  python migrate_all_sqlite_to_postgres.py

You can also pass --include and --exclude patterns.
"""

import argparse
import os
import glob
import fnmatch
from typing import List
from subprocess import check_call


def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Migrate all SQLite DBs to Postgres")
    p.add_argument("--include", nargs="*", default=["*.db"], help="Glob patterns to include")
    p.add_argument("--exclude", nargs="*", default=[], help="Glob patterns to exclude")
    p.add_argument("--dry-run", action="store_true", help="List what would be migrated and exit")
    return p.parse_args()


def should_exclude(path: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(os.path.basename(path), pat) or fnmatch.fnmatch(path, pat):
            return True
    return False


def main():
    args = get_args()
    db_url = os.getenv("DATABASE_URL", "")

    # Search common locations: project root and instance/
    root = os.getcwd()
    candidates = []
    for inc in args.include:
        candidates.extend(glob.glob(os.path.join(root, inc)))
        candidates.extend(glob.glob(os.path.join(root, "instance", inc)))

    # De-duplicate and filter excludes
    seen = set()
    final = []
    for c in candidates:
        c = os.path.abspath(c)
        if c in seen:
            continue
        seen.add(c)
        if should_exclude(c, args.exclude):
            continue
        final.append(c)

    if not final:
        print("No SQLite .db files found to migrate.")
        return

    print("Databases to migrate:")
    for f in final:
        print(f" - {f}")

    if args.dry_run:
        if not db_url:
            print("(dry-run) DATABASE_URL not set; listing only.")
        return

    if not db_url:
        raise SystemExit("DATABASE_URL not set. Set it to your Postgres URL.")

    # Run per-DB migration using existing script
    script = os.path.join(root, "migrate_sqlite_to_postgres.py")
    for f in final:
        print(f"\nMigrating {f} …")
        check_call(["python", script, "-SourceSqlitePath", f])

    print("\nAll migrations completed.")


if __name__ == "__main__":
    main()
