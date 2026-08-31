# Swipedesk

Persoonlijke tool om winnende advertenties uit officiële ad-libraries (Meta, TikTok) te verzamelen, te ordenen naar hook/angle/format, en om te zetten in bruikbare creative briefs voor de eigen webshop.

## Documenten

- [Functioneel ontwerp](docs/functioneel-ontwerp.md) — waarom, voor wie, het signaalmodel, databronnen, fasering, bekende risico's.
- [Technisch ontwerp](docs/technisch-ontwerp.md) — stack (Python + SQLite + Streamlit), datamodel, acquisitiepipeline, projectstructuur.

## Status

Fase 1 (MVP) is opgezet: datamodel, acquisitiepipeline, signaal-engine en de vier schermen uit TO hoofdstuk 7 draaien. Nog te doen voordat er echte data in staat: een Meta developer-app met een Ad Library-token (TO hoofdstuk 12).

Fase 0 — de handmatige validatie van het signaalmodel (FO hoofdstuk 9) — staat nog open. De drempelwaarden in `signal_engine.py` zijn tot die tijd aannames, geen gekalibreerde waarden.

> **Blokkerende open keuze: de markt.** Meta's Ad Library levert commerciële advertenties alleen als ze de EU bereikten; daarbuiten uitsluitend politieke advertenties. Verkoop je niet in of naar de EU, dan is deze bron leeg en moet FO hoofdstuk 6 herzien worden vóórdat er verder gebouwd wordt. Zie FO hoofdstuk 6 en 11.

## Aan de slag

```bash
python -m venv .venv && .venv/Scripts/python.exe -m pip install -r requirements.txt
```

Kopieer `.env.example` naar `.env` en vul het Meta-token in. Daarna:

```bash
.venv/Scripts/python.exe run_daily.py
```

Dit draait fetch → parse → signal en is het cron-doelwit voor de dagelijkse verversing. De interface start met:

```bash
.venv/Scripts/python.exe -m streamlit run app.py
```

Zoektermen voeg je toe in de app onder Instellingen; zonder zoekterm haalt `run_daily.py` niets op.

## Tests

```bash
.venv/Scripts/python.exe -m pytest tests/
```

## Interface

Nederlands en Engels, te wisselen in de zijbalk; alle teksten staan als sleutel in `i18n.py`. Light en dark mode volgen je systeeminstelling en zijn te wisselen via het menu rechtsboven onder Settings → Appearance.
