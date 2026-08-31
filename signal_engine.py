"""Stap 3: signaal-engine. Zie docs/functioneel-ontwerp.md hoofdstuk 5 en
docs/technisch-ontwerp.md hoofdstuk 6. Drempelwaarden zijn hardcoded
configuratiewaarden, niet een losse UI-instelling — wijzigen hoort in code
te gebeuren zodat het traceerbaar is in de git-historie."""

import sqlite3
from datetime import date, datetime, timedelta

LONGEVITY_THRESHOLD_DAYS = 45
VARIANT_THRESHOLD = 3


def classify(longevity_days: int, variant_count: int) -> str:
    strong_longevity = longevity_days >= LONGEVITY_THRESHOLD_DAYS
    strong_variants = variant_count >= VARIANT_THRESHOLD

    if strong_longevity and strong_variants:
        return "strong"
    if strong_longevity != strong_variants:
        return "mid"
    return "weak"


def longevity_days(conn: sqlite3.Connection, ad_id: int, observed_on: str) -> int:
    """Dagen sinds de advertentie volgens de API begon te draaien, mits vandaag
    nog actief. Niet het aantal eigen waarnemingsdagen: dan zou de tool 45 dagen
    moeten draaien voordat er ooit een sterk signaal kan verschijnen."""
    row = conn.execute(
        """SELECT a.first_seen, s.is_active FROM ads a
           LEFT JOIN ad_snapshots s ON s.ad_id = a.id AND s.observed_on = ?
           WHERE a.id = ?""",
        (observed_on, ad_id),
    ).fetchone()

    if not row["is_active"]:
        return 0

    start = datetime.fromisoformat(row["first_seen"][:10]).date()
    return max((date.fromisoformat(observed_on) - start).days, 0)


def count_active_variants(conn: sqlite3.Connection, ad_id: int, observed_on: str) -> int:
    ad = conn.execute("SELECT advertiser_id, landing_url FROM ads WHERE id = ?", (ad_id,)).fetchone()

    row = conn.execute(
        """SELECT COUNT(DISTINCT a.id) AS n
           FROM ads a
           JOIN ad_snapshots s ON s.ad_id = a.id
           WHERE a.advertiser_id = ? AND a.landing_url = ?
             AND s.observed_on = ? AND s.is_active = 1""",
        (ad["advertiser_id"], ad["landing_url"], observed_on),
    ).fetchone()
    return row["n"]


def compute_signals(conn: sqlite3.Connection) -> None:
    observed_on = date.today().isoformat()
    ads = conn.execute("SELECT id FROM ads").fetchall()

    for ad in ads:
        longevity = longevity_days(conn, ad["id"], observed_on)
        variants = count_active_variants(conn, ad["id"], observed_on)
        verdict = classify(longevity, variants)
        save_signal(conn, ad["id"], observed_on, longevity, variants, verdict)

    conn.commit()


def save_signal(conn: sqlite3.Connection, ad_id: int, computed_on: str,
                 longevity_days: int, variant_count: int, verdict: str) -> None:
    conn.execute(
        """INSERT INTO signals (ad_id, computed_on, longevity_days, variant_count, verdict)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(ad_id, computed_on) DO UPDATE SET
               longevity_days = excluded.longevity_days,
               variant_count = excluded.variant_count,
               verdict = excluded.verdict""",
        (ad_id, computed_on, longevity_days, variant_count, verdict),
    )


if __name__ == "__main__":
    from db import get_connection, init_schema

    connection = get_connection()
    init_schema(connection)
    compute_signals(connection)
