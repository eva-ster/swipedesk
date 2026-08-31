"""Streamlit UI. Leest uitsluitend de genormaliseerde tabellen — roept nooit
de Meta API aan. Zie docs/technisch-ontwerp.md hoofdstuk 7.
UI-teksten staan als sleutels in i18n.py, vormgeving in styles.py."""

from datetime import date

import altair as alt
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


def chart_basis(grafiek: alt.Chart) -> alt.Chart:
    """Terugtredende assen en raster, conform het themapalet."""
    return grafiek.configure_view(strokeWidth=0).configure_axis(
        gridColor=styles.CHART_GRID[mode],
        domainColor=styles.CHART_GRID[mode],
        tickColor=styles.CHART_GRID[mode],
        labelColor=styles.CHART_INK[mode],
        titleColor=styles.CHART_INK[mode],
        labelFontSize=11,
        titleFontSize=11,
        titleFontWeight="normal",
    )


def screen_dashboard() -> None:
    st.header(t("dash.header", lang))
    df = latest_signals()

    if df.empty:
        st.info(t("dash.empty", lang))
        screen_bronstatus()
        return

    getagd = conn.execute("SELECT COUNT(*) AS n FROM tags").fetchone()["n"]
    laatste = conn.execute(
        "SELECT MAX(date(fetched_at)) AS d FROM raw_responses WHERE status = 'ok'"
    ).fetchone()["d"]
    dagen_oud = (date.today() - date.fromisoformat(laatste)).days if laatste else None

    kolommen = st.columns(4)
    kpis = [
        (t("dash.kpi.ads", lang), str(len(df)), ""),
        (t("dash.kpi.advertisers", lang), str(df["advertiser"].nunique()), ""),
        (t("dash.kpi.tagged", lang), str(getagd), ""),
        (
            t("dash.kpi.freshness", lang),
            str(dagen_oud) if dagen_oud is not None else t("dash.kpi.freshness_never", lang),
            "",
        ),
    ]
    for kolom, (label, waarde, accent) in zip(kolommen, kpis):
        kolom.markdown(styles.tile(label, waarde, accent), unsafe_allow_html=True)

    # Een verouderde reeks tast de longevity aan; dat hoort zichtbaar te zijn.
    if dagen_oud is None:
        st.warning(t("dash.never_fetched", lang))
    elif dagen_oud > 1:
        st.warning(t("dash.stale_warning", lang).format(days=dagen_oud))

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Drie getallen verdienen geen grafiek — het label draagt de betekenis,
    # de kleur bevestigt hem alleen (FO hoofdstuk 5: geen schijnprecisie).
    st.subheader(t("dash.distribution", lang))
    telling = df["verdict"].value_counts()
    for kolom, verdict in zip(st.columns(3), VERDICTS):
        kolom.markdown(
            styles.tile(verdict_label(verdict), str(int(telling.get(verdict, 0))), verdict),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    kolom_hist, kolom_trend = st.columns(2, gap="large")

    with kolom_hist:
        st.subheader(t("dash.longevity", lang))
        histogram = (
            alt.Chart(df)
            .mark_bar(color=styles.CHART_HUE[mode], cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("longevity_days:Q", bin=alt.Bin(maxbins=20),
                        title=t("dash.longevity_axis", lang)),
                y=alt.Y("count():Q", title=t("dash.longevity_count", lang),
                        axis=alt.Axis(tickMinStep=1)),
                tooltip=[
                    alt.Tooltip("longevity_days:Q", bin=alt.Bin(maxbins=20),
                                title=t("dash.longevity_axis", lang)),
                    alt.Tooltip("count():Q", title=t("dash.longevity_count", lang)),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(chart_basis(histogram), width="stretch")

    with kolom_trend:
        st.subheader(t("dash.trend", lang))
        verloop = pd.read_sql_query(
            """SELECT computed_on, COUNT(*) AS aantal
               FROM signals WHERE verdict = 'strong'
               GROUP BY computed_on ORDER BY computed_on""",
            conn,
        )
        # Eén meetpunt is geen verloop; dat suggereren zou liegen over wat we weten.
        if len(verloop) < 2:
            st.caption(t("dash.trend_need_days", lang))
        else:
            lijn = (
                alt.Chart(verloop)
                .mark_line(color=styles.CHART_HUE[mode], strokeWidth=2,
                           point=alt.OverlayMarkDef(size=80, filled=True))
                .encode(
                    x=alt.X("computed_on:T", title=t("dash.trend_axis", lang),
                            axis=alt.Axis(format="%-d %b", tickCount=len(verloop),
                                          labelAngle=0, labelFlush=True)),
                    y=alt.Y("aantal:Q", title=verdict_label("strong"),
                            axis=alt.Axis(tickMinStep=1)),
                    tooltip=[
                        alt.Tooltip("computed_on:T", title=t("dash.trend_axis", lang),
                                    format="%-d %b %Y"),
                        alt.Tooltip("aantal:Q", title=verdict_label("strong")),
                    ],
                )
                .properties(height=260)
            )
            st.altair_chart(chart_basis(lijn), width="stretch")

    st.divider()
    screen_bronstatus()
    st.caption(t("dash.caveat", lang))


def screen_bronstatus() -> None:
    st.subheader(t("dash.source_health", lang))
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
        return

    bron.columns = [
        t("settings.niche", lang),
        t("settings.term", lang),
        t("feed.filter.country", lang),
        t("settings.col.last_ok", lang),
        t("settings.col.last_attempt", lang),
    ]
    st.dataframe(bron, width="stretch", hide_index=True)


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
    screen_bronstatus()


SCHERMEN = {
    "nav.dashboard": screen_dashboard,
    "nav.feed": screen_feed,
    "nav.swipefile": screen_swipefile,
    "nav.settings": screen_instellingen,
}

keuze = st.sidebar.radio(t("nav.screen", lang), list(SCHERMEN), format_func=lambda k: t(k, lang))

SCHERMEN[keuze]()

# Na het scherm, zodat de hint onder de filters uitkomt die het scherm toevoegt.
st.sidebar.divider()
st.sidebar.caption(t("nav.appearance_hint", lang))
