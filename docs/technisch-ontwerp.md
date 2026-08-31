# Swipedesk — Technisch Ontwerp

**Concept v0.1 · 31 augustus 2026**
Scope: fase 1 MVP uit het FO (`functioneel-ontwerp.md`). Nog niets gebouwd.

De technische invulling van het FO: hoe fase 1 — één bron, één niche, één deadline — daadwerkelijk gebouwd wordt, zonder infrastructuur voor te bereiden op een schaal die er nog niet is.

---

## Inhoud

1. [Scope van dit TO](#1-scope-van-dit-to)
2. [Techniekkeuze](#2-techniekkeuze)
3. [Architectuur](#3-architectuur)
4. [Datamodel](#4-datamodel)
5. [Acquisitiepipeline](#5-acquisitiepipeline)
6. [Signaal-engine](#6-signaal-engine)
7. [Schermen → implementatie](#7-schermen--implementatie)
8. [Projectstructuur](#8-projectstructuur)
9. [Configuratie & secrets](#9-configuratie--secrets)
10. [Validatie tegen fase 0](#10-validatie-tegen-fase-0)
11. [Wat bewust buiten scope blijft](#11-wat-bewust-buiten-scope-blijft)
12. [Open technische keuzes](#12-open-technische-keuzes)

---

## 1. Scope van dit TO

Dit document werkt alleen fase 1 uit het FO (hoofdstuk 9) technisch uit: één bron, één niche, één deadline. Fase 2-functionaliteit wordt genoemd waar de architectuur er nu al rekening mee moet houden (hoofdstuk 11), maar niet gebouwd.

| Module (FO hfst. 4) | In dit TO | Reden |
|---|---|---|
| F1 Advertentiefeed | ✅ Ja | MVP, hoofdstuk 7 |
| F2 Advertentiedetail | ✅ Ja | MVP, hoofdstuk 7 |
| F3 Signaal-engine | ✅ Ja | MVP, hoofdstuk 6 |
| F4 Concurrent-tracking | 🟡 Datamodel wel, UI niet | Draait op dezelfde snapshots als F3 — los toevoegen in fase 2 kost dan geen migratie |
| F5 Tagging & swipefile | ✅ Ja | MVP, hoofdstuk 7 |
| F6 Briefgenerator + testpaar | ❌ Nee | Fase 2, FO hoofdstuk 9 |
| F7 Landingspagina-teardown | ❌ Nee | Fase 2 |
| F8 Bronbeheer | ✅ Ja, minimaal | MVP, hoofdstuk 7 |
| F9 Instellingen | ✅ Ja, minimaal | MVP, hoofdstuk 7 |

## 2. Techniekkeuze

Dit lost de open vraag uit FO hoofdstuk 11 ("Laravel of iets lichters") op. Vier beslissingen, met de reden erbij — niet als losse voorkeur maar als iets dat uit de aard van de opgave volgt.

**Taal — Python 3.12**, niet Laravel/PHP.
> Het zwaartepunt van fase 1 is API-ophaling en signaalberekening, geen webapplicatie met gebruikersbeheer. Python heeft daarvoor de kortste weg naar werkende code, en sluit aan op de toolkeuzes die Kansenradar hoofdstuk 6b al voor eventuele latere scrapers vastlegde — één taal voor beide gepauzeerde/actieve projecten.

**Opslag — SQLite**, één bestand.
> Eén gebruiker, een paar duizend advertenties. Postgres opzetten voor die schaal is voorbereiden op een fase 3 die misschien nooit komt — exact het patroon dat het FO afraadt. Migratiepad naar Postgres is triviaal mocht fase 3 ooit werkelijkheid worden.

**Interface — Streamlit**, geen apart front-end/back-end.
> Feed met filters, een detailweergave en een tag-formulier zijn precies waar Streamlit voor bestaat: een intern data-hulpmiddel voor één gebruiker, zonder authenticatielaag te hoeven bouwen die hier geen functie heeft (FO hoofdstuk 2: één gebruiker, geen rollen).

**Planning — Cron** (of Taakplanner), geen jobqueue.
> Eén dagelijkse taak die een script aanroept. Celery of Airflow invoeren voor één dagelijkse taak is infrastructuur bouwen voor een probleem dat er niet is.

> **Consequentie:** dit draait volledig lokaal, op één laptop of een goedkope VPS, met één `requirements.txt` en geen container-orkestratie. Wie dit leest en een reden zoekt om Docker, Kubernetes of een message queue toe te voegen: dat is hoofdstuk 10 van het FO (scope creep) in actie.

## 3. Architectuur

Vier stappen, strikt gescheiden zoals FO hoofdstuk 6b voorschrijft: ophalen en interpreteren zijn nooit dezelfde functie.

```
Meta Ad Library API
        │
        ▼
   fetch.py  (dagelijks, cron)
        │
        ▼
  raw_responses  (SQLite, onveranderlijk)
        │
        ▼
  parse.py + signal_engine.py
        │
        ▼
  ads, signals, tags  (SQLite)
        │
        ▼
  app.py — Streamlit UI
```

`fetch.py` raakt alleen de API en het onveranderlijke ruwe archief. `parse.py` en `signal_engine.py` lezen dat archief en schrijven de genormaliseerde tabellen. `app.py` leest uitsluitend die tabellen — de Streamlit-interface roept nooit rechtstreeks de Meta API aan.

## 4. Datamodel

Zes tabellen. `ad_snapshots` is bewust een eigen tabel en geen kolom op `ads`: longevity is af te leiden uit een reeks dagelijkse waarnemingen, en dezelfde reeks is precies wat F4 (concurrent-tracking, fase 2) straks nodig heeft. Die tabel nu al goed neerzetten voorkomt een migratie later.

| Tabel | Kernvelden | Doel |
|---|---|---|
| `tracked_queries` | id, niche, term, platform, land | F9 — wat wordt er dagelijks opgehaald (instellingen) |
| `raw_responses` | id, query_id, fetched_at, payload (JSON), status | Onveranderlijk archief van elke API-aanroep, nooit overschreven |
| `advertisers` | id, meta_page_id, name | Eén rij per adverteerder, basis voor variatiedruk |
| `ads` | id, advertiser_id, meta_ad_id, landing_url, format, first_seen, copy_text, creative_url | Eén rij per advertentie, genormaliseerd uit raw_responses |
| `ad_snapshots` | ad_id, observed_on, is_active | Eén rij per advertentie per ophaaldag — basis voor longevity én voor F4 straks |
| `signals` | ad_id, computed_on, longevity_days, variant_count, verdict | Uitkomst van signal_engine.py, herberekend bij elke run |
| `tags` | ad_id, hook, angle, format, note, tagged_at | F5 — swipefile |

> **Bewuste keuze:** `signals` wordt bij elke dagelijkse run volledig herberekend, niet incrementeel bijgewerkt. Bij deze schaal (één niche, dagelijks) is het verschil in rekentijd verwaarloosbaar, en herberekenen voorkomt een hele klasse van bugs waarbij een oude waarde blijft hangen.

## 5. Acquisitiepipeline

Concrete invulling van FO hoofdstuk 6b. Eén dagelijkse cron-taak, één commando, vier stappen op een rij:

```python
# 1. fetch — raakt alleen de API, schrijft alleen raw_responses
for query in tracked_queries:
    response = meta_ad_library.search(query.term, query.land)
    save_raw(query.id, fetched_at=now(), payload=response, status="ok")
    # bij fout: status="failed", geen crash van de hele run

# 2. parse — leest alleen raw_responses van vandaag, schrijft ads + ad_snapshots
for raw in raw_responses.today():
    for item in raw.payload["ads"]:
        ad = upsert_ad(item)                 # bestaat al? bijwerken; nieuw? aanmaken
        upsert_advertiser(item.page_id, item.page_name)
        record_snapshot(ad.id, observed_on=today(), is_active=True)

mark_missing_ads_inactive(seen_today=parsed_ad_ids)  # niet gezien = gestopt

# 3. signal — leest ads + ad_snapshots, schrijft signals
for ad in ads.all():
    longevity = days_since_delivery_start(ad)   # zie noot hieronder
    variants  = count_active_ads(advertiser_id=ad.advertiser_id,
                                  landing_url=ad.landing_url)   # proxy voor "zelfde angle"
    verdict   = classify(longevity, variants)                   # hoofdstuk 6
    save_signal(ad.id, longevity, variants, verdict)

# 4. klaar — app.py leest alleen de tabellen hierboven, roept nooit de API aan
```

### Waarom longevity uit de API komt, niet uit de eigen waarnemingen

Longevity tellen als "aantal opeenvolgende dagen dat wij de advertentie actief zagen"
klinkt zuiverder, maar maakt het MVP bij oplevering leeg: de drempel voor een sterk
signaal ligt op 45 dagen, dus de tool zou anderhalve maand moeten draaien voordat er
één sterk signaal kán verschijnen. De Ad Library levert `ad_delivery_start_time` mee,
dus longevity is `vandaag - startdatum` zolang de advertentie vandaag actief is, en 0
zodra hij niet meer wordt gezien.

`ad_snapshots` blijft onverkort nodig: die reeks bepaalt of een advertentie vandaag
nog actief is, en is straks de basis voor F4 (concurrent-tracking) — het moment van
stoppen zien, dat volgens FO hoofdstuk 5 net zo veel zegt als het signaal zelf.

### Waarom "zelfde landingspagina" als proxy voor "zelfde angle"

Echte angle-clustering (twee advertenties herkennen als dezelfde onderliggende belofte, ook met andere bewoordingen) is een tekstclassificatieprobleem dat een eigen validatieronde verdient. Voor fase 1 is **dezelfde adverteerder + dezelfde landingspagina-URL** een goedkope, eerlijke benadering: verschillende creatives die naar dezelfde pagina leiden, verkopen vrijwel altijd dezelfde onderliggende belofte. Dit is een bewuste vereenvoudiging, geen definitieve aanname — zichtbaar te maken in de UI (hoofdstuk 7) zodat het nooit als meer voorkomt dan het is.

### Foutafhandeling

Elke stap is idempotent: opnieuw draaien voor dezelfde dag overschrijft, dupliceert niet. Als `fetch` voor één query faalt (rate limit, API-storing), gaat de run door met de overige queries en blijven de signals van de vorige dag intact — conform de degradatie-eis uit FO hoofdstuk 8: zichtbaar minder dekking, geen crash en geen stille leegte.

## 6. Signaal-engine

Direct uit FO hoofdstuk 5, nu als concrete classificatieregel:

| Signaal | Regel |
|---|---|
| **Sterk signaal** | `longevity_days >= 45 && variant_count >= 3` |
| **Gemiddeld signaal** | `(longevity_days >= 45) != (variant_count >= 3)` — precies één van de twee waar |
| **Zwak signaal** | `longevity_days < 45 && variant_count < 3` |

De drempelwaarden (45 dagen, drie varianten) zijn de gekalibreerde gewichten uit fase 0 (FO hoofdstuk 9) — hardcoded als configuratiewaarden, niet als losse instelling in de UI. Aanpassen kan, maar hoort in code te gebeuren zodat elke wijziging traceerbaar is in de git-historie.

> **Implementatie-eis uit FO R4:** de UI toont `strong / mid / weak` als label, nooit als percentage of getal. `verdict` is een `enum` in de database, geen `float` — dat voorkomt dat een toekomstige UI-wijziging per ongeluk een schijnprecieze score laat zien.

## 7. Schermen → implementatie

FO hoofdstuk 7 beschrijft zes schermen; dit TO bouwt er vier in fase 1 (S1, S2, S4, S6). S3 (concurrent-tracker) en S5 (brief) zijn fase 2.

- **S1 Feed** — één Streamlit-pagina: `st.dataframe` over `signals JOIN ads`, gesorteerd op `verdict, longevity_days`. Filters in de zijbalk (`st.sidebar.multiselect`) op format en land.
- **S2 Advertentiedetail** — bij het selecteren van een rij: creative-afbeelding of video, volledige copy, en de onderbouwing van het signaal — `longevity_days` en `variant_count` expliciet naast elkaar, nooit alleen het label.
- **S4 Swipefile** — formulier (`st.form`) met vrije-tekstvelden voor hook/angle/format en een notitie, schrijft naar `tags`. Aparte pagina toont alle getagde items, doorzoekbaar op tekst.
- **S6 Instellingen** — CRUD op `tracked_queries` — niche, zoekterm, land toevoegen of verwijderen. Rechtstreeks tegen de tabel, geen aparte configuratielaag.

### Taal en vormgeving

- **Taal** — alle UI-tekst staat als sleutel in `i18n.py` (nl/en), nooit inline in `app.py`. Een test bewaakt dat beide talen dezelfde sleutels hebben, zodat een vergeten vertaling niet pas in de UI opvalt. De taalkeuze staat in de zijbalk.
- **Light/dark** — `.streamlit/config.toml` definieert aparte `[theme.light]`- en `[theme.dark]`-paletten; Streamlit volgt standaard de systeeminstelling en biedt de wissel in zijn eigen menu. `styles.py` leest de actieve modus via `st.context.theme` en injecteert het bijpassende palet, zodat de eigen componenten (signaalbadges, copy-blok) meebewegen in plaats van in één modus vast te zitten.
- **Signaalkleuren** — drie categorische kleuren (groen/amber/grijs), geen verloop. Een verloop zou opnieuw de precisie suggereren die FO hoofdstuk 5 juist afwijst.

## 8. Projectstructuur

```
swipedesk/
├─ app.py                 # Streamlit-app, entrypoint voor de UI
├─ i18n.py                # vertaalsleutels (nl/en) — geen UI-tekst inline
├─ styles.py              # thema-palet en CSS voor light/dark
├─ fetch.py               # stap 1: Meta Ad Library API → raw_responses
├─ parse.py               # stap 2: raw_responses → ads, advertisers, ad_snapshots
├─ signal_engine.py       # stap 3: signaal-engine (hoofdstuk 6)
├─ run_daily.py           # roept fetch → parse → signal na elkaar aan; cron-target
├─ db.py                  # SQLite-verbinding en schema-migraties
├─ schema.sql             # tabeldefinities (hoofdstuk 4)
├─ .streamlit/
│  └─ config.toml         # Streamlit-thema, aparte light- en dark-paletten
├─ data/
│  ├─ swipedesk.db        # SQLite-bestand, niet in git
│  └─ raw/                # optioneel: ruwe payloads ook als losse JSON-bestanden
├─ tests/
│  ├─ test_signal_engine.py  # signaal-engine tegen de fase-0-validatieset (hoofdstuk 10)
│  └─ test_i18n.py           # bewaakt dat beide talen dezelfde sleutels hebben
├─ docs/
│  ├─ functioneel-ontwerp.md
│  └─ technisch-ontwerp.md
├─ .env.example
├─ .gitignore             # data/, .env
├─ requirements.txt
└─ README.md
```

Geen `src/`-laag, geen packages, geen classes waar functies volstaan. Bij deze omvang (één bron, vier scripts) voegt structuur boven dit niveau alleen navigatiekosten toe.

## 9. Configuratie & secrets

```
# .env.example
META_AD_LIBRARY_ACCESS_TOKEN=
META_AD_LIBRARY_APP_ID=
DB_PATH=./data/swipedesk.db
```

- **Toegangstoken** — vereist een Meta developer-app; de exacte verificatie-eisen voor de Ad Library API wisselen per periode en worden bij de start van fase 1 geverifieerd, niet aangenomen (dit is FO B1: kip-ei op toegang).
- **Niets van bovenstaande wordt gecommit.** `.env` staat in `.gitignore`; alleen `.env.example` met lege waarden gaat mee in git.
- **Gevolgde niches** staan in de database (`tracked_queries`), niet in een configuratiebestand — zo blijven ze via S6 aanpasbaar zonder herstart.

## 10. Validatie tegen fase 0

FO fase 0 (hoofdstuk 9) levert een handmatig doorzochte lijst van tien tot vijftien advertenties met een eigen inschatting van sterk/gemiddeld/zwak. Die lijst wordt de eerste testset: `tests/test_signal_engine.py` voert dezelfde advertenties met hun daadwerkelijke `longevity` en `variant_count` door `signal_engine.py` en vergelijkt de uitkomst met de handmatige inschatting.

Dit is geen automatisering van fase 0 — het is de brug die aantoont dat de code hetzelfde model implementeert als de spreadsheet, vóórdat de fase-1-deadline erop vertrouwt.

## 11. Wat bewust buiten scope blijft

- **F4-UI (concurrent-tracking)** — het datamodel (`ad_snapshots`) ondersteunt het al; alleen het scherm dat verschillen tussen twee dagen toont, ontbreekt nog.
- **F6 briefgenerator + testpaar-logging** — vereist een gekoppeld eigen Ads Manager-account, dat er in fase 1 per definitie nog niet is.
- **F7 landingspagina-teardown** — aparte scraper/archiveringslaag, fase 2.
- **TikTok als tweede bron** — het `raw_responses`-schema is bron-agnostisch (bevat al een `query_id` met platform), dus toevoegen is een nieuwe `fetch_tiktok.py`, geen schemawijziging.
- **Authenticatie, multi-user, deployment achter een domein** — niet totdat FO fase 3 ooit werkelijkheid wordt.

## 12. Open technische keuzes

| Vraag | Toelichting |
|---|---|
| **API-toegang** | Meta developer-app aanmaken en verifiëren staat niet in dit TO als afgerond — eerste concrete actie bij de start van fase 1, met een tijdsinschatting die pas na het aanvraagproces bekend is. |
| **Waar draait de cron** | Lokale laptop (moet dan aanstaan op het geplande moment) versus een goedkope VPS (€5–6/mnd, altijd aan). *Voorstel: VPS* — voorkomt gemiste dagen door een uitgeschakelde laptop, wat longevity-berekeningen zou verstoren. |
| **Streamlit-toegang** | Alleen lokaal bereikbaar (`localhost`) of ook van buitenaf (bijv. via Tailscale) om de feed ook op de telefoon te bekijken? Geen blokkerende keuze, later toe te voegen. |
| **Repository** | ✅ Opgelost: `eva-ster/swipedesk`. |
