-- Swipedesk schema — zie docs/technisch-ontwerp.md hoofdstuk 4

CREATE TABLE IF NOT EXISTS tracked_queries (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    niche    TEXT NOT NULL,
    term     TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'meta',
    land     TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS raw_responses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id   INTEGER NOT NULL REFERENCES tracked_queries(id),
    fetched_at TEXT NOT NULL,
    payload    TEXT NOT NULL,   -- JSON, onveranderlijk
    status     TEXT NOT NULL CHECK (status IN ('ok', 'failed'))
);

CREATE TABLE IF NOT EXISTS advertisers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    meta_page_id TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    advertiser_id INTEGER NOT NULL REFERENCES advertisers(id),
    meta_ad_id    TEXT NOT NULL UNIQUE,
    landing_url   TEXT,
    format        TEXT,
    first_seen    TEXT NOT NULL,
    copy_text     TEXT,
    creative_url  TEXT
);

CREATE TABLE IF NOT EXISTS ad_snapshots (
    ad_id       INTEGER NOT NULL REFERENCES ads(id),
    observed_on TEXT NOT NULL,
    is_active   INTEGER NOT NULL CHECK (is_active IN (0, 1)),
    PRIMARY KEY (ad_id, observed_on)
);

CREATE TABLE IF NOT EXISTS signals (
    ad_id           INTEGER NOT NULL REFERENCES ads(id),
    computed_on     TEXT NOT NULL,
    longevity_days  INTEGER NOT NULL,
    variant_count   INTEGER NOT NULL,
    verdict         TEXT NOT NULL CHECK (verdict IN ('strong', 'mid', 'weak')),
    PRIMARY KEY (ad_id, computed_on)
);

CREATE TABLE IF NOT EXISTS tags (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_id     INTEGER NOT NULL REFERENCES ads(id),
    hook      TEXT,
    angle     TEXT,
    format    TEXT,
    note      TEXT,
    tagged_at TEXT NOT NULL DEFAULT (datetime('now'))
);
