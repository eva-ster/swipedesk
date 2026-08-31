"""Vertaalsleutels voor de UI. Platte dict per taal — geen gettext, geen
externe library: bij deze omvang voegt een extractie-toolchain alleen
onderhoudskosten toe. Een ontbrekende sleutel valt terug op DEFAULT_LANG,
zodat een half vertaalde taal de app niet breekt."""

DEFAULT_LANG = "nl"

LANGUAGES = {"nl": "Nederlands", "en": "English"}

TRANSLATIONS = {
    "nl": {
        # Navigatie
        "app.title": "Swipedesk",
        "nav.screen": "Scherm",
        "nav.dashboard": "Dashboard",
        "nav.feed": "Feed",
        "nav.swipefile": "Swipefile",
        "nav.settings": "Instellingen",
        "nav.language": "Taal",
        "app.tagline": "Advertenties die blijven draaien, geordend naar hook en angle.",
        "nav.appearance_hint": "Light/dark: menu rechtsboven → Settings → Appearance.",

        # Signaallabels — FO hoofdstuk 5
        "verdict.strong": "Sterk signaal",
        "verdict.mid": "Gemiddeld signaal",
        "verdict.weak": "Zwak signaal",

        # S1 Feed
        "feed.header": "Feed",
        "feed.empty": "Nog geen data. Voeg een zoekterm toe bij Instellingen en draai `python run_daily.py`.",
        "feed.filter.signal": "Signaal",
        "feed.filter.country": "Land",
        "feed.select_detail": "Bekijk advertentiedetail",
        "feed.col.advertiser": "adverteerder",
        "feed.col.verdict": "signaal",
        "feed.col.longevity": "longevity (dagen)",
        "feed.col.variants": "variatiedruk",
        "feed.col.copy": "copy",
        "feed.summary": "{total} advertenties · {strong} sterk · {mid} gemiddeld · {weak} zwak",
        "feed.no_match": "Geen advertenties met dit filter.",
        "feed.detail_header": "Advertentiedetail",

        # S2 Advertentiedetail
        "detail.no_copy": "_Geen copy in de brondata._",
        "detail.view_creative": "Bekijk creative in Ad Library",
        "detail.landing_page": "Landingspagina",
        "detail.unknown": "onbekend",
        "detail.active_since": "Actief sinds",
        "detail.metric.signal": "Signaal",
        "detail.metric.longevity": "Longevity (dagen)",
        "detail.metric.variants": "Variatiedruk",
        "detail.variants_caveat": (
            "Variatiedruk telt advertenties van dezelfde adverteerder naar dezelfde "
            "landingspagina — een benadering van 'zelfde angle', geen meting."
        ),

        # S4 Swipefile
        "swipefile.header": "Swipefile",
        "swipefile.save_title": "Opslaan in swipefile",
        "swipefile.hook": "Hook",
        "swipefile.angle": "Angle",
        "swipefile.format": "Format",
        "swipefile.note": "Notitie — waarom is dit interessant?",
        "swipefile.save": "Opslaan",
        "swipefile.saved": "Opgeslagen in swipefile.",
        "swipefile.empty": "Nog niets getagd. Tag advertenties vanuit het detailscherm in de Feed.",
        "swipefile.search": "Zoeken in hook, angle, format of notitie",
        "swipefile.col.tagged_at": "getagd op",
        "swipefile.col.note": "notitie",

        # S7 Dashboard
        "dash.header": "Dashboard",
        "dash.empty": "Nog geen data. Voeg een zoekterm toe bij Instellingen en draai `python run_daily.py`.",
        "dash.kpi.ads": "Advertenties gevolgd",
        "dash.kpi.advertisers": "Adverteerders",
        "dash.kpi.tagged": "Getagd in swipefile",
        "dash.kpi.freshness": "Dagen sinds laatste ophaling",
        "dash.kpi.freshness_never": "nooit",
        "dash.distribution": "Verdeling van het signaal",
        "dash.longevity": "Verdeling van longevity",
        "dash.longevity_axis": "Dagen actief",
        "dash.longevity_count": "Aantal advertenties",
        "dash.trend": "Sterke signalen over tijd",
        "dash.trend_need_days": "Nog te weinig ophaaldagen voor een verloop. Dit verschijnt zodra er twee dagen gemeten zijn.",
        "dash.trend_axis": "Ophaaldag",
        "dash.source_health": "Bronstatus",
        "dash.stale_warning": "Laatste geslaagde ophaling is {days} dagen oud. Een onderbroken reeks tast de longevity-berekening aan — controleer of het toegangstoken nog geldig is.",
        "dash.never_fetched": "Nog geen geslaagde ophaling.",
        "dash.caveat": "Alle cijfers zijn tellingen uit de eigen database, geen schattingen. Longevity komt uit de startdatum van de advertentie; het signaal is een filter, geen voorspelling.",

        # S6 Instellingen
        "settings.header": "Instellingen",
        "settings.queries_title": "Gevolgde zoektermen",
        "settings.niche": "Niche",
        "settings.term": "Zoekterm",
        "settings.country": "Land (ISO-code, bijv. NL)",
        "settings.add": "Toevoegen",
        "settings.delete_select": "Verwijderen",
        "settings.delete": "Verwijder zoekterm",
        "settings.source_title": "Bronstatus",
        "settings.source_empty": "Nog geen ophalingen gedaan.",
        "settings.col.last_ok": "laatste geslaagd",
        "settings.col.last_attempt": "laatste poging",
    },
    "en": {
        # Navigation
        "app.title": "Swipedesk",
        "nav.screen": "Screen",
        "nav.dashboard": "Dashboard",
        "nav.feed": "Feed",
        "nav.swipefile": "Swipefile",
        "nav.settings": "Settings",
        "nav.language": "Language",
        "app.tagline": "Ads that keep running, organised by hook and angle.",
        "nav.appearance_hint": "Light/dark: top-right menu → Settings → Appearance.",

        # Signal labels — FO chapter 5
        "verdict.strong": "Strong signal",
        "verdict.mid": "Medium signal",
        "verdict.weak": "Weak signal",

        # S1 Feed
        "feed.header": "Feed",
        "feed.empty": "No data yet. Add a search term under Settings and run `python run_daily.py`.",
        "feed.filter.signal": "Signal",
        "feed.filter.country": "Country",
        "feed.select_detail": "View ad detail",
        "feed.col.advertiser": "advertiser",
        "feed.col.verdict": "signal",
        "feed.col.longevity": "longevity (days)",
        "feed.col.variants": "variant pressure",
        "feed.col.copy": "copy",
        "feed.summary": "{total} ads · {strong} strong · {mid} medium · {weak} weak",
        "feed.no_match": "No ads match this filter.",
        "feed.detail_header": "Ad detail",

        # S2 Ad detail
        "detail.no_copy": "_No copy in the source data._",
        "detail.view_creative": "View creative in Ad Library",
        "detail.landing_page": "Landing page",
        "detail.unknown": "unknown",
        "detail.active_since": "Active since",
        "detail.metric.signal": "Signal",
        "detail.metric.longevity": "Longevity (days)",
        "detail.metric.variants": "Variant pressure",
        "detail.variants_caveat": (
            "Variant pressure counts ads from the same advertiser pointing to the same "
            "landing page — an approximation of 'same angle', not a measurement."
        ),

        # S4 Swipefile
        "swipefile.header": "Swipefile",
        "swipefile.save_title": "Save to swipefile",
        "swipefile.hook": "Hook",
        "swipefile.angle": "Angle",
        "swipefile.format": "Format",
        "swipefile.note": "Note — why is this interesting?",
        "swipefile.save": "Save",
        "swipefile.saved": "Saved to swipefile.",
        "swipefile.empty": "Nothing tagged yet. Tag ads from the detail screen in the Feed.",
        "swipefile.search": "Search hook, angle, format or note",
        "swipefile.col.tagged_at": "tagged at",
        "swipefile.col.note": "note",

        # S7 Dashboard
        "dash.header": "Dashboard",
        "dash.empty": "No data yet. Add a search term under Settings and run `python run_daily.py`.",
        "dash.kpi.ads": "Ads tracked",
        "dash.kpi.advertisers": "Advertisers",
        "dash.kpi.tagged": "Tagged in swipefile",
        "dash.kpi.freshness": "Days since last fetch",
        "dash.kpi.freshness_never": "never",
        "dash.distribution": "Signal distribution",
        "dash.longevity": "Longevity distribution",
        "dash.longevity_axis": "Days active",
        "dash.longevity_count": "Number of ads",
        "dash.trend": "Strong signals over time",
        "dash.trend_need_days": "Not enough fetch days for a trend yet. This appears once two days have been measured.",
        "dash.trend_axis": "Fetch day",
        "dash.source_health": "Source status",
        "dash.stale_warning": "Last successful fetch is {days} days old. A broken series degrades the longevity calculation — check whether the access token is still valid.",
        "dash.never_fetched": "No successful fetch yet.",
        "dash.caveat": "All figures are counts from the local database, not estimates. Longevity comes from the ad's start date; the signal is a filter, not a prediction.",

        # S6 Settings
        "settings.header": "Settings",
        "settings.queries_title": "Tracked search terms",
        "settings.niche": "Niche",
        "settings.term": "Search term",
        "settings.country": "Country (ISO code, e.g. NL)",
        "settings.add": "Add",
        "settings.delete_select": "Delete",
        "settings.delete": "Delete search term",
        "settings.source_title": "Source status",
        "settings.source_empty": "No fetches performed yet.",
        "settings.col.last_ok": "last successful",
        "settings.col.last_attempt": "last attempt",
    },
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    return TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS[DEFAULT_LANG].get(key, key)
