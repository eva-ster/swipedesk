"""SQLite-verbinding en schema-migratie. Zie docs/technisch-ontwerp.md hoofdstuk 4."""

import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "./data/swipedesk.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


if __name__ == "__main__":
    connection = get_connection()
    init_schema(connection)
    print(f"Schema geïnitialiseerd op {DB_PATH}")
