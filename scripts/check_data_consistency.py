"""Check that the two data sources the agent's tools read hold the same data.

The 13 database tools read data/nexaai.sqlite (via src/connection.py).
run_sql_tool reads the CSV folder data/nexaai_database, loaded into in-memory SQLite.
If someone edits one source and not the other, the two tool groups would give
different answers. This script compares every table row by row, through the same
loading code each tool uses.

Run from the project root:  python -m scripts.check_data_consistency
Exit code 0 = consistent, 1 = differences found.
"""
import math
import sys

from src.connection import get_connection
from src.tools.sql_tools import _snapshot_connection


def _norm(value):
    """Make values comparable across the two loaders (int vs float, NaN vs NULL)."""
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return round(value, 6)
    if isinstance(value, int):
        return round(float(value), 6)
    return str(value)


def _table_rows(conn, table):
    cursor = conn.execute(f'SELECT * FROM "{table}"')
    columns = [c[0] for c in cursor.description]
    rows = sorted(
        (tuple(_norm(v) for v in row) for row in cursor.fetchall()),
        key=repr,
    )
    return columns, rows


def _tables(conn):
    return {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def check():
    sqlite_conn = get_connection()
    csv_conn = _snapshot_connection()
    problems = []
    try:
        sqlite_tables, csv_tables = _tables(sqlite_conn), _tables(csv_conn)
        for name in sorted(sqlite_tables ^ csv_tables):
            where = "nexaai.sqlite" if name in sqlite_tables else "CSV folder"
            problems.append(f"table '{name}' exists only in {where}")

        for table in sorted(sqlite_tables & csv_tables):
            cols_a, rows_a = _table_rows(sqlite_conn, table)
            cols_b, rows_b = _table_rows(csv_conn, table)
            if cols_a != cols_b:
                problems.append(f"{table}: columns differ")
            elif rows_a != rows_b:
                only_a = len(set(rows_a) - set(rows_b))
                only_b = len(set(rows_b) - set(rows_a))
                problems.append(
                    f"{table}: {only_a} row(s) only in nexaai.sqlite, "
                    f"{only_b} row(s) only in the CSVs"
                )
            else:
                print(f"OK  {table:22s} {len(rows_a):4d} rows")
    finally:
        sqlite_conn.close()
        csv_conn.close()
    return problems


if __name__ == "__main__":
    found = check()
    if found:
        print("\nINCONSISTENT:")
        for problem in found:
            print("  -", problem)
        sys.exit(1)
    print("\nBoth data sources are consistent.")
