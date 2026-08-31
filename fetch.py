"""Stap 1: Meta Ad Library API -> raw_responses. Raakt alleen de API en het
onveranderlijke ruwe archief. Zie docs/technisch-ontwerp.md hoofdstuk 3 en 5."""

import json
import os
import sqlite3
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v19.0"
ADS_ARCHIVE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/ads_archive"
ACCESS_TOKEN = os.environ.get("META_AD_LIBRARY_ACCESS_TOKEN")

FIELDS = ",".join([
    "id",
    "page_id",
    "page_name",
    "ad_creative_link_captions",
    "ad_creative_bodies",
    "ad_snapshot_url",
    "ad_delivery_start_time",
    "ad_delivery_stop_time",
    "publisher_platforms",
])


def fetch_query(conn: sqlite3.Connection, query: sqlite3.Row) -> None:
    """Haalt alle pagina's op voor één tracked_query en slaat elke pagina
    onveranderlijk op in raw_responses. Eén mislukte query crasht de run niet."""
    params = {
        "search_terms": query["term"],
        "ad_reached_countries": json.dumps([query["land"]]),
        "ad_type": "ALL",
        "fields": FIELDS,
        "access_token": ACCESS_TOKEN,
        "limit": 100,
    }

    url = ADS_ARCHIVE_URL
    while url:
        try:
            response = requests.get(url, params=params if url == ADS_ARCHIVE_URL else None, timeout=30)
            response.raise_for_status()
            payload = response.json()
            save_raw(conn, query["id"], payload, status="ok")
        except requests.RequestException as exc:
            save_raw(conn, query["id"], {"error": str(exc)}, status="failed")
            return

        url = payload.get("paging", {}).get("next")


def save_raw(conn: sqlite3.Connection, query_id: int, payload: dict, status: str) -> None:
    conn.execute(
        "INSERT INTO raw_responses (query_id, fetched_at, payload, status) VALUES (?, ?, ?, ?)",
        (query_id, datetime.now(timezone.utc).isoformat(), json.dumps(payload), status),
    )
    conn.commit()


def fetch_all(conn: sqlite3.Connection) -> None:
    queries = conn.execute("SELECT * FROM tracked_queries").fetchall()
    for query in queries:
        fetch_query(conn, query)


if __name__ == "__main__":
    from db import get_connection, init_schema

    connection = get_connection()
    init_schema(connection)
    fetch_all(connection)
