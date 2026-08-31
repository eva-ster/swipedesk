"""Cron-target: roept fetch -> parse -> signal na elkaar aan.
Zie docs/technisch-ontwerp.md hoofdstuk 5 en 8."""

from db import get_connection, init_schema
from fetch import fetch_all
from parse import parse_today
from signal_engine import compute_signals


def main() -> None:
    conn = get_connection()
    init_schema(conn)
    fetch_all(conn)
    parse_today(conn)
    compute_signals(conn)
    conn.close()


if __name__ == "__main__":
    main()
