"""Stap 2: raw_responses -> ads, advertisers, ad_snapshots. Zie
docs/technisch-ontwerp.md hoofdstuk 3 en 5."""

import json
import sqlite3
from datetime import date, datetime


def today_str() -> str:
    return date.today().isoformat()


def upsert_advertiser(conn: sqlite3.Connection, page_id: str, page_name: str) -> int:
    conn.execute(
        """INSERT INTO advertisers (meta_page_id, name) VALUES (?, ?)
           ON CONFLICT(meta_page_id) DO UPDATE SET name = excluded.name""",
        (page_id, page_name),
    )
    row = conn.execute(
        "SELECT id FROM advertisers WHERE meta_page_id = ?", (page_id,)
    ).fetchone()
    return row["id"]


def upsert_ad(conn: sqlite3.Connection, advertiser_id: int, item: dict) -> int:
    landing_url = item.get("ad_creative_link_captions", [None])[0]
    copy_text = " ".join(item.get("ad_creative_bodies", []) or [])
    first_seen = item.get("ad_delivery_start_time") or today_str()

    conn.execute(
        """INSERT INTO ads (advertiser_id, meta_ad_id, landing_url, format, first_seen, copy_text, creative_url)
           VALUES (?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(meta_ad_id) DO UPDATE SET
               landing_url = excluded.landing_url,
               copy_text = excluded.copy_text""",
        (advertiser_id, item["id"], landing_url, None, first_seen, copy_text, item.get("ad_snapshot_url")),
    )
    row = conn.execute("SELECT id FROM ads WHERE meta_ad_id = ?", (item["id"],)).fetchone()
    return row["id"]


def record_snapshot(conn: sqlite3.Connection, ad_id: int, observed_on: str, is_active: bool) -> None:
    conn.execute(
        """INSERT INTO ad_snapshots (ad_id, observed_on, is_active) VALUES (?, ?, ?)
           ON CONFLICT(ad_id, observed_on) DO UPDATE SET is_active = excluded.is_active""",
        (ad_id, observed_on, int(is_active)),
    )


def parse_today(conn: sqlite3.Connection) -> None:
    observed_on = today_str()
    raw_rows = conn.execute(
        "SELECT * FROM raw_responses WHERE date(fetched_at) = ? AND status = 'ok'",
        (observed_on,),
    ).fetchall()

    parsed_ad_ids = set()
    for raw in raw_rows:
        payload = json.loads(raw["payload"])
        for item in payload.get("data", []):
            advertiser_id = upsert_advertiser(conn, item["page_id"], item.get("page_name", ""))
            ad_id = upsert_ad(conn, advertiser_id, item)
            record_snapshot(conn, ad_id, observed_on, is_active=True)
            parsed_ad_ids.add(ad_id)

    mark_missing_ads_inactive(conn, observed_on, parsed_ad_ids)
    conn.commit()


def mark_missing_ads_inactive(conn: sqlite3.Connection, observed_on: str, seen_today: set[int]) -> None:
    all_ad_ids = {row["id"] for row in conn.execute("SELECT id FROM ads").fetchall()}
    for ad_id in all_ad_ids - seen_today:
        record_snapshot(conn, ad_id, observed_on, is_active=False)


if __name__ == "__main__":
    from db import get_connection, init_schema

    connection = get_connection()
    init_schema(connection)
    parse_today(connection)
