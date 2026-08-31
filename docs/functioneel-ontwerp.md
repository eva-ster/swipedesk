# Swipedesk — Functioneel Ontwerp

**Concept v0.3 · 31 augustus 2026**
Status: fase 1 gebouwd, nog geen echte data. Voor eigen gebruik. Werktitel.

> **v0.3 — dekking gecorrigeerd.** Hoofdstuk 6 stelde dat de Meta Ad Library API geen EU-beperking kent. Dat is bij Meta geverifieerd en onjuist: commerciële advertenties komen alleen terug als ze de EU bereikten. Hoofdstuk 5, 6, 10 (risico 03) en 11 zijn daarop bijgesteld. Gevolg: de markt is een blokkerende keuze geworden en staat nu boven de niche in hoofdstuk 11.

Een persoonlijk onderzoeksarchief van advertenties die aantoonbaar lang blijven draaien — zodat hooks, angles en formats die elders al werken de basis worden van de eigen eerste advertentie, in plaats van een leeg canvas.

**Relatie tot Kansenradar:** Kansenradar (gepauzeerd, apart document) beantwoordt "welk product". Dit document beantwoordt "hoe verkoop ik het" — op basis van de conclusie dat creative en marketinguitvoering meer van het resultaat bepalen dan productkeuze.

---

## Inhoud

1. [Waarom dit product](#1-waarom-dit-product)
2. [Voor wie](#2-voor-wie)
3. [Kernbegrippen](#3-kernbegrippen)
4. [Functionele modules](#4-functionele-modules)
5. [Het signaalmodel](#5-het-signaalmodel)
6. [Databronnen](#6-databronnen)
7. [6b. Data-acquisitie](#6b-data-acquisitie)
8. [Schermen en flows](#7-schermen-en-flows)
9. [Randvoorwaarden](#8-randvoorwaarden)
10. [Fasering](#9-fasering)
11. [Bottlenecks & pre-mortem](#10-bottlenecks--pre-mortem)
12. [Open keuzes](#11-open-keuzes)

---

## 1. Waarom dit product

De vorige twee sessies concludeerden hetzelfde vanuit twee richtingen: productkeuze is niet de bottleneck van e-commerce. Winnaars winnen op creative, aanbod, marge en uitvoeringssnelheid. Wie voor het eerst gaat adverteren, begint met een leeg canvas: geen hook die werkt, geen angle die aanslaat, geen gevoel voor welk format — UGC, studio, statisch — bij het product past.

Tegelijk staat het antwoord grotendeels publiek open. Meta en TikTok zijn wettelijk verplicht om actieve advertenties doorzoekbaar te maken. Een advertentie die weken- of maandenlang blijft draaien, is met hoge waarschijnlijkheid winstgevend — niemand betaalt lang voor iets dat niet rendeert. Die informatie bestaat, maar is nu alleen met de hand en zonder structuur te doorzoeken.

### Wat de tool doet

- **Verzamelt** actieve advertenties per niche of concurrent uit officiële ad-libraries, met hoelang ze al draaien.
- **Signaleert** welke advertenties waarschijnlijk winnen — op basis van looptijd en variatie, niet op basis van geschat budget, want dat cijfer bestaat voor commerciële advertenties grotendeels niet (hoofdstuk 5).
- **Ordent** gevonden advertenties naar hook, angle en format in een doorzoekbaar eigen archief.
- **Levert een brief op**: een concreet, bruikbaar startpunt voor de eigen advertentie, gebaseerd op patronen die elders al werken.

### Wat de tool niet is

- Geen advertentie-uitgaventracker. Dat cijfer is voor de meeste advertenties niet publiek; wat de tool toont is een aflopende benadering, geen meting.
- Geen kopieermachine. Het doel is patroonherkenning — welke hoek, welke belofte, welk format — niet het overnemen van een specifieke advertentie (hoofdstuk 10).
- Geen advertentiebeheertool. De tool eindigt bij de brief; het plaatsen en optimaliseren van de eigen advertentie gebeurt in Meta/TikTok Ads Manager zelf.

## 2. Voor wie

Net als Kansenradar is dit vanaf dag één een persoonlijke tool, geen product voor anderen. Die keuze staat hier niet opnieuw ter discussie; wat wel verschilt is welke rol op welk moment actief is.

**Rol A — Eerste advertentie**
Nog geen shop, nog nooit geadverteerd. Kernvraag: *met welke hoek begin ik, en in welk format?* Prioriteit ligt bij volume aan voorbeelden binnen één niche, niet bij precisie.

**Rol B — Lopende campagne**
Er draait al een advertentie en de resultaten lopen terug (creative fatigue, hoofdstuk 5). Kernvraag: *welke variatie ververst de hoek zonder het werkende aanbod te verlaten?* Prioriteit ligt bij concurrent-tracking (F4) en snel nieuwe varianten vinden.

> **Ontwerpgevolg:** geen accounts, geen quota, geen rollen-laag. Rol A en Rol B zijn twee gebruiksmomenten van dezelfde persoon, geen aparte gebruikers — net als bij Kansenradar is dit een reden om de tool klein te houden, niet om hem uit te breiden.

## 3. Kernbegrippen

| Begrip | Betekenis |
|---|---|
| **Advertentie-item** | Eén specifieke advertentie zoals geregistreerd in een ad-library: creative, copy, actief-sinds datum, platform(en), land(en) en adverteerder. |
| **Longevity** | Aantal dagen dat een advertentie ononderbroken actief staat. De kernmaat van dit model, omdat directe prestatiedata (spend, CTR, ROAS) voor commerciële advertenties nergens openbaar is — ook niet in de EU, waar alleen bereik beschikbaar is (hoofdstuk 5). |
| **Variatiedruk** | Aantal gelijktijdig actieve advertenties van dezelfde adverteerder met dezelfde onderliggende angle. Adverteerders testen alleen door te schalen wat al werkt — veel varianten van hetzelfde idee is zelf een signaal. |
| **Angle** | De onderliggende belofte of het probleem dat de advertentie aanspreekt (bijvoorbeeld "bespaar tijd" versus "los pijn op") — losstaand van de specifieke formulering. |
| **Hook** | De eerste twee tot drie seconden video of de eerste regel tekst: het element dat bepaalt of iemand doorkijkt. |
| **Format** | De productievorm: UGC-stijl, studio-productie, statische afbeelding, carrousel of tekst-op-achtergrond. |
| **Swipe-item** | Een advertentie-item dat handmatig is opgeslagen en getagd in het eigen archief, met een notitie waarom het interessant is. |
| **Creative fatigue** | Het punt waarop een advertentie, ondanks langdurig succes, in prestatie terugloopt — de reden dat zelfs winnende advertenties op den duur vervangen moeten worden (hoofdstuk 5). |
| **Brief** | Het exporteerbare eindproduct: hoek, angle, format en drie referentievoorbeelden, samengevat tot een bruikbaar startpunt voor een eigen advertentie. |
| **Testpaar** | Twee varianten van dezelfde brief die op precies één dimensie verschillen — bijvoorbeeld dezelfde angle met twee hooks, of dezelfde hook in twee formats. Draait als test via Meta Experiments of TikTok Smart+; het resultaat wordt na afloop teruggelogd (hoofdstuk 9, fase 2). |

## 4. Functionele modules

Negen modules, in dezelfde opzet als Kansenradar: de status geeft aan of iets in het MVP zit, de laatste regel is de belangrijkste functionele regel.

### F1 — Advertentiefeed `MVP`
Doorzoekbare lijst van actieve advertenties per niche, zoekterm of concurrent, met longevity en variatiedruk als primaire sortering.
> Standaard gesorteerd op longevity, niet op datum toegevoegd — nieuw is niet hetzelfde als relevant.

### F2 — Advertentiedetail `MVP`
Creative, volledige copy, platform, land, actief-sinds datum en het afgeleide signaal (hoofdstuk 5) met de onderliggende berekening zichtbaar.
> Elk signaal is herleidbaar naar de brondata waarop het rust. Geen zwarte doos.

### F3 — Signaal-engine `MVP`
Berekent longevity en variatiedruk per advertentie en adverteerder, en wijst het categorische signaal toe (zwak/gemiddeld/sterk — hoofdstuk 5).
> Geen numerieke score. Waar de brondata een schatting is, oogt een getal preciezer dan gerechtvaardigd.

### F4 — Concurrent-tracking `MVP`
Specifieke advertentiepagina's volgen: nieuwe launches, gestopte advertenties en verschuivingen in variatiedruk sinds de vorige controle.
> Een advertentie die stopt terwijl de rest van de pagina doorloopt, is zelf een signaal — dat wordt getoond, niet verborgen.

### F5 — Tagging & swipefile `MVP`
Advertentie-items opslaan met eigen tags voor hook, angle en format, doorzoekbaar archief van eigen bevindingen.
> Tags zijn vrije tekst met suggesties uit eerdere tags — geen vaste taxonomie die de eerste maanden toch verkeerd blijkt.

### F6 — Briefgenerator `Fase 2`
Zet een selectie getagde swipe-items om in een concrete brief: hoek, angle, format en drie referenties, als startpunt voor een eigen script of creative-opdracht. Kan een brief ook als testpaar opleveren — twee varianten die op één dimensie verschillen, bedoeld om tegen elkaar te draaien in plaats van één variant blind te kiezen.
> Genereert een startpunt, geen eindproduct — altijd met de bronvoorbeelden ernaast, nooit als vervanging ervan. Zet zelf geen test op; dat gebeurt in Meta Experiments of TikTok Smart+.

### F7 — Landingspagina-teardown `Fase 2`
Aanbod, garantie, urgentie en bundelopbouw van de landingspagina achter een geselecteerde advertentie, naast elkaar gelegd met eigen aannames.
> Beschrijft opbouw en structuur, kopieert geen tekst of vormgeving.

### F8 — Bronbeheer `MVP`
Status en dekking per bron: laatste geslaagde ophaling, welke landen en platforms daadwerkelijk gedekt zijn.
> Valt een bron weg, dan wordt dat zichtbaar in de feed — niet stilletjes minder resultaten zonder verklaring.

### F9 — Instellingen `MVP`
Gevolgde niches, concurrenten en zoektermen; lokale voorkeuren voor platform en land.
> Eén gebruiker, dus geen accountlaag — dit zijn lokale instellingen, geen multi-tenant configuratie.

## 5. Het signaalmodel

De kern van dit hele document zit hier: er is geen betrouwbare spend- of prestatiedata voor commerciële advertenties. Het model moet dus "waarschijnlijk winnend" afleiden uit wat wel publiek is — en moet daar eerlijk in zijn.

> **Nuance, toegevoegd 31 augustus 2026.** Voor advertenties die de EU bereikten levert de Ad Library wél `eu_total_reach`, plus een uitsplitsing naar leeftijd, geslacht en land. Dat is een meting, geen benadering, en daarmee een sterker signaal dan longevity. Het model hieronder blijft de basis — het moet werken zonder die velden, want een tweede bron levert ze niet — maar bereik hoort er als derde signaal bij zodra fase 1 aantoonbaar op EU-data draait. Spend blijft ontbreken: bereik zegt hoeveel mensen het zagen, niet wat het kostte of opleverde.

### Waarom geen score van 0 tot 100

Kansenradar gebruikte een gewogen index, met expliciete waarschuwing tegen schijnzekerheid (R4 in dat document). Hier is het onderliggende bewijs nog dunner: geen vijf pijlers met deels harde cijfers, maar twee indirecte signalen op een aanname. Een getal als "73" zou een precisie suggereren die er niet is. Daarom een categorisch signaal in drie niveaus in plaats van een continue score.

| Signaal | Voorwaarde |
|---|---|
| **Sterk signaal** | Longevity boven 45 dagen *én* variatiedruk van drie of meer gelijktijdige varianten. Beide signalen wijzen dezelfde kant op: een adverteerder die zo lang doorgaat *én* actief blijft testen binnen dezelfde angle, houdt vast aan iets dat aantoonbaar werkt. |
| **Gemiddeld signaal** | Slechts één van de twee signalen is sterk aanwezig. Bijvoorbeeld lange looptijd zonder variatie (kan set-and-forget zijn met bescheiden maar acceptabel resultaat) of veel variatie zonder lange looptijd (kan nog in een testfase zitten). |
| **Zwak signaal** | Korte looptijd en geen variatie. Kan een net gelanceerde test zijn, kan ook een advertentie zijn die simpelweg niet loopt — op dit niveau is het onderscheid met de brondata alleen niet te maken. |

> **Wat dit niet is:** een voorspelling van prestatie, laat staan een percentage. Een advertentie die lang draait ondanks matige resultaten — omdat de adverteerder het simpelweg niet controleert — bestaat, en de tool kan dat geval niet onderscheiden van een echte winnaar. Het signaal is een filter om sneller te zoeken, geen garantie.

### Creative fatigue: ook winnende advertenties verouderen

Een sterk signaal vandaag betekent niet dat de advertentie over twee maanden nog werkt. Naarmate dezelfde advertentie aan meer mensen herhaald wordt, daalt de respons — een bekend patroon in mediabuying. Dit is de reden dat Rol B (hoofdstuk 2) net zo belangrijk is als Rol A: ook een bestaande, werkende advertentie heeft op termijn een vervanger nodig.

Curve: lancering → schaal (respons stijgt) → **piekrespons** → vermoeidheid (respons daalt terwijl de advertentie nog "sterk" scoort op longevity) → uitgeput. De longevity die het signaal sterk maakt, is een terugblik: een advertentie die nu 45 dagen draait, kan zich al in de vermoeidheidszone bevinden. Dit is waarom concurrent-tracking (F4) — het moment van stoppen zien — net zo veel zegt als het signaal zelf.

## 6. Databronnen

Zelfde volgorde als bij Kansenradar: eerst officiële API, dan kant-en-klaar kopen, pas dan zelf iets bouwen. Het goede nieuws hier is dat de belangrijkste bron — de ad-library's — wettelijk verplicht en gratis toegankelijk is.

| Bron | Levert | Toegang | Beperking |
|---|---|---|---|
| Meta Ad Library API | Creative, copy, actief-sinds, platforms, landen; voor EU-advertenties ook `eu_total_reach` en targeting-uitsplitsing | Officieel, gratis; identiteitsverificatie met overheids-ID vereist | Commerciële advertenties alleen als ze de EU bereikten; geen spend |
| TikTok Commercial Content API | Zelfde als Meta, EU-only door de DSA-verplichting | Officieel, gratis | Dekking buiten de EU grotendeels leeg |
| Kant-en-klare spy-tools (PiPiads, BigSpy, Minea Ads, Foreplay) | Vaak een eigen engagement- of spend-proxy, TikTok Shop-specifiek | Betaald (€30–100/mnd) | Overlap — deels dezelfde brondata, maar met eigen verrijking die zelf bouwen niet snel evenaart |
| Landingspagina + Wayback Machine | Aanbod, garantie, historie van wijzigingen over tijd | Publiek, officieel archief-API | Stabiel — geen toegangsdrempel |
| Eigen Ads Manager (Meta/TikTok) | Echte CPA, ROAS, frequentie — pas zodra er zelf geadverteerd wordt | Officieel, eigen account | Enige echte metingsbron, zie hoofdstuk 9 fase 2 |

> **Gecorrigeerd 31 augustus 2026.** Een eerdere versie van dit hoofdstuk stelde dat de Meta Ad Library API "geen EU-beperking" heeft, en dat was de reden om Meta boven TikTok te kiezen. Dat klopt niet. Meta's eigen documentatie bij `ads_archive`: *"Ads that did not reach any location in the EU will only return if they are about social issues, elections or politics."* Commerciële advertenties zitten dus alleen in de API als ze de EU bereikten — dezelfde DSA-grond als bij TikTok, alleen ruimer in dekking.

> Voor het MVP is **één bron genoeg**: de Meta Ad Library API — mits er in of naar de EU verkocht wordt. Buiten de EU levert deze bron uitsluitend politieke en maatschappelijke advertenties op en is hij voor dit doel leeg. Voor een niet-EU markt verschuift risico 04 (een bestaande spy-tool huren) daarmee van bewust verworpen alternatief naar de realistische route; dat is dan een herziening van dit hoofdstuk, geen detail.

> **Wat wel overdraagbaar blijft:** de tool levert patronen — welke hoek, welke belofte, welk format — en die zijn grotendeels marktonafhankelijk. Ook wie buiten de EU verkoopt, heeft aan onderzoek op EU-advertenties wat. Wat dan ontbreekt is een betrouwbaar *signaal* over de eigen markt: de longevity die je ziet weerspiegelt Europese concurrentie en biedingen.

## 6b. Data-acquisitie

Lichter dan bij Kansenradar, want de hoofdbron is een officiële, gratis API zonder scraping. Wat overblijft aan aandacht:

- **Ruw opslaan, apart parsen** — zelfde patroon als Kansenradar hoofdstuk 6b: de ruwe API-respons onveranderlijk bewaren, interpretatie in een aparte stap. Als Meta het schema van de library wijzigt, is de historie te herparseren in plaats van kwijt.
- **Creative-assets bewaren** — afbeeldingen en video's downloaden voor het eigen swipefile-archief is voor persoonlijk onderzoek te verdedigen; nooit republiceren, doorverkopen of als eigen werk presenteren (zie hoofdstuk 10 voor de auteursrechtelijke grens).
- **Rate limits van de Ad Library API** — ruim binnen budget bij dagelijkse verversing van een handvol gevolgde niches en concurrenten; wordt pas relevant bij tientallen gevolgde pagina's tegelijk.
- **Spy-tools scrapen, indien later gekozen** — dan gelden dezelfde regels als bij Kansenradar: gebruiksvoorwaarden respecteren, geen ingelogde sessies gebruiken voor geautomatiseerd ophalen.

## 7. Schermen en flows

### Zes schermen

- **S1 Feed** — doorzoekbare advertentielijst, gesorteerd op signaal.
- **S2 Advertentiedetail** — creative, copy, signaal met onderbouwing.
- **S3 Concurrent-tracker** — gevolgde pagina's met verschuiving sinds vorige controle.
- **S4 Swipefile** — eigen getagd archief, doorzoekbaar op hook/angle/format.
- **S5 Brief** — het exporteerbare eindresultaat (fase 2).
- **S6 Instellingen** — gevolgde niches, concurrenten, platform- en landvoorkeur.

### Hoofdflow — van leeg canvas naar een eigen advertentie

Niche of concurrent instellen → feed doorzoeken op sterk signaal → drie tot vijf advertenties met overeenkomstige angle taggen in de swipefile → patroon herkennen in hook en format → zelf een script of creative-opdracht schrijven op basis van dat patroon. In fase 1 is de laatste stap handmatig; F6 automatiseert die pas als het handmatige patroon zich heeft bewezen.

### Terugkeerflow — waarom dit meer is dan een eenmalige zoektocht

Zodra een eigen advertentie draait, verschuift het gebruik naar Rol B: concurrent-tracking laten zien wanneer gevolgde pagina's een advertentie stoppen (een teken van vermoeidheid, hoofdstuk 5) of juist een nieuwe variant lanceren. Dat is het moment om de eigen creative te verversen vóór de eigen resultaten al zijn teruggelopen.

## 8. Randvoorwaarden

- **Versheid** — de feed ververst dagelijks; elke datum bij een advertentie is de laatst geconstateerde actieve status, geen garantie dat hij nu nog loopt.
- **Transparantie** — elk signaal is herleidbaar naar de onderliggende longevity- en variatiecijfers.
- **Auteursrecht** — creatives worden bewaard voor eigen onderzoek en inspiratie, nooit gepubliceerd, doorverkocht of als eigen werk gepresenteerd. Dit is een werkregel, geen juridisch advies.
- **Privacy** — er worden geen persoonsgegevens van de doelgroep opgeslagen buiten wat de advertentie zelf publiek toont.
- **Snelheid** — niet kritisch. Een dagelijkse batchverversing volstaat; niemand wacht live op resultaten.
- **Taal & markt** — begin bij de landen waarin zelf verkocht wordt; geen aparte lokalisatie-eis zolang dit persoonlijk gebruik blijft.

## 9. Fasering

Dezelfde les als Kansenradar hoofdstuk 9, nu direct verwerkt in plaats van er later achter te komen: een persoonlijke tool bouwen kan het makkelijkste uitstelmiddel worden dat er is. Daarom heeft fase 1 een harde deadline, vanaf het begin.

### Fase 0 — Validatie zonder code *(~3 dagen)*
Tien tot vijftien advertenties handmatig doorzoeken in de Meta Ad Library-website zelf, voor één gekozen niche. Toetsen: klopt de longevity/variatie-heuristiek uit hoofdstuk 5 tegen wat er intuïtief als "dit lijkt te werken" aanvoelt?
**Levert:** bevestiging van het signaalmodel, en een eerste ruwe lijst kandidaat-hooks zonder dat er één regel code is geschreven.

### Fase 1 — Eén bron, één niche, één deadline *(MVP · harde deadline)*
Meta Ad Library API, één niche. Feed, advertentiedetail, signaal-engine, swipefile. Concurrent-tracking en briefgenerator mogen wachten.
**Harde regel:** op de einddatum wordt met wat er dan staat een brief geschreven en een eigen advertentie gepubliceerd — ongeacht of de tool compleet aanvoelt. Een onvolledige tool die tot een advertentie dwingt, is het doel.

### Fase 2 — De loop sluiten met eigen data *(na de eerste advertentie)*
Eigen Ads Manager koppelen: nu is er voor het eerst echte CPA/ROAS-data om het signaalmodel tegen te toetsen. Concurrent-tracking (F4), briefgenerator (F6) en landingspagina-teardown (F7) toevoegen. TikTok erbij als de eigen markt daarom vraagt.

Het toetsen zelf verloopt via testparen: twee varianten die op één dimensie verschillen, opgezet en verdeeld met Meta Experiments of TikTok Smart+ — geen eigen test-infrastructuur, die functionaliteit bestaat al. Alleen de uitkomst (welke variant won, op welke dimensie) wordt teruggelogd naar het signaalmodel. Dat is een uitbreiding van F6, geen nieuwe module.
**Levert:** een signaalmodel dat getoetst is aan echte resultaten, niet aan aanname.

### Fase 3 — Pas heropenen als het zichzelf bewijst *(optioneel, later)*
Alleen als de tool na meerdere producten aantoonbaar betere beslissingen oplevert dan de aanschaf van een bestaand pakket: overwegen om het als product aan anderen aan te bieden (P3, multi-tenancy, teams). Dit is een nieuw project met een eigen go-to-market, geen automatisch vervolg.
**Levert:** alleen relevant als fase 1 en 2 een aantoonbaar werkend model hebben opgeleverd.

## 10. Bottlenecks & pre-mortem

De generieke categorieën (aanpak, uitvoering, juridisch in algemene zin) zijn al doorgenomen in Kansenradar hoofdstuk 12 en gelden hier onverkort. Deze sectie beperkt zich tot wat specifiek anders of nieuw is bij een tool die op ad-libraries draait.

**01 — Longevity is een zwakke proxy, geen meting.** Een advertentie die lang draait ondanks matige resultaten — omdat niemand het budget controleert — ziet er in dit model identiek uit aan een echte winnaar. Dit is de grens van wat zonder spend-data mogelijk is; het driewaardige signaal is er om die onzekerheid niet te verbergen, niet om hem op te lossen.

**02 — De grens tussen geïnspireerd en gekopieerd is dun.** Een hook of angle overnemen is legitiem patroononderzoek; een advertentie woordelijk namaken is een ander risico. De briefgenerator (F6) moet daarom altijd de bronvoorbeelden tonen, nooit een kant-en-klare tekst zonder attributie aanleveren.

**03 — Buiten de EU valt de dekking niet terug maar weg.** Zowel TikTok's Commercial Content API als Meta's Ad Library leveren commerciële advertenties alleen als die de EU bereikten — beide door de DSA, niet uit eigen keuze. Buiten de EU is de tool dus niet "Meta-only", maar zonder bruikbare bron. Dit was in een eerdere versie te mild opgeschreven en is de scherpste randvoorwaarde van het hele project: valt de markt buiten de EU, dan vervalt de gratis route en is risico 04 de enige overgebleven optie.

**04 — Bouwen versus een kant-en-klare spy-tool huren.** PiPiads, BigSpy en Foreplay bestaan al en kosten €30–100 per maand, met vaak betere dekking dan een eigen Ad Library-integratie in fase 1. Bewust verworpen ten gunste van een eigen tool, hier vermeld voor traceerbaarheid.

Twee risico's zijn ongewijzigd overgenomen van Kansenradar omdat ze niet productspecifiek zijn: **bouwen als uitstelmiddel** (tegenmaatregel: de harde deadline in fase 1) en **scope creep via "nog één bron of module erbij"** (tegenmaatregel: dezelfde deadline).

## 11. Open keuzes

| Vraag | Toelichting |
|---|---|
| **Markt** | *Nieuw en blokkerend, 31 augustus 2026.* In of naar de EU verkopen, of daarbuiten? Bepaalt of de gratis bron überhaupt data levert (hoofdstuk 6). Dit gaat vóór de nichekeuze: zonder EU-markt is er geen bron om een niche in te zoeken. |
| **Niche** | Welke productcategorie eerst? Bepaalt of Meta alleen genoeg dekking geeft of dat TikTok erbij nodig is. |
| **Startpunt** | Meteen koppelen aan een concreet product uit Kansenradar's eerdere werk, of een nieuwe, onafhankelijke productkeuze? *Voorstel: koppelen* — scheelt een aparte beslissing en toetst meteen of de twee documenten samen werken. |
| **Deadline** | Concrete einddatum voor fase 1 — zonder vaste datum is "harde deadline" in hoofdstuk 9 een intentie, geen mechanisme. |
| **Techniek** | Opgelost in het Technisch Ontwerp (`technisch-ontwerp.md`): Python + SQLite + Streamlit. |
| **Naam & repo** | "Swipedesk" is een werktitel. Repository: `eva-ster/swipedesk`. |
