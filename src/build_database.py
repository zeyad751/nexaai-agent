import sqlite3
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_FOLDER = PROJECT_ROOT / "data" / "nexaai_database"
DATABASE_PATH = PROJECT_ROOT / "data" / "nexaai.sqlite"


def build_database():
    connection = sqlite3.connect(DATABASE_PATH)

    for csv_file in CSV_FOLDER.glob("*.csv"):
        table_name = csv_file.stem

        print(f"Loading {table_name}...")

        dataframe = pd.read_csv(csv_file)

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False
        )

    connection.close()

    print("\nNexaAI SQLite database created successfully!")


if __name__ == "__main__":
    build_database()