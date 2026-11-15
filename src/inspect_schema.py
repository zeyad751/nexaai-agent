from src.connection import get_connection


def inspect_schema():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
    """)

    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        print("\n" + "=" * 60)
        print(f"TABLE: {table}")
        print("=" * 60)

        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        print("\nColumns:")
        for column in columns:
            column_id, name, data_type, not_null, default_value, primary_key = column

            print(
                f"  {name} | "
                f"type={data_type} | "
                f"primary_key={primary_key}"
            )

        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()

        print("\nSample rows:")
        for row in rows:
            print(" ", row)

    connection.close()


if __name__ == "__main__":
    inspect_schema()