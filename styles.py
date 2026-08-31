"""Eigen stijllaag bovenop het Streamlit-thema (.streamlit/config.toml).

Streamlit stelt zijn themakleuren niet als CSS-variabelen beschikbaar, dus de
palletten staan hier per modus en worden geïnjecteerd op basis van de actief
gekozen modus. Zo volgen de eigen componenten (signaalbadges, kaarten) de
light/dark-keuze van de gebruiker in plaats van er los van te staan."""

import streamlit as st

# Signaalkleuren zijn bewust categorisch — drie stappen, geen verloop. FO
# hoofdstuk 5: een verloop zou een precisie suggereren die de brondata niet heeft.
PALETTES = {
    "light": {
        "surface": "#FFFFFF",
        "surface_muted": "#F5F6F8",
        "border": "#E2E5EA",
        "text_muted": "#5B6270",
        "strong_bg": "#E7F6EE",
        "strong_fg": "#0F6B43",
        "strong_border": "#A8DFC4",
        "mid_bg": "#FDF3E2",
        "mid_fg": "#8A5A05",
        "mid_border": "#F0D3A0",
        "weak_bg": "#F1F2F4",
        "weak_fg": "#5B6270",
        "weak_border": "#DCDFE4",
    },
    "dark": {
        "surface": "#171A21",
        "surface_muted": "#1E222B",
        "border": "#2A2F3A",
        "text_muted": "#9BA3B2",
        "strong_bg": "#12301F",
        "strong_fg": "#6FD3A0",
        "strong_border": "#245C3C",
        "mid_bg": "#33260E",
        "mid_fg": "#E5B65C",
        "mid_border": "#5C4519",
        "weak_bg": "#1F232B",
        "weak_fg": "#9BA3B2",
        "weak_border": "#333945",
    },
}


def active_theme() -> str:
    theme = getattr(st.context, "theme", None)
    return "dark" if theme and theme.type == "dark" else "light"


def inject(mode: str) -> None:
    p = PALETTES[mode]
    st.markdown(
        f"""
        <style>
        /* Afgeleid van currentColor, dat Streamlit zelf per thema zet. Een
           vaste hex hier zou bij een themawissel zonder rerun uit de pas
           lopen — grote donkere vlakken op een lichte pagina. Zo kan dat niet. */
        .stApp {{
            --sd-surface: color-mix(in srgb, currentColor 4%, transparent);
            --sd-surface-muted: color-mix(in srgb, currentColor 6%, transparent);
            --sd-border: color-mix(in srgb, currentColor 16%, transparent);
            --sd-text-muted: color-mix(in srgb, currentColor 62%, transparent);
        }}

        .block-container {{ padding-top: 2.5rem; max-width: 1400px; }}

        h1, h2, h3 {{ letter-spacing: -0.015em; font-weight: 650; }}
        h2 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}

        /* Zachtere scheiding tussen kop en inhoud dan de standaard hr */
        .sd-subtle {{
            color: var(--sd-text-muted);
            font-size: 0.875rem;
            margin: -0.25rem 0 1.25rem 0;
        }}

        .sd-card {{
            background: var(--sd-surface);
            border: 1px solid var(--sd-border);
            border-radius: 0.75rem;
            padding: 1.25rem 1.5rem;
        }}

        .sd-badge {{
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            line-height: 1.5;
            border: 1px solid transparent;
            white-space: nowrap;
        }}
        .sd-badge-strong {{ background: {p['strong_bg']}; color: {p['strong_fg']}; border-color: {p['strong_border']}; }}
        .sd-badge-mid    {{ background: {p['mid_bg']};    color: {p['mid_fg']};    border-color: {p['mid_border']}; }}
        .sd-badge-weak   {{ background: {p['weak_bg']};   color: {p['weak_fg']};   border-color: {p['weak_border']}; }}

        .sd-copy {{
            background: var(--sd-surface-muted);
            border-left: 3px solid var(--sd-border);
            border-radius: 0 0.5rem 0.5rem 0;
            padding: 0.9rem 1.1rem;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .sd-meta {{ color: var(--sd-text-muted); font-size: 0.85rem; }}

        /* KPI-tegel. De waarde staat altijd naast een tekstlabel: kleur
           reinforceert de betekenis, maar draagt hem nooit alleen. */
        .sd-tile {{
            background: var(--sd-surface);
            border: 1px solid var(--sd-border);
            border-left: 3px solid var(--sd-accent, var(--sd-border));
            border-radius: 0.6rem;
            padding: 0.9rem 1.1rem;
            height: 100%;
        }}
        .sd-tile-label {{
            color: var(--sd-text-muted);
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 0.3rem;
        }}
        .sd-tile-value {{
            font-size: 1.75rem;
            font-weight: 650;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}
        .sd-tile-strong {{ --sd-accent: {p['strong_fg']}; }}
        .sd-tile-mid    {{ --sd-accent: {p['mid_fg']}; }}
        .sd-tile-weak   {{ --sd-accent: {p['weak_fg']}; }}

        /* Metric-labels iets rustiger dan de standaard */
        [data-testid="stMetricLabel"] {{ color: var(--sd-text-muted); }}

        section[data-testid="stSidebar"] h1 {{
            font-size: 1.35rem;
            margin-bottom: 0.5rem;
        }}

        /* Navigatie: knoppen die zich als navigatie-items gedragen —
           links uitgelijnd, volle breedte, actieve staat duidelijk. */
        section[data-testid="stSidebar"] .stButton > button {{
            justify-content: flex-start;
            text-align: left;
            font-weight: 500;
            padding: 0.45rem 0.7rem;
            margin-bottom: 0.15rem;
            border-radius: 0.5rem;
        }}
        /* Streamlit centreert de inhoud in een binnenste div; die moet mee. */
        section[data-testid="stSidebar"] .stButton > button > div {{
            justify-content: flex-start;
            width: 100%;
            gap: 0.6rem;
        }}
        section[data-testid="stSidebar"] .stButton > button p {{
            font-weight: 500;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge(verdict: str, label: str) -> str:
    return f'<span class="sd-badge sd-badge-{verdict}">{label}</span>'


def tile(label: str, value: str, accent: str = "") -> str:
    klasse = f"sd-tile sd-tile-{accent}" if accent else "sd-tile"
    return (
        f'<div class="{klasse}"><div class="sd-tile-label">{label}</div>'
        f'<div class="sd-tile-value">{value}</div></div>'
    )


# Chartkleuren. Bewust één hue voor magnitude in plaats van een kleur per
# signaal: de drie signaalkleuren liggen bij kleurenblindheid te dicht op
# elkaar (groen↔amber ΔE 5.2) om betekenis alleen via kleur te dragen.
#
# Eén set voor beide modi, niet twee. Altair bakt letterlijke kleuren in de
# SVG en kan geen CSS-variabele volgen; een modus-afhankelijke keuze zou dus
# bij een themawissel zonder rerun verkeerd blijven staan. Deze waarden zijn
# gekozen omdat ze op beide oppervlakken contrast halen:
#   #6366F1  4.47:1 op wit · 4.23:1 op #0F1116
#   #767E8B  4.10:1 op wit · 4.61:1 op #0F1116
CHART_HUE = "#6366F1"
CHART_INK = "#767E8B"
CHART_GRID = "rgba(118, 126, 139, 0.28)"
