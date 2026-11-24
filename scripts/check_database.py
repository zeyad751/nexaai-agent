"""Check that the agent's database is present and complete.

All 15 tools read one database, data/nexaai.sqlite: the 13 database tools through
src/connection.py, and run_sql_tool through an in-memory copy of the same file. This check
confirms the file opens read-only and that every expected table exists with data. The
server runs it at startup; /health reports "degraded" (HTTP 503) if it fails.

Run from the project root:  python -m scripts.check_database
Exit code 0 = OK, 1 = problems found.
"""
import sqlite3
import sys

from src.connection import DATABASE_PATH

EXPECTED_TABLES = (
    "clients", "decisions", "departments", "employees", "milestones", "project_kpis",
    "project_team", "project_technologies", "projects", "risks", "strategies",
    "technologies",
)


def check():
    """Return a list of problems; an empty list means the database is usable."""
    if not DATABASE_PATH.exists():
        return [f"database file not found: {DATABASE_PATH}"]
    problems = []
    try:
        conn = sqlite3.connect(f"file:{DATABASE_PATH.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return [f"cannot open {DATABASE_PATH.name}: {exc}"]
    try:
        present = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table in EXPECTED_TABLES:
            if table not in present:
                problems.append(f"table '{table}' is missing")
                continue
            rows = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            if rows == 0:
                problems.append(f"table '{table}' is empty")
            else:
                print(f"OK  {table:22s} {rows:4d} rows")
    except sqlite3.Error as exc:
        problems.append(f"cannot read {DATABASE_PATH.name}: {exc}")
    finally:
        conn.close()
    return problems


if __name__ == "__main__":
    found = check()
    if found:
        print("\nDATABASE PROBLEMS:")
        for problem in found:
            print("  -", problem)
        sys.exit(1)
    print("\nDatabase OK: all 12 tables present.")
