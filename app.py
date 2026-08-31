"""Streamlit UI. Leest uitsluitend de genormaliseerde tabellen — roept nooit
de Meta API aan. Zie docs/technisch-ontwerp.md hoofdstuk 7.
UI-teksten staan als sleutels in i18n.py, vormgeving in styles.py."""

import pandas as pd
import streamlit as st

import styles
from db import get_connection, init_schema
from i18n import DEFAULT_LANG, LANGUAGES, t

VERDICTS = ["strong", "mid", "weak"]
VERDICT_ORDER = {v: i for i, v in enumerate(VERDICTS)}

st.set_page_config(page_title="Swipedesk", layout="wide")

mode = styles.active_theme()
styles.inject(mode)
palette = styles.PALETTES[mode]

conn = get_connection()
init_schema(conn)

# De taalkeuze bepaalt zijn eigen label: session_state houdt de vorige keuze
# vast, zodat het label na een wissel niet in de oude taal blijft staan.
lang = st.session_state.get("lang", DEFAULT_LANG)

st.sidebar.title(t("app.title"))
st.sidebar.caption(t("app.tagline", lang))
lang = st.sidebar.selectbox(
    t("nav.language", lang), list(LANGUAGES), key="lang", format_func=lambda c: LANGUAGES[c]
)


def verdict_label(verdict: str) -> str:
    return t(f"verdict.{verdict}", lang)


def latest_signals() -> pd.DataFrame:
    return pd.read_sql_query(
        """SELECT a.id, a.meta_ad_id, adv.name AS advertiser, a.landing_url,
                  a.format, a.copy_text, a.creative_url, a.first_seen,
                  s.longevity_days, s.variant_count, s.verdict
           FROM signals s
           JOIN ads a ON a.id = s.ad_id
           JOIN advertisers adv ON adv.id = a.advertiser_id
           WHERE s.computed_on = (SELECT MAX(computed_on) FROM signals)""",
        conn,
    )


def kleur_verdict(waarde: str) -> str:
    for verdict in VERDICTS:
        if waarde == verdict_label(verdict):
            p = styles.PALETTES[mode]
            return f"background-color: {p[f'{verdict}_bg']}; color: {p[f'{verdict}_fg']};"
    return ""


def screen_feed() -> None:
    st.header(t("feed.header", lang))
    alles = latest_signals()

    if alles.empty:
        st.info(t("feed.empty", lang))
        return

    telling = alles["verdict"].value_counts()
    st.markdown(
        f"<div class='sd-subtle'>"
        + t("feed.summary", lang).format(
            total=len(alles),
            strong=int(telling.get("strong", 0)),
            mid=int(telling.get("mid", 0)),
            weak=int(telling.get("weak", 0)),
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    gekozen_verdict = st.sidebar.multiselect(
        t("feed.filter.signal", lang), VERDICTS, default=VERDICTS, format_func=verdict_label
    )
    landen = pd.read_sql_query("SELECT DISTINCT land FROM tracked_queries", conn)["land"].tolist()
    if landen:
        st.sidebar.multiselect(t("feed.filter.country", lang), landen, default=landen)

    df = alles[alles["verdict"].isin(gekozen_verdict)]
    if df.empty:
        st.info(t("feed.no_match", lang))
        return

    df = df.sort_values(
        by=["verdict", "longevity_days"],
        key=lambda col: col.map(VERDICT_ORDER) if col.name == "verdict" else col,
        ascending=[True, False],
    )

    tabel = df[["advertiser", "verdict", "longevity_days", "variant_count", "copy_text"]].copy()
    tabel["verdict"] = tabel["verdict"].map(verdict_label)
    tabel.columns = [
        t("feed.col.advertiser", lang),
        t("feed.col.verdict", lang),
        t("feed.col.longevity", lang),
        t("feed.col.variants", lang),
        t("feed.col.copy", lang),
    ]
    st.dataframe(
        tabel.style.map(kleur_verdict, subset=[t("feed.col.verdict", lang)]),
        width="stretch",
        hide_index=True,
    )

    st.divider()
    st.subheader(t("feed.detail_header", lang))
    keuze = st.selectbox(
        t("feed.select_detail", lang),
        df["id"],
        label_visibility="collapsed",
        format_func=lambda i: f"{df.loc[df['id'] == i, 'advertiser'].iloc[0]} — {df.loc[df['id'] == i, 'meta_ad_id'].iloc[0]}",
    )
    if keuze:
        screen_detail(df[df["id"] == keuze].iloc[0])


def screen_detail(ad: pd.Series) -> None:
    kolom_links, kolom_rechts = st.columns([3, 2], gap="large")

    with kolom_links:
        st.markdown(
            f"#### {ad['advertiser']} &nbsp; {styles.badge(ad['verdict'], verdict_label(ad['verdict']))}",
            unsafe_allow_html=True,
        )
        copy = ad["copy_text"] or t("detail.no_copy", lang)
        st.markdown(f"<div class='sd-copy'>{copy}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='sd-meta' style='margin-top:0.75rem'>"
            f"{t('detail.landing_page', lang)}: {ad['landing_url'] or t('detail.unknown', lang)}"
            f" · {t('detail.active_since', lang)} {ad['first_seen']}</div>",
            unsafe_allow_html=True,
        )
        if ad["creative_url"]:
            st.link_button(t("detail.view_creative", lang), ad["creative_url"])

    with kolom_rechts:
        st.metric(t("detail.metric.longevity", lang), int(ad["longevity_days"]))
        st.metric(t("detail.metric.variants", lang), int(ad["variant_count"]))
        st.caption(t("detail.variants_caveat", lang))

    with st.expander(t("swipefile.save_title", lang)):
        with st.form(f"tag_{ad['id']}", clear_on_submit=True):
            veld_links, veld_midden, veld_rechts = st.columns(3)
            hook = veld_links.text_input(t("swipefile.hook", lang))
            angle = veld_midden.text_input(t("swipefile.angle", lang))
            formaat = veld_rechts.text_input(t("swipefile.format", lang))
            note = st.text_area(t("swipefile.note", lang))
            if st.form_submit_button(t("swipefile.save", lang), type="primary"):
                conn.execute(
                    "INSERT INTO tags (ad_id, hook, angle, format, note) VALUES (?, ?, ?, ?, ?)",
                    (int(ad["id"]), hook, angle, formaat, note),
                )
                conn.commit()
                st.success(t("swipefile.saved", lang))


def screen_swipefile() -> None:
    st.header(t("swipefile.header", lang))
    df = pd.read_sql_query(
        """SELECT t.hook, t.angle, t.format, t.note, t.tagged_at,
                  adv.name AS advertiser
           FROM tags t
           JOIN ads a ON a.id = t.ad_id
           JOIN advertisers adv ON adv.id = a.advertiser_id
           ORDER BY t.tagged_at DESC""",
        conn,
    )

    if df.empty:
        st.info(t("swipefile.empty", lang))
        return

    zoek = st.text_input(t("swipefile.search", lang), label_visibility="collapsed",
                         placeholder=t("swipefile.search", lang))
    if zoek:
        masker = df.apply(lambda r: zoek.lower() in " ".join(map(str, r.values)).lower(), axis=1)
        df = df[masker]

    df.columns = [
        t("swipefile.hook", lang),
        t("swipefile.angle", lang),
        t("swipefile.format", lang),
        t("swipefile.col.note", lang),
        t("swipefile.col.tagged_at", lang),
        t("feed.col.advertiser", lang),
    ]
    st.dataframe(df, width="stretch", hide_index=True)


def screen_instellingen() -> None:
    st.header(t("settings.header", lang))

    st.subheader(t("settings.queries_title", lang))
    queries = pd.read_sql_query(
        "SELECT niche, term, platform, land FROM tracked_queries", conn
    )
    if not queries.empty:
        st.dataframe(queries, width="stretch", hide_index=True)

    with st.form("nieuwe_query", clear_on_submit=True):
        kolom_niche, kolom_term, kolom_land = st.columns([2, 2, 1])
        niche = kolom_niche.text_input(t("settings.niche", lang))
        term = kolom_term.text_input(t("settings.term", lang))
        land = kolom_land.text_input(t("settings.country", lang), value="NL")
        if st.form_submit_button(t("settings.add", lang), type="primary") and niche and term and land:
            conn.execute(
                "INSERT INTO tracked_queries (niche, term, platform, land) VALUES (?, ?, 'meta', ?)",
                (niche, term, land.upper()),
            )
            conn.commit()
            st.rerun()

    ids = pd.read_sql_query("SELECT id, niche, term FROM tracked_queries", conn)
    if not ids.empty:
        kolom_keuze, kolom_knop = st.columns([3, 1], vertical_alignment="bottom")
        verwijderen = kolom_keuze.selectbox(
            t("settings.delete_select", lang),
            ids["id"],
            format_func=lambda i: f"{ids.loc[ids['id'] == i, 'niche'].iloc[0]} — {ids.loc[ids['id'] == i, 'term'].iloc[0]}",
        )
        if kolom_knop.button(t("settings.delete", lang)):
            conn.execute("DELETE FROM tracked_queries WHERE id = ?", (int(verwijderen),))
            conn.commit()
            st.rerun()

    st.divider()
    st.subheader(t("settings.source_title", lang))
    bron = pd.read_sql_query(
        """SELECT q.niche, q.term, q.land,
                  MAX(CASE WHEN r.status = 'ok' THEN r.fetched_at END) AS last_ok,
                  MAX(r.fetched_at) AS last_attempt
           FROM tracked_queries q
           LEFT JOIN raw_responses r ON r.query_id = q.id
           GROUP BY q.id""",
        conn,
    )
    if bron.empty:
        st.caption(t("settings.source_empty", lang))
    else:
        bron.columns = [
            t("settings.niche", lang),
            t("settings.term", lang),
            t("feed.filter.country", lang),
            t("settings.col.last_ok", lang),
            t("settings.col.last_attempt", lang),
        ]
        st.dataframe(bron, width="stretch", hide_index=True)


SCHERMEN = {
    "nav.feed": screen_feed,
    "nav.swipefile": screen_swipefile,
    "nav.settings": screen_instellingen,
}

keuze = st.sidebar.radio(t("nav.screen", lang), list(SCHERMEN), format_func=lambda k: t(k, lang))

SCHERMEN[keuze]()

# Na het scherm, zodat de hint onder de filters uitkomt die het scherm toevoegt.
st.sidebar.divider()
st.sidebar.caption(t("nav.appearance_hint", lang))
