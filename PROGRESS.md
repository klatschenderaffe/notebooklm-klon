# Projekt-Verlauf: NotebookLM-Klon

Diese Datei protokolliert den **gesamten** Verlauf des Projekts chronologisch — nicht nur erfolgreiche Schritte, sondern auch Probleme, Fehler, Debugging-Sitzungen und die dabei gefundenen Lösungen. Ziel: Der Nutzer soll später jeden Schritt nachvollziehen können, inklusive dem, was nicht auf Anhieb funktioniert hat.

Format pro Eintrag: Datum, was gemacht wurde, was ggf. schiefgelaufen ist, wie es gelöst wurde, offene Punkte.

---

## 2026-09-16 — Projektstart & Recherche

**Getan:**
- Projektverzeichnis `NotebookLM-Klon` angelegt (noch kein Git-Repo).
- Recherche zum Funktionsprinzip von Google NotebookLM durchgeführt:
  - **RAG-Architektur**: NotebookLM kombiniert ein LLM (Gemini) mit Retrieval-Augmented Generation. Anfragen werden nicht direkt ans LLM gestellt, sondern zunächst werden relevante Passagen aus den hochgeladenen Quellen gesucht (Retrieval) und nur diese Passagen als Kontext an das LLM übergeben. Das Modell antwortet ausschließlich auf Basis dieses Kontexts.
  - **Source Grounding**: Jede Antwort wird mit Inline-Zitaten versehen, die auf die genaue Passage in der Ursprungsquelle verweisen. Es wird explizit kein Wissen aus dem offenen Internet/Trainingsdaten verwendet — dadurch werden Halluzinationen reduziert.
  - **Unterstützte Eingabeformate im Original**: PDF, Google Docs, Google Slides, Webseiten, YouTube-Transkripte, Audiodateien.
  - **Zusatzfunktionen im Original**: "Audio Overview" (KI-generierter Podcast-Dialog über die Quellen) und seit November 2025 "Slide Deck"-Generierung (KI-narrierte Präsentationen mit Visuals/Diagrammen/Zitaten aus den Quellen, per Bildgenerierungsmodell).
  - Quellen: DigitalOcean ("What Is NotebookLM?"), Wikipedia ("NotebookLM"), blog.google (Audio Overviews Announcement), dev.to (Architektur-Deep-Dive Gemini-Integration).

**Probleme / Debugging:** keine.

**Nächster Schritt:** Anforderungsinterview mit dem Nutzer zur Festlegung von Tech-Stack, Architektur und Scope, bevor Repo-Struktur und DevOps-Setup (GitHub + Netlify + CI/CD) aufgesetzt werden.

---

## 2026-09-16 — Interview Teil 1: Kern-Architektur-Entscheidungen

**Getan:**
- Recherche zu Kostenoptionen der wichtigsten Anbieter durchgeführt, da der Nutzer explizit nach kostenlosen Optionen gefragt hat:
  - **Google Gemini API**: einziger Anbieter mit echtem, dauerhaftem Free Tier (kein Ablaufdatum, keine Kreditkarte nötig). Flash-Modell z.B. ~1.500 Anfragen/Tag. Trade-off: Daten im Free Tier dürfen von Google zu Trainingszwecken verwendet werden.
  - **OpenAI / Anthropic Claude API**: nur einmaliges Startguthaben (~5–10$), läuft nach ca. 3 Monaten ab, danach kostenpflichtig — für Dauerbetrieb ungeeignet, wenn "kostenlos" Priorität hat.
  - **Netlify**: kostenloser Plan reicht für Projekt mit geringer Nutzung (125.000 Funktionsaufrufe/Monat, ~15 GB Traffic-Guthaben).
  - **Render vs. Railway vs. Fly.io** (für separat gehosteten Python-Service): Render ist aktuell der einzige Anbieter mit einem dauerhaften kostenlosen Tier; Trade-off: Dienst pausiert nach 15 Min. Inaktivität, erste Anfrage danach dauert ca. 30–50 Sekunden (Cold Start). Railway und Fly.io bieten nur noch Zeit-/Guthaben-limitierte Trials, danach kostenpflichtig.
- Interview-Fragen zur Architektur gestellt und folgende Entscheidungen getroffen:

**Entscheidungen:**
- **LLM-/Embedding-Provider:** Google Gemini API (wegen dauerhaftem Free Tier)
- **Backend-Sprache:** Python für die gesamte Backend-Logik als separater Service (kein Netlify-Function-Mix mit JS nötig — JS wird für das Frontend genutzt)
- **Vektordatenbank:** Supabase (Postgres + pgvector), liefert im selben kostenlosen Tier zusätzlich Datei-Storage
- **Nutzerverwaltung:** Single-User ohne Login (reduziert Komplexität, kein Auth-System nötig)

**Probleme / Debugging:** keine.

**Offen:** Hosting des Python-Backends (Render als kostenlose Option im Gespräch), Frontend-Framework, Präsentations-Ausgabeformat, Datei-Storage-Details, CI/CD-Anforderungen, Repo-Struktur.

---

## 2026-09-16 — Interview Teil 2: Hosting, Frontend, Präsentation, Storage

**Entscheidungen:**
- **Backend-Hosting:** Render (kostenloser Tier, Cold-Start-Trade-off akzeptiert)
- **Frontend-Framework:** React + Vite
- **Präsentationsformat:** Download als PPTX (Erzeugung via python-pptx im Backend)
- **Datei-Storage:** Supabase Storage (selber Anbieter wie Vektordatenbank)

**Probleme / Debugging:** keine.

---

## Offene Entscheidungen (werden im Interview geklärt)

- [x] LLM-/Embedding-Provider → Google Gemini API
- [x] Backend-Architektur → Python (separater Service), JS nur Frontend
- [x] Vektordatenbank / RAG-Speicher → Supabase (pgvector)
- [x] Nutzerverwaltung / Auth → Single-User ohne Login
- [x] Hosting des Python-Backends → Render
- [x] Frontend-Framework → React + Vite
- [x] Format der generierten Präsentationen → PPTX-Download
- [x] Datei-Storage-Lösung → Supabase Storage
- [x] CI/CD-Anforderungen → Linting (ESLint/Ruff), Type-Checking (TypeScript/mypy), Unit-Tests, Build-Check via GitHub Actions
- [x] Repo-Struktur → Monorepo (/frontend, /backend)
- [x] GitHub-Setup → neues Repo per gh CLI anlegen
- [x] Design-Details → Light/Dark Mode mit Umschalter

## 2026-09-16 — Interview Teil 3: DevOps-Grundlagen

**Entscheidungen:**
- **Repo-Struktur:** Monorepo mit `/frontend` (React + Vite + TypeScript, Netlify) und `/backend` (Python/FastAPI, Render)
- **GitHub:** neues Repository wird per `gh` CLI angelegt
- **CI/CD (GitHub Actions):** Linting (ESLint für Frontend, Ruff für Backend), Type-Checking (TypeScript + mypy), Unit-Tests, Build-Check bei jedem Push/PR
- **Design:** Light/Dark Mode mit Umschalter, folgt standardmäßig der Systemeinstellung
- Da Type-Checking gewünscht ist, wird das Frontend in **TypeScript** statt reinem JavaScript umgesetzt (React + Vite + TS)

**Probleme / Debugging:** keine.

**Nächster Schritt:** Letzte offene Detailfragen klären (Repo-Name, Sichtbarkeit, API-Key-/Secret-Handling), dann Grundgerüst (Ordnerstruktur, Git-Init, GitHub-Repo, Netlify- & Render-Konfiguration) aufsetzen.

---

## 2026-09-16 — Interview Teil 4: Repo-Name & Secret-Handling

**Entscheidungen:**
- **Sichtbarkeit:** Repo ist **öffentlich** → oberste Priorität: keine Secrets/Tokens dürfen im Repo landen.
- **Secret-Handling:** Keys (Gemini API-Key, Supabase-Keys) ausschließlich in lokalen `.env`-Dateien (per `.gitignore` ausgeschlossen) sowie direkt in den Secret-Verwaltungen von Netlify, Render und GitHub Actions. Zusätzlich wird ein automatisierter Secret-Scan (Gitleaks) als GitHub-Actions-Check ergänzt, der bei jedem Push/PR prüft, ob versehentlich Keys committet wurden.
- **Repo-Name:** `notebooklm-klon`, öffentlich, unter GitHub-Account `klatschenderaffe` (bereits über `gh auth status` als eingeloggt verifiziert).

**Probleme / Debugging:** keine.

---

## Finale Architektur-Zusammenfassung (Ende Interview)

| Bereich | Entscheidung |
|---|---|
| LLM & Embeddings | Google Gemini API (kostenloser Tier) |
| Backend | Python (FastAPI), separater Service |
| Backend-Hosting | Render (kostenloser Tier, Cold Start ~30-50s nach Inaktivität) |
| Frontend | React + Vite + TypeScript |
| Frontend-Hosting | Cloudflare Pages (kostenloser Tier) |
| Vektordatenbank | Supabase (Postgres + pgvector) |
| Datei-Storage | Supabase Storage |
| Nutzerverwaltung | Single-User, kein Login |
| Präsentations-Export | PPTX-Download (python-pptx im Backend) |
| Repo-Struktur | Monorepo (`/frontend`, `/backend`) |
| GitHub | öffentliches Repo `notebooklm-klon`, Account `klatschenderaffe` |
| CI/CD | GitHub Actions: Linting (ESLint/Ruff), Type-Checking (TS/mypy), Unit-Tests, Build-Check, Gitleaks Secret-Scan |
| Design | Light/Dark Mode mit Umschalter, minimalistisch/modern |
| Secret-Handling | Nur `.env` (gitignored) + Plattform-Secrets, nie im Git-Verlauf |

**Nächster Schritt:** Projekt-Grundgerüst aufsetzen (Ordnerstruktur, Frontend-/Backend-Scaffold, Git-Init, GitHub-Repo anlegen & pushen, CI/CD-Workflows, Netlify-/Render-Konfiguration).

---

## 2026-09-16 — Projekt-Grundgerüst & lokale Verifikation

**Getan:**
- Lokale Toolchain fehlte (kein Node/npm, nur veraltetes Python 3.9.6 aus den Command Line Tools) → nach Rückfrage per Homebrew installiert: `node` (v26.8.2) und `python@3.12` (v3.12.14).
- **Frontend** gescaffoldet mit `npm create vite@latest frontend -- --template react-ts`. Default-Boilerplate (Marketing-Landingpage, Vite/React-Logos) entfernt und durch minimalistische App-Shell ersetzt: Header mit Titel + Light/Dark-Toggle (persistiert in `localStorage`, respektiert `prefers-color-scheme` als Default via `data-theme`-Attribut-Pattern), Karten-Layout mit Hinweis auf unterstützte Dateitypen (`.pdf`, `.md`), Platzhalter für den Datei-Upload (Funktion folgt später), sowie ein Live-Status-Indikator, der `/health` am Backend pingt.
- **Backend** manuell strukturiert (`app/main.py`, `app/config.py`, `app/routers/health.py`, `app/services/`, `tests/`): FastAPI mit CORS-Middleware, `/health`-Endpoint, Settings über `pydantic-settings` (liest `.env`). Virtuelle Umgebung mit Python 3.12 angelegt, Dependencies installiert.
- Paketversionen in `requirements.txt`/`requirements-dev.txt` zunächst aus dem Gedächtnis geschätzt — dabei festgestellt, dass die Schätzungen veraltet waren. Korrigiert, indem die tatsächlich aktuellen Versionen live von PyPI abgefragt wurden (u.a. `fastapi==0.141.1`, `google-genai==2.23.0`, `supabase==2.31.0`).
- Root-Level DevOps-Dateien angelegt: `.gitignore` (schließt `.env`, `node_modules/`, `.venv/`, Caches etc. aus), `README.md` (Architektur-Überblick, lokale Setup-Anleitung, Secret-Handling-Regeln), `netlify.toml` (Build aus `/frontend`, Node 26), `render.yaml` (Blueprint für den Backend-Service, Secrets als `sync: false` definiert statt inline), `.github/workflows/ci.yml` (Jobs: Gitleaks Secret-Scan, Frontend Lint/Typecheck/Build, Backend Lint/Typecheck/Test).
- Vor dem Schreiben des CI-Workflows die aktuell gültigen Action-Versionen recherchiert, da `gitleaks-action@v2` laut offizieller Ankündigung exakt am 16.09.2026 (heutiges Datum) wegen des Wegfalls von Node 20 auf GitHub-Runnern nicht mehr funktioniert → stattdessen `gitleaks-action@v3`, sowie `actions/checkout@v7`, `actions/setup-node@v7`, `actions/setup-python@v7` verwendet.
- **Lokale Verifikation, alles grün:**
  - Backend: `ruff check .` ✅, `mypy app` ✅, `pytest -q` ✅ (1 Test)
  - Frontend: `npm run lint` (oxlint) ✅, `npm run build` (tsc + vite build) ✅
  - Frontend-Dev-Server und Backend-Server gemeinsam gestartet, End-to-End-Verbindung über den Browser (Claude in Chrome) geprüft: Seite rendert korrekt, Theme-Toggle funktioniert (Screenshot Light/Dark), Status-Indikator zeigt korrekt "Backend erreichbar" (grün) bzw. "Backend nicht erreichbar" (rot), je nachdem ob das Backend lief.
  - Nutzer hat zusätzlich selbst lokal durch die Anwendung geklickt und den Stand bestätigt ("Passt soweit").

**Probleme / Debugging:**
- Beim ersten Testlauf der Backend-Tests erschien eine `StarletteDeprecationWarning`: *"Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead."* Tests liefen trotzdem erfolgreich durch (nicht blockierend), sollte aber beobachtet werden — ggf. später auf `httpx2` migrieren, sobald sich das im Ökosystem etabliert hat.
- Standardmäßig von `npm create vite` generierter Linter ist inzwischen `oxlint` statt `ESLint` (Rust-basierter, schnellerer Nachfolger im Vite-Ökosystem). Im Interview war "ESLint" als Beispieltechnologie genannt, die eigentliche Anforderung war jedoch "Linting" allgemein — `oxlint` erfüllt denselben Zweck und wurde beibehalten, um dem aktuellen Vite-Standard zu folgen. Wird hier transparent vermerkt, da Abweichung von der wörtlichen Interview-Antwort.

**Wichtiger Hinweis für den Nutzer (noch offen):** Bevor Deploys auf Netlify/Render funktionieren, müssen dort jeweils eigene Accounts/Projekte angelegt und die Secrets (`GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ALLOWED_ORIGINS`) eingetragen werden. Das ist noch nicht erfolgt.

**Nächster Schritt:** Lokales Git-Repository initialisieren, öffentliches GitHub-Repo `notebooklm-klon` per `gh` CLI anlegen und ersten Commit pushen.

---

## 2026-09-16 — Git-Init, GitHub-Repo & erste CI-Pipeline

**Getan:**
- Lokales Git-Repository initialisiert, alle Projektdateien geprüft und committet (34 Dateien) — verifiziert, dass **keine** `.env`, `node_modules/`, `.venv/`, `dist/` oder sonstigen generierten/sensiblen Dateien im Commit enthalten sind.
- Öffentliches GitHub-Repository `klatschenderaffe/notebooklm-klon` per `gh repo create --public --source=. --remote=origin --push` angelegt.
- Ersten Commit gepusht und verifiziert, dass die CI-Pipeline (GitHub Actions) automatisch anläuft.
- **CI-Ergebnis: alle 3 Jobs grün** ✅ Secret Scan (Gitleaks), ✅ Backend (Lint/Typecheck/Test), ✅ Frontend (Lint/Typecheck/Build).
- Repo: https://github.com/klatschenderaffe/notebooklm-klon

**Probleme / Debugging:**
- `gh repo create ... --push` schlug beim automatischen Push fehl: `Host key verification failed` / `Could not read from remote repository`. Ursache: `~/.ssh/known_hosts` existierte auf diesem Rechner noch gar nicht, da SSH zu GitHub hier zuvor noch nie genutzt wurde (Git-Protokoll ist laut `gh auth status` auf SSH eingestellt) — der SSH-Host-Key von GitHub war also nicht vertrauenswürdig hinterlegt.
  - **Lösung:** `ssh-keyscan -t rsa,ed25519 github.com` ausgeführt und Ergebnis in `~/.ssh/known_hosts` eingetragen (Rechte auf `700`/`600` gesetzt). Mit `ssh -T git@github.com` verifiziert, dass die Authentifizierung danach funktioniert. Anschließend manueller `git push -u origin main` — erfolgreich. Das GitHub-Repo selbst war durch den vorherigen Befehl bereits korrekt angelegt worden, nur der Push scheiterte.

**Offen (nächste Schritte, nicht Teil dieses Setups):**
- Supabase-Projekt anlegen (Datenbank + pgvector + Storage), Keys in `.env` (lokal) und in Cloudflare/Render/GitHub-Secrets eintragen.
- Gemini API-Key über Google AI Studio erstellen, ebenso hinterlegen.
- Cloudflare-Pages-Projekt mit dem GitHub-Repo verbinden (nutzt `frontend/wrangler.toml`).
- Render-Service über `render.yaml`-Blueprint verbinden.
- Eigentliche Kernfunktionen implementieren: Datei-Upload, RAG-Pipeline (Chunking, Embeddings, Retrieval, Chat), PPTX-Generierung.

---

## 2026-09-16 — Wechsel des Frontend-Hostings: Netlify → Cloudflare Pages

**Getan:**
- Nutzer äußerte nachträglich Unsicherheit bezüglich Netlify als Frontend-Host und bat um Alternativen.
- Recherche zu aktuellen (Stand Sept. 2026) kostenlosen Static-Site-Hosting-Optionen durchgeführt: Cloudflare Pages, Vercel, GitHub Pages, Render Static Site, Netlify verglichen (Bandbreiten-Limits, Build-Minuten, GitHub-Integration).
- **Ergebnis:** Cloudflare Pages gewählt — einziger verglichener Anbieter ohne Bandbreiten-Deckelung im Free Tier (500 Builds/Monat), genauso einfache GitHub-Integration wie Netlify.
- Umsetzung: `netlify.toml` entfernt, stattdessen `frontend/wrangler.toml` (Cloudflare-Pages-Build-Konfiguration: Output-Verzeichnis `dist`) angelegt. `README.md` und `PROGRESS.md` (Architektur-Tabelle) entsprechend aktualisiert.

**Probleme / Debugging:** keine.

**Offen:** Cloudflare-Pages-Projekt muss noch im Cloudflare-Dashboard mit dem GitHub-Repo verbunden werden (Build-Verzeichnis `frontend`, Build-Command `npm run build`, Output `dist`) — Anleitung dazu in `README.md` unter "Deployment".

---

## 2026-09-16 — Kernfunktionen implementiert: Upload, RAG-Chat, Präsentationserstellung

Nutzer-Wunsch für die Reihenfolge der nächsten Schritte: zuerst Kernfunktionen (Code), dann Supabase-Projekt live einrichten, dann Cloudflare-Deployment. Dieser Eintrag deckt Schritt 1 ab.

**Getan:**
- **Supabase-Schema als Code versioniert** (`backend/supabase/schema.sql`, wird in Phase 2 im Supabase SQL Editor ausgeführt): Tabellen `sources` und `chunks` (inkl. `pgvector`-Spalte, HNSW-Index für Cosine-Similarity), RPC-Funktion `match_chunks` für die Ähnlichkeitssuche über `supabase-py`.
- **Backend-Services** implementiert:
  - `text_extraction.py` — Text aus PDF (`pypdf`) und Markdown extrahieren.
  - `chunking.py` — Absatz-bewusstes, überlappendes Chunking.
  - `gemini_client.py` — Embeddings (`gemini-embedding-2`, 768 Dimensionen) und Chat-Antworten (`gemini-3.8-flash`) über die `google-genai`-SDK; Präsentations-Gliederung wird als strukturiertes JSON (`response_schema`) angefragt. Modellnamen bewusst über `Settings` konfigurierbar gemacht statt hart im Code verteilt, da Google aktuell im 4-6-Wochen-Takt neue Flash-Versionen veröffentlicht (Modell-Alias `gemini-flash-latest` wurde von Google bereits einmal abgekündigt) — ein Modellwechsel erfordert damit nur eine Env-Var-Änderung.
  - `vector_store.py` — Supabase-Zugriff (Sources/Chunks CRUD, Ähnlichkeitssuche über `match_chunks`-RPC).
  - `storage.py` — Original-Dateien in Supabase Storage hochladen.
  - `presentation.py` — PPTX-Datei aus einer Gliederung bauen (`python-pptx`).
- **API-Endpunkte:** `POST/GET/DELETE /sources` (Upload-Pipeline: Validierung → Textextraktion → Chunking → Embedding → Storage-Upload → DB-Insert), `POST /chat` (Frage einbetten → Ähnlichkeitssuche → Antwort ausschließlich aus gefundenen Chunks generieren, inkl. Zitate), `POST /presentations` (Gliederung generieren → PPTX bauen → als Datei-Download zurückgeben).
- **Frontend:** `api.ts` (typisierter Fetch-Client), `SourcesPanel` (Upload per Drag&Drop/Klick, Liste, Löschen), `ChatPanel` (Chatverlauf inkl. Zitat-Anzeige), `PresentationPanel` (Thema eingeben → PPTX-Download). `App.tsx` zu einem Zwei-Spalten-Layout (Quellen+Präsentation / Chat) umgebaut.
- **Tests (ohne echte Netzwerk-Calls, alles gemockt):** 20 Backend-Tests — reine Logik (Chunking, Text-Extraktion, PPTX-Bau) sowie API-Endpunkte mit gemockten Gemini-/Supabase-Aufrufen. `ruff`, `mypy`, `pytest` grün. Frontend: `oxlint` und `tsc -b && vite build` grün.

**Probleme / Debugging:**
1. **Bug beim ersten Wurf:** In `sources.py` wurde `storage_path` erst nach dem DB-Insert lokal am zurückgegebenen Objekt gesetzt, aber nie tatsächlich in die Datenbank zurückgeschrieben — die Zeile in Supabase hätte dauerhaft `storage_path=""` gehabt. **Fix:** Source-ID jetzt vorab client-seitig per `uuid.uuid4()` generiert, damit der Storage-Pfad vor dem DB-Insert feststeht und korrekt mitgespeichert wird.
2. **mypy-Fehler durch lose typisierte externe SDKs** (`supabase-py` gibt generische `JSON`-Typen zurück, `google-genai` hat sehr breite Union-Typen für `contents`): mit gezielten `cast(...)`-Aufrufen behoben, da zur Laufzeit die konkreten Typen bekannt sind.
3. **Echter Bug beim Live-Test im Browser gefunden** (nicht nur Konfigurationsproblem): Beim Testen ohne Supabase-Zugangsdaten zeigte das Frontend nur „Failed to fetch“ statt einer verständlichen Fehlermeldung.
   - **Ursache:** Ein unbehandelter Python-Fehler im Backend führte zu einem 500-Response *ohne* `Access-Control-Allow-Origin`-Header. Grund: FastAPI/Starlette routet Handler für die generische `Exception`-Klasse (`@app.exception_handler(Exception)`) an `ServerErrorMiddleware`, das *außerhalb* von `CORSMiddleware` liegt — dessen Antwort läuft nie durch `CORSMiddleware`, bekommt also nie CORS-Header. Der Browser blockiert die Antwort dann komplett und meldet nur „Failed to fetch“, ohne den eigentlichen Fehler preiszugeben.
   - **Erster Fixversuch fehlgeschlagen:** `@app.exception_handler(Exception)` hinzugefügt — per `curl` verifiziert, dass der Header immer noch fehlte.
   - **Zweiter Fixversuch fehlgeschlagen:** Stattdessen eine eigene `BaseHTTPMiddleware` gebaut und *nach* `CORSMiddleware` registriert — Header fehlte weiterhin. Ursache: `app.add_middleware()` fügt jede Middleware am **Anfang** der internen Liste ein (nicht ans Ende), wodurch die Reihenfolge genau umgekehrt zur Erwartung war und die eigene Middleware *außerhalb* von `CORSMiddleware` landete statt innerhalb.
   - **Tatsächlicher Fix:** Registrierungsreihenfolge vertauscht — die eigene `CatchAllExceptionsMiddleware` wird *vor* `CORSMiddleware` registriert, wodurch sie (aufgrund der Insert-an-Position-0-Logik) innerhalb von `CORSMiddleware` landet. Per `curl -H "Origin: ..."` verifiziert, dass der `access-control-allow-origin`-Header jetzt auch bei einem 500-Fehler gesetzt ist. Zusätzlich als Regressionstest (`test_error_handling.py`) abgesichert, damit dieser Bug bei künftigen Refactorings nicht unbemerkt wieder auftritt.
4. **Live-Verifikation im Browser** (mit laufendem Backend, aber noch ohne echte Gemini-/Supabase-Credentials): Upload einer Test-Markdown-Datei durchlaufen lassen — Pipeline kam korrekt bis zum Gemini-Embedding-Aufruf und schlug dort mit der erwarteten Fehlermeldung *"No API key was provided"* fehl (kein Bug, sondern der erwartete Zustand vor Phase 2). Dank Fix aus Punkt 3 wurde das im Frontend jetzt auch korrekt als „Interner Serverfehler“ angezeigt statt als unklares „Failed to fetch“.

**Noch nicht live testbar (folgt in Phase 2 „Supabase“ bzw. mit echtem Gemini-Key):** tatsächlicher Upload-Durchlauf inkl. Embedding + Speicherung, Chat mit echten Antworten, Präsentations-Generierung mit echtem Inhalt. Die Code-Pfade dafür sind vollständig implementiert und unit-getestet (mit gemockten externen Aufrufen), aber ein End-to-End-Test mit echten Credentials steht noch aus.

**Nächster Schritt:** Supabase-Projekt live anlegen (Schema aus `backend/supabase/schema.sql` ausführen, Storage-Bucket `sources` anlegen, Keys besorgen), Gemini-API-Key erstellen, beides lokal in `.env` eintragen und End-to-End im Browser verifizieren.

---

## 2026-09-16 — Manueller Test durch Nutzer: Responsive-Bug gefunden & behoben (Mobile-First)

**Getan:**
- Nutzer hat das Frontend lokal selbst getestet (vor jedem Commit/Push, wie gewünscht) und einen Layout-Bug gemeldet: Der "Als PPTX herunterladen"-Button lief über den Panel-Rand hinaus.
- **Ursache:** `.presentation-form` war eine Flex-Row aus Input (`flex: 1`) und Button (`white-space: nowrap`, kein Shrink/Wrap) — bei einem langen Button-Label wie "Als PPTX herunterladen" plus der intrinsischen Mindestbreite von `<input>`-Elementen ergab das mehr Breite als der 380px-Sidebar-Panel zur Verfügung hatte, wodurch der Button optisch über den Rand hinausragte.
- **Fix + komplette Umstellung auf Mobile-First** (auf ausdrücklichen Wunsch des Nutzers, betrifft `frontend/src/App.css`):
  - Alle Basis-Styles (ohne Media Query) gelten jetzt für schmale Viewports: `.layout` ist standardmäßig eine einspaltige Flex-Column, `.presentation-form` steht standardmäßig untereinander (Input oben, Button darunter, volle Breite) statt nebeneinander — das behebt den gemeldeten Bug grundsätzlich, unabhängig von der Bildschirmbreite.
  - Ab `min-width: 800px` (Desktop) wird per Media Query auf das zweispaltige Grid-Layout umgeschaltet (vorher war es umgekehrt/Desktop-first mit `max-width`-Query).
  - Generelle Button-/Touch-Ziel-Regeln ergänzt: `min-height: 44px` auf Submit-Buttons und Eingabefeldern (Empfehlung für Touch-Bedienbarkeit), `min-width: 0` auf Flex-Kindern (Input, Button, Source-Namen) als generische Absicherung gegen Flex-Overflow, `font-size: 16px` auf Text-Inputs (verhindert automatisches Zoomen bei Fokus auf iOS-Safari).
  - `.chat-input-row` bleibt bewusst eine Zeile (kurzes Label "Senden"), aber mit `min-width: 0` auf dem Input und `flex-shrink: 0` auf dem Button abgesichert, damit dort derselbe Bug nicht auftreten kann.
- Verifiziert im Browser (Claude in Chrome) bei 375px (Mobile) und 1440px (Desktop): Button bleibt in beiden Fällen vollständig innerhalb des Panels, Layout schaltet korrekt zwischen ein- und zweispaltig um.
- `oxlint` und `npm run build` (tsc + vite build) laufen weiterhin fehlerfrei.

**Probleme / Debugging:** Der gemeldete Overflow-Bug selbst (siehe Ursache oben) — kein weiterer Debugging-Aufwand nötig, direkt reproduzierbar und behoben.

**Nächster Schritt:** Weiterhin wie zuvor — Supabase-Projekt live einrichten, danach Gemini-Key, danach Cloudflare-Deployment. Commit/Push für die Kernfunktionen (inkl. dieses CSS-Fixes) steht noch aus, wartet auf Freigabe durch den Nutzer.

---

## 2026-09-16 — Supabase-Projekt live eingerichtet (mit zwei gefundenen Bugs)

**Getan:**
- Nutzer hat Supabase-Account + Projekt `notebooklm-klon` angelegt (geführt Schritt für Schritt, Account-Erstellung selbst durfte/wollte ich nicht übernehmen).
- Beim Projekt-Setup nach den drei „Data API"-Optionen gefragt worden. Empfehlung gegeben: **Enable Data API** an (Pflicht für `supabase-py`), **Automatically expose new tables** aus (Supabase-Empfehlung, sollte nur `anon`/`authenticated` betreffen), **Enable automatic RLS** an (unschädlich für `service_role`, da dieser RLS immer umgeht).
- Schema aus `backend/supabase/schema.sql` im SQL Editor ausgeführt.
- Storage-Bucket `sources` angelegt: privat, 20 MB Limit, MIME-Whitelist (`application/pdf`, `text/markdown`, `text/x-markdown`, `text/plain`).
- Dabei proaktiv einen Zuverlässigkeitsbug im eigenen Code gefunden und behoben, bevor er unter echten Bedingungen aufgefallen wäre: `storage.py` setzte beim Upload keinen expliziten `Content-Type`, sondern verließ sich auf Auto-Erkennung durch die Supabase-Bibliothek — bei der neu eingerichteten MIME-Type-Restriktion auf dem Bucket hätte das bei `.md`-Dateien potenziell fehlschlagen können. Fix: `upload_source_file()` nimmt jetzt einen expliziten `file_type`-Parameter und setzt `file_options={"content-type": ...}` explizit (`application/pdf` bzw. `text/markdown`). Mit zwei neuen Tests (`test_storage.py`) abgesichert, die die tatsächlich übergebenen Content-Type-Werte prüfen.
- `SUPABASE_URL` und `SUPABASE_SERVICE_KEY` vom Nutzer lokal in `backend/.env` eingetragen (nicht im Chat geteilt), Backend neu gestartet und `GET /sources` getestet.

**Probleme / Debugging (zwei echte Bugs):**
1. **Erster Fehlversuch — falsche URL-Form:** `GET /sources` schlug mit `postgrest.exceptions.APIError: {'message': 'Invalid path specified in request URL', 'code': 'PGRST125'}` fehl. Ursache: In `.env` stand die REST-Endpoint-URL inkl. `/rest/v1/`-Suffix statt der reinen Projekt-URL — Supabase zeigt im Dashboard beide URLs an, `supabase-py` erwartet aber die reine Projekt-URL und hängt `/rest/v1/` selbst an, wodurch der Pfad doppelt vorkam. **Fix:** `/rest/v1/`-Suffix aus `SUPABASE_URL` entfernt (per `sed`, da nur eine nicht-geheime URL betroffen war). Jetzt in `README.md` unter "Supabase Setup" explizit dokumentiert, damit das nicht erneut passiert.
2. **Zweiter Fehlversuch — fehlende Rechte:** Danach `postgrest.exceptions.APIError: {'message': 'permission denied for table sources', 'code': '42501', 'hint': 'Grant the required privileges to the current role with: GRANT SELECT ON public.sources TO service_role;'}`.
   - **Eigene Fehleinschätzung zuvor:** Bei der Empfehlung, "Automatically expose new tables" zu deaktivieren, war die Begründung, dies betreffe nur `anon`/`authenticated` und `service_role` habe ohnehin immer vollen Zugriff. Das war **falsch** bzw. unvollständig: `service_role` umgeht zwar immer Row-Level-Security (RLS), aber die separate SQL-`GRANT`-Rechteebene ist davon unabhängig — und ohne "Automatically expose new tables" vergibt Supabase bei per SQL (statt über den Table Editor) angelegten Tabellen offenbar **keine** automatischen Grants, auch nicht für `service_role`.
   - **Fix:** Explizite `GRANT`/`ALTER DEFAULT PRIVILEGES`-Statements für `service_role` ergänzt und dauerhaft in `backend/supabase/schema.sql` versioniert (nicht nur einmalig im Dashboard ausgeführt), damit das Schema beim nächsten Mal (z.B. neues Supabase-Projekt) reproduzierbar korrekt ist. Vom Nutzer im SQL Editor ausgeführt.
   - Nach beiden Fixes: `curl http://localhost:8000/sources` liefert `200 OK` mit `[]`. Im Browser verifiziert: kein Fehlerbanner mehr im Frontend.
- Backend-Tests weiterhin grün (22 Tests, inkl. der 2 neuen für den Content-Type-Fix), `ruff`/`mypy` sauber.

**Nächster Schritt:** Commit + Push dieses Standes (Storage-Content-Type-Fix, erweitertes `schema.sql` mit Grants, README-Abschnitt "Supabase Setup"). Danach: Gemini-API-Key einrichten, dann End-to-End-Test mit echtem Upload/Chat/Präsentation, danach Cloudflare-Deployment.

---

## 2026-09-16 — Backup außerhalb des Repos: TODO-Liste & Claude-Memory

**Getan:**
- Auf Wunsch des Nutzers eine vollständige, gruppierte `TODO.md` mit allen noch offenen Aufgaben erstellt (Gemini-Setup, End-to-End-Tests, Render-Deployment, Cloudflare-Deployment, spätere Beobachtungspunkte) — **bewusst nicht Teil des Git-Repos**, da der Nutzer das explizit so wollte (Repo ist öffentlich, die TODO-Liste ist reine private Arbeitsplanung). In `.gitignore` als `TODO.md` ausgeschlossen, README-Verweis darauf wieder entfernt.
- Zusätzlich eine persistente Claude-Code-Memory (außerhalb des Projektverzeichnisses, unter `~/.claude/projects/.../memory/notebooklm-klon-project-status.md`) angelegt: eine kurze Orientierungs-Notiz mit Tech-Stack-Entscheidungen, aktuellem Stand und Verweis auf `PROGRESS.md`/`TODO.md` als eigentliche Quelle der Wahrheit — als Backup, falls diese Chat-Session verloren geht und eine neue Session ohne Kontext an diesem Projekt weiterarbeiten muss.
- Beide Dateien liegen ausschließlich lokal beim Nutzer bzw. in Claudes eigenem Memory-Speicher, nicht im Repository.

**Probleme / Debugging:** keine.

---

## 2026-09-16 — Gemini-API-Key eingerichtet & vollständiger End-to-End-Test aller Kernfunktionen

**Getan:**
- Nutzer hat über [Google AI Studio](https://aistudio.google.com/apikey) einen Gemini-API-Key erstellt und lokal in `backend/.env` eingetragen.
- Backend neu gestartet — `GET /sources` weiterhin `200 OK`.
- **Upload getestet** (echte Markdown-Testdatei mit Katzen-Inhalt über die Browser-UI hochgeladen): Text-Extraktion, Chunking, Gemini-Embeddings, Supabase-Storage-Upload und DB-Insert liefen vollständig durch, Datei erschien korrekt in der Quellenliste.
- **Chat getestet:** Frage zur hochgeladenen Datei gestellt, korrekte, ausschließlich quellenbasierte Antwort mit Zitat erhalten (zweite Testfrage zur Ernährung ebenfalls korrekt beantwortet).
- **Präsentationserstellung getestet:** PPTX für das Thema "Katzen als Haustiere" generiert, heruntergeladen (`~/Downloads/praesentation.pptx`, 30 KB) und mit `python-pptx` inhaltlich verifiziert: 3 Folien (Titel + 2 inhaltliche Folien "Allgemeine Merkmale" und "Ernährung"), Inhalte stimmen korrekt mit der Quelldatei überein.
- Test-Quelle danach wieder gelöscht (`DELETE /sources/{id}` → `204`, Liste danach wieder leer), lokale Testdatei im Scratchpad entfernt.
- **Damit sind alle drei Kernfunktionen (Upload, RAG-Chat, Präsentationserstellung) erstmals vollständig mit echten Credentials end-to-end verifiziert.**

**Probleme / Debugging:**
1. **Chat schlug zunächst zweimal fehl** mit `google.genai.errors.ServerError: 503 UNAVAILABLE` — *"This model is currently experiencing high demand"* für `gemini-3.8-flash` (unser bisheriger Standard, laut vorheriger Recherche erst am 2. September 2026 veröffentlicht). Embeddings liefen zu diesem Zeitpunkt bereits erfolgreich durch — das Problem betraf ausschließlich die Chat-Generierung.
2. **Erster Fallback-Versuch fehlgeschlagen:** `GEMINI_CHAT_MODEL` testweise auf `gemini-2.5-flash` gesetzt (älteres, etablierteres Modell) → `404 NOT_FOUND`: *"This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.6-flash..."* — das Modell ist offenbar zwischenzeitlich vollständig eingestellt worden, nicht nur überlastet.
3. **Fix:** `gemini-3.6-flash` (von Google selbst in der Fehlermeldung empfohlen) getestet — funktionierte sofort stabil und lieferte korrekte Antworten. Als neuen Code-Standard in `backend/app/config.py` (`gemini_chat_model`) sowie in `backend/.env.example` hinterlegt, mit Kommentar zur Begründung. Zeigt konkret, warum die Modellnamen bewusst konfigurierbar gemacht wurden (siehe früherer Eintrag zur Kernfunktions-Implementierung) — genau dieser Fall (schnelllebige Modellverfügbarkeit) trat postwendend ein.
4. Ein kleiner UI-Nebeneffekt beobachtet: Bei den ersten beiden fehlgeschlagenen Chat-Versuchen zeigte ein Zwischen-Screenshot nur die erste Fehlermeldung, obwohl laut Backend-Log bereits eine zweite Anfrage verarbeitet wurde — vermutlich nur ein Timing-Artefakt beim Screenshot (React-Update noch nicht gerendert), kein reproduzierbares Problem; ein späterer Screenshot zeigte beide Versuche korrekt.

**Bekannte Lücke (kein Bug, aber notiert):** `DELETE /sources/{id}` löscht die Datei aktuell nur aus der Datenbank (per `on delete cascade` auch die zugehörigen Chunks), aber **nicht** aus dem Supabase-Storage-Bucket — die Originaldatei bleibt dort verwaist liegen. Für den aktuellen Testfall unkritisch, aber als Backlog-Punkt in der lokalen `TODO.md` vermerkt.

**Nächster Schritt:** Backend-Deployment auf Render, danach Frontend-Deployment auf Cloudflare Pages, danach `ALLOWED_ORIGINS` auf die echte Cloudflare-Domain aktualisieren und ein Produktions-Smoke-Test.

---

## 2026-09-16 — Präsentations-Design, Quellen-Auswahl, grüne Akzentfarbe, Google-Drive-Button

Nutzer war mit der Optik der generierten Präsentationen unzufrieden ("sieht lieblos aus") und wollte vor dem Deployment mehrere UX-Verbesserungen: Design-Beschreibung als Eingabefeld, grüne Akzentfarbe, direktes Öffnen in Google Präsentationen, weitere Einstellungsmöglichkeiten.

**Getan:**
- **Präsentations-Design überarbeitet:** `backend/app/services/design.py` (neu) — Liste zuverlässig verfügbarer Schriftarten, Default-Farbschema, `validate_design()` mit Feld-für-Feld-Fallback (nie Alles-oder-nichts). `gemini_client.generate_presentation_outline()` liefert jetzt zusätzlich ein von Gemini passend zur Design-Beschreibung gewähltes Farbschema (Hex-Codes, Kontrast-Vorgabe) sowie Schriftart aus der erlaubten Liste. `presentation.py` komplett umgebaut: 16:9-Breitbildformat (vorher veraltetes 4:3), Hintergrundfarbe/Textfarbe/Schriftart/Akzent-Balken pro Folie aus dem Design angewendet, saubere manuelle Layouts statt Standard-Platzhaltern.
- **Weitere Einstellungen ergänzt** (Nutzer-Auswahl aus vorgeschlagenen Ideen): Ton/Stil des Texts (Formell/Locker/Einfach erklärt), Ziel-Foliezahl als Hinweis (kurz/mittel/lang), Farbschema-Presets (Minimal/Bunt/Dunkel/Corporate) als Schnellauswahl-Buttons, die die Freitext-Design-Beschreibung befüllen, sowie Checkboxen an den Quellen zur gezielten Auswahl, welche Dateien in eine Präsentation einfließen (Backend unterstützte `source_ids` bereits, jetzt auch UI dafür — Auswahl-State in `App.tsx` gehoben, da `SourcesPanel` und `PresentationPanel` ihn beide brauchen).
- **Akzentfarbe auf Grün geändert:** `index.css`, Light `#16a34a` / Dark `#4ade80`, jeweils mit passendem Kontrasttext.
- **"In Google Präsentationen öffnen":** Einfache Variante gewählt (statt vollständiger OAuth-Integration, um keine zusätzlichen Google-Cloud-Secrets/Angriffsfläche für dieses Single-User-Tool einzuführen) — nach dem PPTX-Download öffnet ein Button `https://drive.google.com/drive/my-drive` in neuem Tab; Nutzer zieht die Datei manuell per Drag & Drop hinein, Google konvertiert automatisch zu Google Slides.
- Vollständige Test-Abdeckung für die neuen Backend-Pfade (Design-Validierung, Farbanwendung, 16:9-Format) ergänzt/angepasst.

**Bild-Generierung — implementiert, dann wieder entfernt (wichtige Korrektur):**
- Nutzer fragte nach echten KI-generierten Bildern pro Folie statt nur Farben/Typografie. Recherche ergab scheinbar einen kostenlosen Tier für "Nano Banana" (`gemini-2.5-flash-image`, 500 Bilder/Tag gratis) — auf dieser Basis mit Zustimmung des Nutzers implementiert: Bild-Prompt pro Folie im Gliederungs-Schema, `generate_slide_image()` im Gemini-Client, parallele Generierung mit `ThreadPoolExecutor` (max. 4 gleichzeitig) im Presentations-Router, Fehlerabsicherung pro Folie (ein fehlgeschlagenes Bild darf nicht die ganze Präsentation verhindern), neues Bild+Text-Split-Layout in `presentation.py`.
- **Live-Test deckte auf, dass die Recherche falsch bzw. veraltet war:** Beim echten Testlauf lieferte die Gemini-API `429 RESOURCE_EXHAUSTED`, `limit: 0` für `gemini-2.5-flash-preview-image` im Free Tier — auf dem tatsächlichen API-Key-Zugang existiert für Bildgenerierung aktuell kein kostenloses Kontingent (weitere Recherche bestätigte: die 500-Bilder-Angabe bezog sich offenbar nur auf die AI-Studio-Oberfläche, nicht auf den programmatischen API-Zugriff, oder war schlicht veraltet). Nutzer explizit auf diesen Irrtum hingewiesen.
- **Positiv:** Die eingebaute Fehlerabsicherung griff korrekt — trotz fehlgeschlagener Bildgenerierung wurde die Präsentation trotzdem vollständig erstellt (nur ohne Bilder), kein Absturz.
- **Nutzer-Entscheidung:** Da Bildgenerierung auf diesem Account echtes Geld kosten würde (~0,02-0,13$/Bild) und das ursprüngliche Projektziel "läuft kostenlos" war, wurde das Feature auf Wunsch des Nutzers **vollständig wieder entfernt** (nicht nur deaktiviert) statt als totes/kostenpflichtiges Feature im Code zu belassen: `generate_slide_image()`, `_generate_images()`, `image_prompt`-Schema-Feld, Bild-Layout in `presentation.py`, `include_images`-Option in Schema/API/Frontend, `gemini_image_model`-Setting — alles rückgebaut. Tests entsprechend bereinigt.

**Probleme / Debugging:**
- Beim ersten Download-Test in derselben Browser-Session wurde die neue Datei vom Browser automatisch als `praesentation (1).pptx` gespeichert (da `praesentation.pptx` vom vorherigen Testlauf schon existierte) — meine erste Inhaltsprüfung lief versehentlich gegen die alte Datei und zeigte einen irreführenden `_NoFill`-Fehler beim Auslesen der Hintergrundfarbe. Nach Prüfung des tatsächlichen `ls`-Outputs (zwei Dateien, unterschiedliches Datum) auf die richtige Datei zugegriffen — kein echter Bug im Code.
- `python-pptx`-Typing: `Presentation` ist eine Fabrikfunktion, kein Typ — `prs: Presentation` als Parameter-Annotation schlug in `mypy` fehl (`is not valid as a type`). Behoben durch `Any` als Parametertyp für die internen Hilfsfunktionen.

**Ergebnis:** Präsentationen haben jetzt ein durchgängiges, zur Design-Beschreibung passendes Farbschema, passende Schriftart, 16:9-Format und einen Akzent-Balken — deutlich weniger "lieblos" als der reine Standard-Look vorher, ganz ohne laufende Kosten.

**Nächster Schritt:** Wie zuvor — Deployment (Render, dann Cloudflare Pages).

---

## 2026-09-16 — Großer Ausbau beschlossen: Multi-User, mehr Kernfunktionen, größerer DevOps-Umfang

Nutzer war mit dem Umfang des Projekts nicht zufrieden und wollte ein "größeres Projekt", statt jetzt zu deployen. Nach Rückfrage (AskUserQuestion) gewünschter Umfang: mehrere Notebooks, weitere Quellentypen (URL/YouTube/Audio), Notizen pro Quelle, echte Nutzerverwaltung (Supabase Auth), zusätzliche Seiten (Notebook-Übersicht, Verlauf, Dashboard), größerer DevOps-Ausbau (Staging, E2E-Tests, Error-Monitoring, versionierte Migrationen) — alles nur soweit kostenlos umsetzbar.

**Vorgehen:** Wechsel in den Plan-Modus, gemeinsam mit dem Nutzer einen Phasenplan (0-5) erarbeitet und per `ExitPlanMode` freigegeben. Vorgehen: Phase für Phase mit Freigabe nach jeder Phase; voller Plan liegt zusätzlich unter `~/.claude/plans/nested-dreaming-raven.md`; laufender Status/Phasenliste wird in der lokalen `TODO.md` gepflegt (nicht im Repo, wie bereits etabliert).

**Deployment (Render/Cloudflare) zurückgestellt:** Ergibt mehr Sinn, zuerst die Multi-User-Grundlage (Phase 1) zu bauen, statt jetzt die bald überholte Single-User-Version live zu schalten.

### Phase 0 — Kostenlos-Machbarkeit von Audio verifiziert ✅

Nach dem Bild-Generierungs-Vorfall (Recherche sagte "kostenlos", Live-Test zeigte `limit: 0`) diesmal von Anfang an mit einem echten API-Call statt nur Recherche geprüft, bevor Audio als Quellentyp gebaut wird:

- **Audio-Input beim Chat-Modell (`gemini-3.6-flash`):** Live mit einer WAV-Testdatei geprüft — ✅ Erfolgreich, kostenlos (kein Quota-Fehler), Transkription korrekt. Da reale Nutzer-Uploads (mp3/wav/m4a) gültige Container-Header haben, ist das der relevante Pfad für Phase 3.

**Ergebnis:** Anders als bei der Bildgenerierung — hier hält sich die Erwartung zum kostenlosen Zugang. Phase 3 (Audio-Datei als Quellentyp) wird wie geplant umgesetzt.

**Nächster Schritt:** Phase 1 — Supabase Auth + Multi-Notebook-Datenmodell + versionierte Migrationen + Frontend-Routing.

---

## 2026-09-16/17 — Phase 1 abgeschlossen: Supabase Auth + Multi-Notebook + versionierte Migrationen

**Getan:**
- Bereits vorhandene Test-Quellen (CV.pdf, Lebenslauf) vor dem Schema-Umbau auf Nutzerwunsch gelöscht (DB-Einträge per API, verwaiste Storage-Objekte manuell per Python-Skript bereinigt, da `DELETE /sources/{id}` sie zu diesem Zeitpunkt noch nicht aus dem Storage entfernte — siehe unten).
- **DB-Schema umgebaut auf versionierte Migrationen:** `backend/supabase/schema.sql` zu `backend/supabase/migrations/0001_initial_schema.sql` verschoben (per `git mv`), neue `0002_multi_user_notebooks.sql`: Tabelle `notebooks` (user_id → `auth.users`), Pflichtspalte `sources.notebook_id`, RLS-Policies auf allen drei Tabellen als Tiefenverteidigung (Backend nutzt weiterhin `service_role`, umgeht RLS technisch, filtert aber zusätzlich explizit nach `notebook_id`/`user_id` in jeder Query — RLS ist zusätzliche Absicherung, kein alleiniger Schutz), `match_chunks`-RPC um `target_notebook_id`-Filter erweitert (sonst hätte die Ähnlichkeitssuche versehentlich quer über alle Notebooks/Nutzer gesucht). Vom Nutzer im SQL Editor ausgeführt.
- **Backend:** `pyjwt` als neue Dependency. `app/auth.py`: `get_current_user_id()` als FastAPI-Dependency, verifiziert Supabase-JWTs — verzweigt zur Laufzeit zwischen legacy HS256 (`SUPABASE_JWT_SECRET`) und neueren asymmetrischen Signing Keys (JWKS-Endpunkt), da beide Verfahren je nach Projekt-Konfiguration vorkommen können und der Algorithmus im Token-Header selbst steht. Neuer `app/services/notebooks_store.py` (CRUD + `require_owned_notebook_id`-Dependency, die Auth + Eigentümerschaft in einem Schritt prüft) und `app/routers/notebooks.py`. Bestehende Router (`sources.py`, `chat.py`, `presentations.py`) auf `/notebooks/{notebook_id}/...`-Pfade umgestellt, jeder Endpunkt jetzt notebook-scoped und auth-geschützt. `vector_store.py` und `storage.py` entsprechend um `notebook_id`/`user_id` erweitert; Storage-Pfadschema neu `{user_id}/{notebook_id}/{source_id}/{filename}`.
- **Nebenbei behoben (aus der TODO-Liste vorgezogen):** `DELETE /sources/{id}` löscht jetzt auch die Datei aus dem Supabase-Storage-Bucket (`storage.delete_source_file()`), nicht mehr nur aus der DB — vorher blieben gelöschte Dateien im Bucket verwaist liegen. Ebenso räumt `DELETE /notebooks/{id}` jetzt alle zugehörigen Storage-Dateien mit auf, bevor das Notebook (und per Cascade seine Quellen/Chunks) gelöscht wird.
- **Backend-Tests umgebaut:** neue `tests/conftest.py` mit `client`-Fixture (FastAPI `dependency_overrides` für Auth statt Monkeypatching, da es eine echte Dependency ist) und gemockter Notebook-Eigentümerschaft. Alle bestehenden Tests an die neuen notebook-scoped Pfade angepasst, neue Tests für `notebooks`-Router, `auth.py` (u.a. HS256-Token-Verifikation, falsches Secret, falsche Audience) und die Storage-Löschung. 39 Tests grün, `ruff`/`mypy` sauber.
- **Frontend:** `@supabase/supabase-js` + `react-router-dom` installiert. Neuer `src/lib/supabaseClient.ts`, `AuthContext`/`useAuth` (Context-Value in eigene Datei ausgelagert, um eine `oxlint`-Fast-Refresh-Warnung sauber zu beheben, statt sie zu ignorieren). Neue Seiten: `LoginPage`, `SignupPage`, `DashboardPage`, `NotebooksListPage` (Notebook-Übersicht mit Erstellen/Umbenennen/Löschen), `NotebookPage` (bisheriges 3-Panel-UI, jetzt pro Notebook). `ProtectedRoute` leitet nicht eingeloggte Nutzer zu `/login`. `api.ts` komplett umgebaut: jeder Request hängt automatisch `Authorization: Bearer <token>` an, alle URLs notebook-scoped. Akzentfarbe/Design-System unverändert übernommen (mobile-first, wie in den Memories festgehalten).
- Frontend-`.env.local` um `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` ergänzt (Anon-Key bewusst öffentlich/im Frontend, anders als der Service-Key im Backend).

**Live-Verifikation (vollständiger End-to-End-Test mit zwei echten Test-Accounts):**
1. **User A** registriert (`notebooklmklon-usera@mailinator.com`, echter, öffentlich einsehbarer Wegwerf-Posteingang für den Bestätigungslink) → E-Mail bestätigt → eingeloggt → Notebook "Notebook A - Katzen" erstellt → Markdown-Datei hochgeladen → Chat-Frage gestellt, korrekt beantwortet mit Zitat. Kompletter Auth+Daten-Kreislauf funktioniert.
2. Logout getestet — funktioniert, zurück zu `/login`.
3. **User B** registriert und eingeloggt (separater Account).
4. **Isolationstest bestanden:** User B sieht in der Notebook-Übersicht korrekt eine **leere Liste** (nicht Notebook A). Direkter URL-Zugriff auf User As Notebook-ID (`/notebooks/{id-von-A}`) liefert korrekt **"Notebook nicht gefunden"** (404) — keine Quellen, kein Chatverlauf von User A sichtbar. Row-Level-Isolation funktioniert wie geplant.

**Probleme / Debugging:**
1. **`example.com` als Signup-E-Mail abgelehnt:** Supabase erkennt offensichtlich unechte Domains und blockt sie (`Email address "...@example.com" is invalid`). Gelöst durch Umstieg auf einen echten, öffentlich einsehbaren Wegwerf-Mailanbieter (mailinator.com), um Bestätigungslinks ohne Zugriff auf ein echtes Postfach abrufen zu können.
2. **Bestätigungslink zweimal über das `find`-Tool abgerufen kam abgeschnitten zurück** (fehlende `type=signup&redirect_to=...`-Parameter bzw. gekürzter Token) — führte zu einer fehlgeschlagenen Verifikation (Redirect zu `/login` statt `/dashboard`, später `"Email not confirmed"` beim Login-Versuch). Kein App-Bug, sondern eine Einschränkung des Browser-Automatisierungs-Tools beim Extrahieren von Link-Text. **Gelöst:** vollständigen E-Mail-Inhalt stattdessen direkt über die öffentliche Mailinator-API (`/api/v2/domains/public/messages/{id}`) als Rohtext abgerufen, daraus den ungekürzten Token entnommen und den Bestätigungslink manuell korrekt zusammengesetzt.
3. **Supabase E-Mail-Rate-Limit erreicht** (`email rate limit exceeded`) beim zweiten Signup-Versuch von User B — der kostenlose Supabase-Mailer hat ein niedriges Limit. Kein Fehler im eigenen Code; nach kurzer Wartezeit (Sessionsunterbrechung bis zum nächsten Tag) erneut versucht, danach erfolgreich.
4. **Login-Formular reagierte zunächst nicht zuverlässig auf schnell aufeinanderfolgende `click`+`type`-Aktionen** des Automatisierungstools (Passwortfeld blieb leer, `"Fülle dieses Feld aus"`-Validierungshinweis erschien trotz sichtbar getippten Zeichen in einem Zwischenschritt). Kein Bug im eigentlichen Code — durch Trennen von Klick und Eingabe in getrennte Tool-Aufrufe mit kurzer Wartezeit dazwischen zuverlässig reproduzierbar gelöst.
5. Ein Klick auf einen Mailinator-Link löste kurzzeitig einen `chrome-extension://`-Zugriffsfehler im Browser-Automatisierungstool aus (Cross-Extension-Zugriff blockiert) — behoben durch erneute Navigation zur normalen URL statt Klick auf das Link-Element.

**Nächster Schritt:** Freigabe des Nutzers für Phase 1 einholen (Test war erfolgreich, aber Bestätigung steht noch aus), dann Phase 2 — Verlauf (History) für Chats und Präsentationen.

---

## 2026-09-17 — Phase 2 abgeschlossen: Verlauf (History) für Chats und Präsentationen

Nutzer hat Phase 1 freigegeben ("Nein, du kannst weiter machen"). Direkt mit Phase 2 fortgefahren.

**Getan:**
- **Migration `0003_history.sql`:** neue Tabellen `chat_messages` (notebook_id, role, content, citations jsonb) und `presentations` (notebook_id, title, topic, storage_path, design jsonb), RLS-Policies nach demselben Muster wie zuvor. Zusätzlich ein **neuer Storage-Bucket `presentations`** — bewusst getrennt vom bestehenden `sources`-Bucket, da dieser eine MIME-Type-Restriktion auf PDF/Markdown hat, die PPTX-Dateien abgelehnt hätte. Bucket-Erstellung diesmal direkt per SQL (`insert into storage.buckets ...`) statt manuell im Dashboard — funktional identisch zur Dashboard-UI, aber versioniert und reproduzierbar; das war vorher nicht bekannt/genutzt worden (siehe damalige Einrichtung des `sources`-Buckets manuell im Dashboard).
- **Backend:** neuer `history_store.py`-Service (Chat-Nachrichten und Präsentationen: insert/list/get). `storage.py` um Präsentations-Upload/-Download/-Löschung erweitert. `chat.py`: jede Frage und Antwort wird jetzt in `chat_messages` gespeichert, neuer `GET /notebooks/{id}/chat/history`-Endpoint. `presentations.py`: die generierte PPTX wird jetzt zusätzlich in Storage hochgeladen und als DB-Eintrag gespeichert (Original-Verhalten — sofortiger Download als Antwort — bleibt erhalten), neue Endpoints `GET /notebooks/{id}/presentations` (Liste) und `GET .../presentations/{id}/download` (erneuter Download aus dem Storage-Bucket). `notebooks.py`: Löschen eines Notebooks räumt jetzt zusätzlich die Präsentations-Storage-Dateien auf (analog zu den Quellen-Dateien aus Phase 1).
- **Backend-Tests:** bestehende Chat-/Presentations-Tests um die neuen History-Aufrufe erweitert (gemockt), neue Tests für `history_store.py` (mit einem kleinen Fake-Query-Objekt statt echtem Supabase-Client) sowie für die neuen Endpoints (Chat-Verlauf laden, Präsentationen auflisten, herunterladen, 404 bei fehlender Präsentation). 46 Tests grün, `ruff`/`mypy` sauber.
- **Frontend:** `api.ts` um `getChatHistory`, `listPresentationHistory`, `downloadPresentation` erweitert. `ChatPanel` lädt beim Öffnen eines Notebooks automatisch den gespeicherten Chatverlauf (mit Ladezustand und stillem Fallback bei Fehlern, damit der Chat trotzdem nutzbar bleibt). Neue Komponente `PresentationHistoryPanel` (zeigt vergangene Präsentationen mit Datum, Download-Button pro Eintrag; blendet sich komplett aus, wenn keine Präsentationen vorhanden sind, um die Seite bei einem frischen Notebook nicht unnötig zu füllen). `PresentationPanel` bekommt einen `onPresentationCreated`-Callback, den `NotebookPage` nutzt, um die History-Liste nach jeder neuen Erstellung sofort zu aktualisieren (`refreshKey`-Pattern statt Re-Mount).

**Probleme / Debugging:**
1. **`oxlint`-Warnung `set-state-in-effect`** in `ChatPanel`: `setIsLoadingHistory(true)` stand als allererste, synchron ausgeführte Anweisung direkt im Effect-Body. Behoben, indem die Ladelogik in eine `async`-Funktion innerhalb des Effects verschoben wurde, die zusätzlich per `cancelled`-Flag beim Unmount/Notebook-Wechsel abgebrochen wird — das behebt nicht nur die Lint-Warnung, sondern auch eine potenzielle Race Condition (falls der Nutzer sehr schnell zwischen Notebooks wechselt, bevor die vorherige Anfrage zurückkommt).
2. **Live-Test deckte einen einmaligen `500 Internal Server Error` beim ersten Laden von "Frühere Präsentationen" auf** (Backend-Log: `httpx.RemoteProtocolError: Server disconnected`). Kein Bug im eigenen Code — ein transienter Verbindungsabbruch zur Supabase-API beim allerersten Request nach Server-Neustart. Da React im Entwicklungsmodus (StrictMode) Effects zweimal ausführt, griff im selben Moment ein zweiter, unabhängiger Versuch, der erfolgreich war (`200 OK` direkt im Log danach) — der Fehler war dadurch im UI praktisch nicht sichtbar. Nach einem Seiten-Reload bestätigt: kein wiederkehrendes Problem. **Für die Produktion vorgemerkt** (kein Blocker für Phase 2, aber in `TODO.md` als Robustheits-Punkt festgehalten): In der Produktions-Build läuft kein StrictMode-Doppelaufruf mehr, ein einzelner transienter Verbindungsfehler würde dem Nutzer dort ohne automatischen Retry angezeigt.
3. Live-Verifikation vollständig durchlaufen: Chat-Frage gestellt (korrekt beantwortet, Zitat aus `vulkane.md`), Seite neu geladen → Chatverlauf korrekt aus der DB wiederhergestellt (identische Frage/Antwort/Zitat). Präsentation "Vulkane in Europa" erstellt → erscheint sofort in "Frühere Präsentationen" mit korrektem Titel/Datum → erneuter Download über den Verlauf-Button lieferte `200 OK` vom neuen `/download`-Endpoint (Datei kam korrekt aus dem `presentations`-Bucket zurück, nicht neu generiert).

**Nächster Schritt:** Freigabe für Phase 2 einholen, dann Phase 3 — weitere Quellentypen (URL, YouTube, ggf. Audio).

---

## 2026-09-17 — Echter Bug vom Nutzer gefunden: RAG zitierte irrelevante Quellen

Nutzer bat darum, den PDF-Upload-Pfad zu testen (bisher nur Markdown getestet). Test-PDF (`delfine.pdf`, per `fpdf2` temporär erzeugt) erfolgreich hochgeladen, Text-Extraktion via `pypdf` korrekt (`# Delfine ...`). Chat-Frage zum PDF-Inhalt korrekt beantwortet ("40 Jahre", "30 km/h") — **aber** der Nutzer bemerkte selbst, dass die Zitate zusätzlich die völlig themenfremde `vulkane.md`-Quelle enthielten, obwohl diese keinerlei Bezug zur Delfin-Frage hatte.

**Root Cause gefunden und mit echten Werten verifiziert** (nicht nur vermutet): `match_chunks` (die Supabase-RPC für die Ähnlichkeitssuche) liefert immer bis zu `match_count` (Standard 6) Treffer zurück, unabhängig davon, wie unähnlich sie inhaltlich sind — es gibt keinerlei Mindest-Relevanz-Schwelle. Bei nur wenigen Chunks im Notebook (wie hier: nur 2) werden dadurch zwangsläufig auch komplett irrelevante Chunks "top-6", einfach weil nichts Besseres konkurriert.
- Per direktem Test der Gemini-Embeddings kalibriert: Ähnlichkeit der Delfin-Frage zu einem tatsächlich passenden Delfin-Chunk = **0,81**; zur völlig themenfremden Vulkane-Quelle = **0,53**. Deutliche Lücke zwischen "relevant" und "irrelevant" vorhanden, nur bisher nicht genutzt.

**Fix:**
- Neues Setting `chat_similarity_threshold` (Standard `0.6`, konfigurierbar über `.env`) in `backend/app/config.py`.
- In `backend/app/routers/chat.py`: nach der Ähnlichkeitssuche werden Treffer unterhalb des Schwellenwerts vor der Verwendung als Chat-Kontext **und** als Zitate herausgefiltert (`vector_store.similarity_search` liefert weiterhin die rohen Top-6, die Filterung passiert im Router).
- Regressionstest `test_chat_filters_out_low_similarity_matches` ergänzt (nutzt exakt die vor Ort gemessenen Werte 0,81/0,53 als Testdaten), der belegt: bei gemischten Treffern landet nur der relevante Chunk im Gemini-Kontext und in den zurückgegebenen Zitaten.
- **Live erneut verifiziert nach dem Fix:** Frage "Welche Geräusche machen Delfine?" (Notebook enthielt zu diesem Zeitpunkt nur noch `vulkane.md`) lieferte jetzt korrekt **keine Zitate mehr** statt fälschlich die Vulkan-Quelle zu zitieren.

**Nebenproblem beim Testen:** Ein `pkill`-Befehl aus der vorherigen Aufräum-Routine war durch eine Nutzer-Unterbrechung nie ausgeführt worden — der alte Backend-Prozess (ohne den Fix) lief weiter auf Port 8000, wodurch der erste Verifikationsversuch fälschlich noch die alte, fehlerhafte Antwort zeigte (`address already in use` beim Versuch, den "neuen" Server zu starten, der in Wahrheit gar nicht lief). Gefunden durch Prüfen von `/tmp/uvicorn.log`, behoben mit `lsof -ti:8000 | xargs kill -9` vor dem eigentlichen Neustart. Für zukünftige Server-Neustarts nach einer unterbrochenen/abgelehnten Aufräum-Aktion: immer verifizieren, dass der alte Prozess wirklich beendet wurde, bevor Testergebnisse als "nach dem Fix" gewertet werden.

**Testdaten-Hinweis:** Zur Kalibrierung wurde kurzzeitig ein synthetischer Test-Chunk direkt in die Datenbank eingefügt (nicht über die reguläre Upload-Pipeline) und danach wieder entfernt — diente nur dem Vergleich der Ähnlichkeitswerte, keine dauerhafte Datenänderung.

**Ergebnis:** PDF-Upload-Pfad vollständig verifiziert (Upload → Extraktion → Embedding → Chat → Löschen inkl. Storage-Cleanup), zusätzlich ein echter RAG-Qualitätsbug gefunden und behoben, der bei jedem Notebook mit wenigen/thematisch gemischten Quellen aufgetreten wäre.

**Nächster Schritt:** Freigabe für Phase 2 (weiterhin ausstehend) einholen, dann Phase 3 — weitere Quellentypen (URL, YouTube, ggf. Audio).

---

## 2026-09-17 — Phase 3 abgeschlossen: weitere Quellentypen (URL, YouTube, Audio)

Nutzer hat mit "Ja, mach weiter mit Phase 3" freigegeben. Ziel: Notebooks sollen zusätzlich zu PDF/Markdown auch URLs, YouTube-Videos und Audiodateien als Quellen akzeptieren.

**Getan:**
- **Migration `0004_more_source_types.sql`:** erweitert die `sources.file_type`-CHECK-Constraint um `url`/`youtube`/`audio`. Da die ursprüngliche Constraint in `0001_initial_schema.sql` inline definiert wurde, hat Postgres ihr einen automatisch generierten Namen gegeben — die Migration ermittelt den echten Namen zur Laufzeit über `pg_constraint`/`pg_get_constraintdef` in einem `DO $...$`-Block, statt ihn zu erraten. Zusätzlich werden die Audio-MIME-Types zur `allowed_mime_types`-Liste des `sources`-Buckets hinzugefügt. Vom Nutzer im Supabase SQL Editor ausgeführt und bestätigt.
- **Neue Backend-Services:**
  - `web_extraction.py`: `extract_url_content(url)` per `trafilatura` (Fetch + Text-Extraktion mit `favor_recall=True`, Metadaten-Titel mit Fallback auf die URL selbst).
  - `youtube_extraction.py`: `extract_youtube_transcript(url)` per `youtube-transcript-api` (Video-ID-Extraktion für alle gängigen URL-Formate `v=`/`youtu.be/`/`embed/`/`shorts/`, Sprachpriorität DE vor EN, Titel-Fallback `"YouTube-Video {id}"`, da keine Titel-API ohne zusätzlichen Key verfügbar ist).
  - `gemini_client.transcribe_audio()`: nutzt `generate_content` mit `types.Part.from_bytes` für die Audiodatei.
- **Backend-Refactoring:** die vier Ingestion-Pfade (Datei-Upload, URL, YouTube, Audio) teilen sich jetzt eine gemeinsame `_ingest_source()`-Hilfsfunktion in `sources.py` (chunken, einbetten, in Storage ablegen, DB-Einträge anlegen) statt vier separater Implementierungen. Neue Endpoints `POST /notebooks/{id}/sources/url` und `POST /notebooks/{id}/sources/youtube`; `POST /notebooks/{id}/sources` (Datei-Upload) erkennt Audio-Dateiendungen (`.mp3/.wav/.m4a/.ogg`) und ruft `transcribe_audio()` statt der normalen Textextraktion auf.
- **Frontend:** `SourcesPanel` um zwei kompakte Eingabeformulare (URL/YouTube-Link + Absenden) erweitert, Dropzone akzeptiert zusätzlich Audio-Endungen, jede Quelle zeigt jetzt ein kleines Typ-Badge (PDF/MD/URL/YT/Audio). `api.ts` um `addUrlSource`/`addYoutubeSource` erweitert, `Source.file_type` entsprechend erweitert.
- **Neue/erweiterte Tests:** `test_gemini_client.py` (neu), `test_web_extraction.py` (neu), `test_youtube_extraction.py` (neu), `test_sources_api.py`/`test_storage.py`/`test_text_extraction.py` um URL/YouTube/Audio-Fälle erweitert. Backend-Testsuite jetzt **82 Tests, alle grün**, `ruff check .` und `mypy app tests` sauber. Frontend: `oxlint` sauber, `tsc -b && vite build` erfolgreich.

**Probleme / Debugging (die wichtigsten Funde dieser Phase):**

1. **`embed_texts()`-Batching-Bug — der bedeutendste Fund dieser Phase.** Beim ersten Live-Test mit einer realistisch langen Quelle (Wikipedia-Artikel "Octopus" über die neue URL-Funktion, 68 Chunks) blieb die Chat-Antwort auf Fragen zu dieser Quelle leer. Ursache: `embed_content()` wurde mit `contents=[str, str, ...]` als **flacher Liste** aufgerufen — die Gemini-API interpretiert eine flache String-Liste dabei als **ein einziges Multi-Part-Dokument** und liefert dadurch immer nur **1 Embedding** zurück, unabhängig von der Anzahl der übergebenen Texte. Live verifiziert: 68 Strings rein, 1 Embedding raus. Dieser Bug bestand seit der ursprünglichen Implementierung der Funktion, fiel aber nie auf, weil jede bisherige Testquelle (Markdown-Notizen, das Delfin-PDF) zufällig genau 1 Chunk erzeugte — "1 raus" sah dort korrekt aus. **Fix:** jeder Text wird jetzt einzeln als eigenständiges `types.Content(parts=[types.Part(text=t)])`-Objekt übergeben, wodurch die API sie als N unabhängige Dokumente batcht (live erneut verifiziert: 68 rein, 68 raus). Regressionstest `test_embed_texts_wraps_each_text_as_its_own_content` in `test_gemini_client.py` ergänzt, der die tatsächlich gesendeten `contents` auf `types.Content`-Instanzen und korrekte Länge prüft. **Lektion:** Kleine Testfixtures mit genau einem Chunk hatten diesen Bug systematisch verdeckt — größere, realistischere Testquellen waren nötig, um ihn aufzudecken.
2. **Nicht-atomare Ingestion — direkte Folge des Bugs oben.** Als `embed_texts` mit der falschen Chunk-Anzahl zurückkam, schlug der nachfolgende `insert_chunks`-Aufruf fehl (`zip()`-Längenmismatch) — aber Storage-Datei und `sources`-DB-Zeile waren zu diesem Zeitpunkt bereits angelegt. Ergebnis: eine "Geister"-Quelle mit 0 Chunks, die in der UI normal aussah, aber im Chat nie gefunden werden konnte, weil kein durchsuchbarer Inhalt existierte. Der Supabase-REST-Client bietet keine Mehrtabellen-Transaktionen. **Fix:** `_ingest_source()` sichert Storage-Upload und DB-Inserts jetzt manuell per Try/Except ab — schlägt irgendein Schritt nach dem Storage-Upload fehl, werden sowohl die Storage-Datei als auch eine ggf. bereits angelegte Source-Zeile wieder gelöscht, statt eine unbrauchbare Teilquelle zurückzulassen. Regressionstest `test_upload_source_cleans_up_on_chunk_insert_failure` ergänzt.
3. **`youtube-transcript-api`-Verhalten vor dem Schreiben von Code live per `inspect.signature()` geprüft** statt sich auf Suchergebnisse/Trainingsdaten zu verlassen (Konsequenz aus der früheren Fehleinschätzung beim Nano-Banana-Bildgenerierungs-Free-Tier) — bestätigte die tatsächliche Methode `YouTubeTranscriptApi().fetch(video_id, languages=[...])` und die relevanten Exception-Typen, bevor `youtube_extraction.py` geschrieben wurde.
4. **Browser-Automatisierungstool hing beim Hochladen einer echten 326-KB-WAV-Datei** ("Wird hochgeladen..." endlos, kein entsprechender Request im Backend-Log sichtbar). Kein App-Bug: direkte Prüfung per Standalone-Skript zeigte `transcribe_audio()` funktioniert korrekt (3,3s, korrekte Transkription), und eine direkte DB-Abfrage bestätigte, dass die Audio-Quelle serverseitig tatsächlich korrekt angelegt worden war (inkl. Chunk-Inhalt) — der Request war also durchgelaufen, nur das UI dieses einen Browser-Tabs zeigte es nie an (auch Folgenavigation im selben Tab hing danach weiter, obwohl `curl http://localhost:8000/health` sofort antwortete). **Gelöst** durch Schließen des hängenden Tabs und Öffnen eines neuen — danach zeigte das Notebook sofort korrekt alle vier Quellentypen mit intaktem Chatverlauf.
5. Für unabhängiges Testen anderer Audioformate (mp3/ogg) konnten im Sandbox-Netzwerk keine echten Beispieldateien heruntergeladen werden (Wikimedia lieferte 403, andere Versuche schlugen fehl). Transparent gehandhabt: mp3/wav/m4a/ogg sind laut Gemini-Dokumentation unterstützt und im Code entsprechend hinterlegt, aber nur WAV wurde tatsächlich live end-to-end verifiziert.

**Live-Verifikation (nach beiden Fixes, in einem frischen Browser-Tab):** Ein Notebook mit allen vier Quellentypen gleichzeitig — `vulkane.md` (MD), "Octopus" von Wikipedia (URL), ein YouTube-Video (YT), `wombats.wav` (Audio) — zeigt korrekte Badges für jeden Typ. Chat-Test pro neuem Quellentyp:
- **URL:** "Wie viele Herzen hat ein Oktopus laut Wikipedia?" → korrekt "drei Herzen" mit mehreren Octopus-Wikipedia-Zitaten.
- **Audio:** "Was graben Wombats?" → korrekt "komplexe unterirdische Baue" mit Zitat aus `wombats.wav` (dem transkribierten Audioinhalt).
- **Regressionstest der Relevanz-Filterung aus der vorigen Phase weiterhin bestätigt:** Fragen zu Delfinen/Delfingeräuschen bei einem Notebook ohne Delfin-Quelle lieferten weiterhin korrekt "keine Informationen" statt falscher Zitate aus themenfremden Quellen.

**Ergebnis:** Alle vier Quellentypen (PDF/MD, URL, YouTube, Audio) vollständig end-to-end verifiziert — Ingestion, Embedding, Chat-Retrieval mit korrekten Zitaten. Zwei reale Bugs gefunden und behoben (Embedding-Batching, nicht-atomare Ingestion), beide mit Regressionstests abgesichert. Backend: 82 Tests grün, `ruff`/`mypy` sauber. Frontend: `oxlint` sauber, Produktions-Build erfolgreich.

**Nächster Schritt:** Freigabe des Nutzers für Phase 3 einholen, dann Phase 4 — Notizen pro Quelle.

---

## 2026-09-17 — Phase 4 abgeschlossen: Notizen pro Quelle

Nutzer hat mit "Ja, mach weiter mit Phase 4" freigegeben. Ziel (wie im Ausbauplan festgehalten): einfache Freitext-Notizen pro Quelle, kein Text-Highlighting/Viewer — Quelle aufklappen, Notizen sehen/hinzufügen/löschen.

**Getan:**
- **Migration `0005_notes.sql`:** neue Tabelle `notes (id, source_id, content, created_at)`. Wie schon bei `chunks` keine eigene `user_id`-Spalte — Eigentümerschaft wird über die Kette `notes → sources → notebooks → auth.users` per RLS-Policy geprüft (Backend filtert zusätzlich explizit, RLS ist Tiefenverteidigung). Vom Nutzer im Supabase SQL Editor ausgeführt und bestätigt.
- **Backend:** neuer `notes_store.py`-Service (insert/list/delete, letzteres gibt `bool` zurück, ob wirklich eine Zeile gelöscht wurde — Muster aus `notebooks_store.delete_notebook` übernommen). Neuer Router `app/routers/notes.py`, gemountet unter `/notebooks/{notebook_id}/sources/{source_id}/notes`, mit einer eigenen `require_owned_source_id`-Dependency (baut auf der bestehenden `require_owned_notebook_id` auf und prüft zusätzlich, dass die Quelle zu diesem Notebook gehört, per `vector_store.get_source`). Endpoints: `GET`/`POST` auf der Notizen-Liste, `DELETE /{note_id}` (404 falls nicht gefunden). Leerer Notiz-Inhalt wird mit 422 abgelehnt.
- **Backend-Tests:** neue `test_notes_store.py` (Store-Funktionen mit Fake-Query-Objekt, analog zu `test_history_store.py`) und `test_notes_api.py` (Endpoints inkl. 404 bei fremder/fehlender Quelle, 422 bei leerem Inhalt, 401 ohne Auth). Backend-Testsuite jetzt **93 Tests, alle grün**, `ruff check .` und `mypy app tests` weiterhin sauber.
- **Frontend:** `api.ts` um `Note`-Typ und `listNotes`/`addNote`/`deleteNote` erweitert. `SourcesPanel.tsx`: jede Quelle bekommt einen "Notizen ▾/▲"-Toggle-Button neben dem Lösch-Button; aufgeklappt erscheint eine neue `SourceNotes`-Komponente (eigener State, lädt die Notizen erst beim ersten Aufklappen nach — kein unnötiger Request pro Quelle beim Laden des Notebooks), zeigt die Liste inkl. Lösch-Button pro Notiz und ein kompaktes Eingabeformular zum Hinzufügen. `App.css` mobile-first um `.source-notes`/`.note-list`/`.note-item`/`.note-toggle-button` ergänzt.

**Probleme / Debugging:**
1. **Alter Backend-Prozess ohne `--reload` lief noch mit dem Phase-3-Code**, als die neuen Notizen-Endpoints live getestet werden sollten (aus der Live-Verifikation der Vorphase noch offen) — dieselbe Fehlerklasse wie das bereits in Phase 2 dokumentierte Problem. Diesmal präventiv behandelt: vor dem Test explizit `lsof -ti:8000 | xargs kill -9`, Neustart, und zusätzlich der neue Endpoint-Satz direkt über `curl .../openapi.json` verifiziert (`/notebooks/{id}/sources/{id}/notes` taucht auf), bevor der Browser-Test überhaupt begann — kein erneuter Fehlalarm diesmal.
2. Keine weiteren funktionalen Probleme — Feature verlief beim ersten Live-Versuch fehlerfrei.

**Live-Verifikation (frischer Tab, Backend neu gestartet):** Bei `vulkane.md` "Notizen ▾" aufgeklappt → korrekt "Noch keine Notizen". Notiz "Ätna ist der aktivste Vulkan Europas" hinzugefügt → erscheint sofort in der Liste, Eingabefeld leert sich. **Persistenz-Test:** Seite neu geladen, Notizen-Bereich erneut aufgeklappt → Notiz korrekt aus der DB nachgeladen (nicht nur lokaler State). **Lösch-Test:** Notiz über ihren ✕-Button entfernt → sofort aus der Liste verschwunden, zurück zu "Noch keine Notizen". **Isolations-Test:** `wombats.wav` (andere Quelle im selben Notebook) aufgeklappt → zeigt korrekt keine Notizen, bestätigt saubere Trennung pro Quelle statt pro Notebook.

**Ergebnis:** Notizen-Feature vollständig end-to-end verifiziert (Erstellen, Anzeigen, Persistenz über Reload, Löschen, Isolation zwischen Quellen). Backend: 93 Tests grün, `ruff`/`mypy` sauber. Frontend: `oxlint` sauber, Produktions-Build erfolgreich.

**Nächster Schritt:** Freigabe des Nutzers für Phase 4 einholen, dann Phase 5 — DevOps-Ausbau.

---

## 2026-09-17 — Phase 5 (Teil 1): Sentry-SDK-Integration, E2E-Gerüst, Branch-Strategie — erster Durchlauf mit festem Subagent-Workflow

Session-Neustart, damit die vom Nutzer in `.claude/agents/` abgelegten Subagenten (`full-stack-developer`, `python-pro`, `code-reviewer` → intern `code-reviewer-pro`, `incident-responder`, `debugger`) als `subagent_type` verfügbar sind. Verifiziert: Agenten ließen sich nach dem Neustart problemlos aufrufen — der vorherige `Agent type 'full-stack-developer' not found`-Fehler trat nicht mehr auf. Ab jetzt gilt für dieses Projekt der feste Workflow **schreiben (`full-stack-developer`/`python-pro`, parallel in überschneidungsfreien Dateibereichen) → reviewen (`code-reviewer-pro`, `incident-responder`, parallel) → Bugs beheben (`debugger`)**, koordiniert vom Hauptagenten.

Umfang dieser Runde (mit dem Nutzer vorab abgestimmt): nur was **ohne neue Accounts** geht. Explizit nicht: echte Staging-Infra, echter Sentry-Account, GitHub-Actions-Secrets für E2E — diese Account-Schritte kommen später gemeinsam mit dem Nutzer.

**Gebaut:**
- **Backend-Sentry** (`python-pro`): `sentry_dsn`/`environment`-Settings in `app/config.py`, Init in `app/main.py` hart gated hinter leerem DSN (No-Op ohne Account), `sentry-sdk[fastapi]==2.69.2` exact-pinned, `.env.example` ergänzt, neuer Test `test_sentry_init.py`.
- **Frontend-Sentry** (`full-stack-developer`): `@sentry/react`, Init in `src/main.tsx` gated hinter `VITE_SENTRY_DSN`, kein Performance-Tracing.
- **E2E-Gerüst** (`full-stack-developer`): neues Top-Level-Verzeichnis `e2e/` (Playwright), 4 Smoke-Tests gegen `ProtectedRoute`/`AuthContext`-Verhalten (Login-/Signup-Formularfelder, Redirect zu `/login` bei fehlender Auth) — **tatsächlich lokal gegen einen selbst gestarteten Dev-Server ausgeführt und grün verifiziert**, nicht nur geschrieben.
- **CI-Workflow** `.github/workflows/e2e.yml`: nur `workflow_dispatch` + wöchentlicher `schedule`, bewusst nicht bei jedem Push (Gemini-Kontingent schonen).
- **README:** neuer Abschnitt „Branch-Strategie" (`main` = Produktion, `develop` = künftige Staging-Integrationsbranch).

**Review-Funde und Fixes (der eigentliche Wert des neuen Workflows):**
1. **`incident-responder` fand reproduziert (nicht nur vermutet), dass ein ungültiger `SENTRY_DSN` das gesamte Backend am Start hindern würde:** `_init_sentry()` lief als bare Top-Level-Call vor `app = FastAPI(...)` ohne try/except; `sentry_sdk.init(dsn='not-a-valid-dsn', ...)` wirft nachweislich `BadDsn`. Ein einzelner Tippfehler in einer künftigen Render-Env-Var hätte den kompletten Service lahmgelegt — genau die Art Fehler, vor der ein Observability-Feature schützen soll, nicht verursachen. **Von `debugger` behoben:** `sentry_sdk.init(...)` in try/except gewrappt, Fehlerfall wird nur geloggt, Service startet trotzdem.
2. **`incident-responder` fand außerdem, dass Sentry die eigenen Fehler strukturell nie gesehen hätte:** `CatchAllExceptionsMiddleware` schluckt Exceptions und gibt eine saubere 500-Response zurück, ohne `sentry_sdk.capture_exception()` aufzurufen — und Sentrys ASGI-Hook sitzt (per Quellcode-Inspektion von `sentry_sdk/integrations/starlette.py` bestätigt) außerhalb der über `add_middleware` registrierten Middlewares. Ohne Fix wäre das Monitoring nach echtem Account-Setup vollständig blind für genau die Fehler geblieben, die die Middleware normalisiert. **Von `debugger` behoben:** `capture_exception()` im except-Block ergänzt, zwei neue Regressionstests (`test_init_sentry_invalid_dsn_does_not_raise`, `test_unhandled_exception_reports_to_sentry`).
3. **`code-reviewer-pro` fand eine kleinere Race-Condition-Möglichkeit** im E2E-Health-Check (reiner `curl`-Verbindungstest statt Prüfung auf tatsächliche HTML-Antwort) sowie einige unkritische Verbesserungsvorschläge (Node-Version, Test-Robustheit) — als Follow-up vermerkt, nicht blockierend.
4. **Eigener Fund beim Gegenlesen:** eine bereits vor dieser Session bestehende, uncommittete `.gitignore`-Änderung (`.claude/settings.local.json` → `.claude/*`) hätte die neu erstellten Subagent-Definitionen dauerhaft von Git ausgeschlossen — obwohl der Subagent-Workflow laut Nutzerentscheidung dauerhaft genutzt werden soll. Mit dem Nutzer per Rückfrage geklärt: Agenten sollen eingecheckt werden, `.gitignore` entsprechend auf `.claude/settings.local.json` zurückgesetzt.

**Finale Checks (alle grün):** Backend `ruff check .` / `mypy app` / `pytest -q` → **97 Tests**. Frontend `npm run lint` (oxlint) / `npm run build` → sauber.

**Ergebnis:** Sentry-Integration (Backend + Frontend) und E2E-Gerüst stehen, beide No-Op ohne echte Accounts. Zwei reale, vom Review-Workflow gefundene Bugs behoben, bevor sie in Produktion hätten auffallen können — erster praktischer Beleg, dass sich der neue Subagent-Workflow lohnt. `develop`-Branch als Nächstes lokal anlegen (kein Push ohne Rückfrage).

**Nächster Schritt:** `develop`-Branch anlegen, committen (Push nur nach Rückfrage), TODO.md aktualisieren. Danach als eigener, gemeinsamer Schritt mit dem Nutzer: echte Staging-Infra (2. Supabase-Projekt, 2. Render-Service, Cloudflare-Previews), echter Sentry-Account, GitHub-Secrets für E2E.

---

## 2026-09-17 — Phase 5 (Teil 2, erste Hälfte): Staging-Infrastruktur live (Supabase + Render + Cloudflare Pages)

`main`/`develop` wurden gepusht (Nutzer-Freigabe erhalten). Ab jetzt gilt zusätzlich eine neue Standregel: **alles, was online sichtbar wird (Push, PR, etc.), braucht vorherige Freigabe des Nutzers — auch im Auto-Modus** (siehe Claude-Memory `require-approval-before-online-visible-actions.md`). Ebenso neu: **am Ende jeder Phase und vor jedem Commit gibt es eine kurze Stichpunkt-Zusammenfassung im Chat** (Claude-Memory `phase-end-summary-preference.md`).

Ziel dieser Session: den Nutzer (erstmals bei Supabase/Cloudflare, mit Auffrischung bei Render) Schritt für Schritt durch den Aufbau der Staging-Umgebung führen — Account-/Dashboard-Aktionen macht der Nutzer selbst, wie in diesem Projekt üblich.

**Aufgebaut:**
- **Zweites Supabase-Projekt** (Staging, komplett getrennt von der Dev-Datenbank) — alle 5 Migrationen (`0001`–`0005`) im SQL Editor eingespielt, `sources`-Bucket manuell angelegt (privat, 20 MB, PDF/Markdown/Audio-MIME-Types gleich vollständig statt wie beim Original in zwei Schritten).
- **Erster Render-Service überhaupt** (`notebooklm-klon-api-staging`, Branch `develop`, Root `backend/`) — Deployment war zuvor komplett pausiert, dies ist der erste reale Deploy des Backends. `render.yaml` im Repo ist für die spätere Produktion vorgesehen, für Staging wurde bewusst manuell im Dashboard angelegt (kollisionsfrei zum Blueprint-Namen `notebooklm-klon-api`). `/health` liefert `200 {"status":"ok"}`.
- **Erstes Cloudflare-Pages-Projekt überhaupt** (`notebooklm-klon`, Root `frontend/`, Production-Branch `main`) — Cloudflare läuft inzwischen technisch über eine vereinheitlichte "Workers mit Assets"-Architektur statt der klassischen Pages-Pipeline; Branch-Previews funktionieren trotzdem, nur über `workers.dev`-Alias-URLs (`<branch>-<project>.workers.dev`) statt `*.pages.dev`.

**Zwei reale Deploy-Bugs gefunden und behoben (nicht im Code, sondern in der Deploy-Konfiguration `frontend/wrangler.toml`):**
1. **Deploy schlug fehl trotz erfolgreichem Build:** `wrangler deploy` (der von Cloudflare jetzt genutzte vereinheitlichte Befehl) versteht das alte `pages_build_output_dir`-Feld nicht mehr, sondern erwartet einen `[assets]`-Block — Fehler `Missing entry-point to Worker script or to assets directory`. Live in der Cloudflare-Doku verifiziert (nicht geraten) und auf `[assets] directory = "./dist"` umgestellt.
2. **404 bei Direktaufruf jeder Unterseite** (`/login`, `/dashboard`, etc.) — Workers-Assets liefert standardmäßig nur Dateien, die 1:1 auf der Platte existieren, ohne SPA-Fallback. Gefunden beim eigenen End-to-End-Test (Browser-Tool zeigte "Frame is showing error page", `curl` bestätigte HTTP 404 exakt bei `/login`). Live in der Cloudflare-Doku verifiziert: `not_found_handling = "single-page-application"` im `[assets]`-Block ergänzt, liefert seitdem bei unbekannten Pfaden `index.html` mit 200 aus, React Router übernimmt dann clientseitig.
- Beide Fixes committed und (mit Nutzer-Freigabe) auf `main` und `develop` gepusht, `develop` jeweils per Fast-Forward auf `main` synchron gehalten (keine eigenen Commits auf `develop`).

**End-to-End-Verifikation (nach beiden Fixes):** Testkonto `nlmklon-staging-check@mailinator.com` über die Staging-Signup-Seite registriert, Bestätigungs-Mail über die öffentliche Mailinator-API abgerufen (gleiches Verfahren wie beim allerersten Supabase-Setup, siehe damaliger Eintrag) und den Verify-Link direkt aufgerufen. Login im Browser getestet: Frontend (Cloudflare Staging) → Supabase Auth (Staging) → Backend (Render Staging, `ALLOWED_ORIGINS` auf die Staging-Frontend-URL gesetzt) → Dashboard lädt korrekt ("Willkommen, ...", "0 Notebooks"). Komplette Kette funktional bestätigt.

**Nebenbei bemerkt (kein Fix nötig, nur notiert):** Der Bestätigungslink aus Supabase Auth zeigt aktuell auf `redirect_to=http://localhost:3000` (Standard-"Site URL" des neuen Projekts, noch nicht angepasst) — für den Confirm-Vorgang selbst unerheblich (die Bestätigung passiert serverseitig beim Aufruf von `/auth/v1/verify`, unabhängig vom Redirect-Ziel), aber für echte Nutzer später unschön. Sollte vor echtem Produktivbetrieb in den Supabase-Auth-Einstellungen auf die richtige Frontend-URL gestellt werden — als Punkt für später vermerkt (siehe TODO.md).

**Noch offen (Rest von Phase 5 Teil 2):** echter Sentry-Account + DSN eintragen, GitHub-Secrets für den E2E-Workflow anlegen.

---

## 2026-09-18 — Phase 5 (Teil 2, zweite Hälfte): Sentry-Account + Performance-Tracing + nutzerbezogene Fehlerzuordnung

Echter Sentry-Account angelegt (Backend-Projekt "FastAPI", Frontend-Projekt "React"), jeweils nur **Error Monitoring** aktiviert — Logging/Tracing/Profiling/Application Metrics bewusst abgewählt, um ungenutzte Kontingente nicht zu belegen.

**Bewusste Design-Entscheidung gegen das Sentry-Standard-Snippet:** Das von Sentry vorgeschlagene FastAPI-Beispiel setzt `send_default_pii=True` (schickt IP-Adressen, alle HTTP-Header und Cookies mit). Bewusst NICHT übernommen — stattdessen datensparsamer Ansatz: `sentry_sdk.set_user({"id": user_id})` gezielt in `app/auth.py` direkt nach erfolgreicher JWT-Verifikation ergänzt, sodass Fehler einem Nutzer zugeordnet werden können, ohne IP/Header/Cookies zu übertragen. SDK-Defaults vorab live geprüft (nicht geraten): `traces_sample_rate` und `send_default_pii` sind beide standardmäßig `None`/aus — unsere bisherige Implementierung ohne Performance-Tracing war also tatsächlich schon rein Error-Tracking, wie beabsichtigt.

**Performance-Tracing nachträglich doch aktiviert** (Backend + Frontend), nach kurzer gemeinsamer Abwägung: `traces_sample_rate`/`tracesSampleRate` konfigurierbar über Env-Var, Standardwert bewusst `1.0` (100%) für die aktuelle Staging-/Demo-Phase ohne echten Produktivtraffic — Begründung: bei so geringem Traffic besteht keine reale Kontingent-Gefahr (Sentry-Free-Tier laut Signup-Screen: 5.000.000 Spans/Monat, `errors` separat 5.000/Monat), während 100% Sampling sicherstellt, dass beim Durchklicken/Demonstrieren zuverlässig Daten im Dashboard erscheinen. Dokumentiert, dass der Wert bei echtem Produktivbetrieb auf ~0.1-0.2 reduziert werden sollte. Frontend: `Sentry.browserTracingIntegration()` ergänzt (API-Version live anhand der installierten `@sentry/react`-Typdeklarationen verifiziert, nicht geraten — `@sentry/tracing` als separates Paket ist seit SDK v7 abgelöst).

**Subagent-Workflow-Störung (Nebenbefund, kein App-Bug):** Der `full-stack-developer`-Agent für die Frontend-Änderung lief in eine Berechtigungssperre (alle Schreib-Tools wurden in dieser Session abgelehnt, vermutlich durch den zwischenzeitlichen Session-Neustart verursacht) — er hat sauber recherchiert (korrekte Sentry-API bestätigt), aber nichts geschrieben und das transparent gemeldet, statt es zu erzwingen. Die recherchierten Änderungen wurden danach vom Hauptagenten direkt übernommen. Der `python-pro`-Agent für die Backend-Seite meldete zusätzlich, während der Arbeit einen scheinbar injizierten "System-Reminder" in einem Tool-Ergebnis gesehen zu haben, und hat diesen zurecht als nicht vertrauenswürdig ignoriert, statt darauf zu reagieren — nach Prüfung durch den Hauptagenten stellte sich das als derselbe legitime Speicher-Neulade-Vorgang heraus, den die Session zeitgleich selbst erlebt hat, kein tatsächlicher Angriff.

**Review-Runde (`code-reviewer-pro` + `incident-responder`) fand einen echten Bug:** `sentry_traces_sample_rate: float = 1.0` in `app/config.py` hatte keine Eingabevalidierung — ein nicht als Zahl parsbarer Wert in der Env-Var (z.B. leer gelassenes Feld im Render-Dashboard) ließ `Settings()` bereits beim Modul-Import mit einer `pydantic`-`ValidationError` abstürzen, **noch bevor** das bestehende try/except in `_init_sentry()` greifen konnte — hätte also den kompletten Backend-Start verhindert, nicht nur Sentry deaktiviert. Der Reviewer hat das empirisch reproduziert (nicht nur vermutet) und zusätzlich bestätigt, dass out-of-range-aber-parsbare Werte (z.B. `5.0`, `-1`) unkritisch sind, weil `sentry_sdk` das intern selbst sicher abfängt. **Von `debugger` behoben:** pydantic `field_validator(mode="before")` ergänzt, der bei Parse-Fehlern auf den Standardwert zurückfällt (mit Log-Warnung) statt zu crashen — analog zum bereits bestehenden Fallback-Muster im Frontend (`Number.isFinite`-Check). Mit 7 neuen parametrisierten Tests abgesichert.

**Zusätzlicher Reliability-Fund, verifiziert statt vermutet:** Die Sorge, `sentry_sdk.set_user()` könnte bei FastAPIs synchronen Dependencies (laufen in einem Threadpool) zwischen gleichzeitigen Requests "durchsickern" (ein bekanntes, in der Sentry-Python-Community diskutiertes Risikomuster), wurde vom `incident-responder` nicht nur diskutiert, sondern mit zwei eigens geschriebenen Testskripten gegen die tatsächlich in diesem Projekt gepinnten Versionen (`sentry-sdk==2.69.2`) reproduziert: sequentielle UND parallele, verschachtelte Requests wurden geprüft — keine Vermischung zwischen Nutzern festgestellt. Als versionsabhängiges Verhalten vermerkt, das bei einem künftigen Upgrade von `sentry-sdk`/`starlette`/`anyio` erneut geprüft werden sollte.

**Finale Checks (nach dem Fix):** Backend `ruff`/`mypy`/`pytest -q` → **107 Tests grün**. Frontend `npm run lint`/`npm run build` → sauber.

**Ergebnis:** Sentry läuft jetzt mit echtem Account, Performance-Tracing (bewusst kalibriert für die aktuelle Phase) und einer datensparsamen Nutzer-Zuordnung für Fehlerreports. Ein zweiter, unabhängig vom ersten Review-Durchlauf gefundener echter Startup-Crash-Bug wurde vor dem Commit behoben — zweiter praktischer Beleg für den Wert der Review-Runde in diesem Workflow.

**Noch offen:** DSNs in Render/Cloudflare eintragen, GitHub-Secrets für den E2E-Workflow anlegen.

---

## 2026-09-18 — Phase 5 (Teil 2, Abschluss): Sentry-DSNs eingetragen, Uptime-Monitoring, E2E-Test gegen echte Staging-Umgebung

**Sentry fertig verdrahtet:** Backend-DSN in Render (`SENTRY_DSN`) und Frontend-DSN in Cloudflare Pages (`VITE_SENTRY_DSN`, Preview-Umgebung) eingetragen, Redeploy per "Retry deployment" ausgelöst, Konsole im Browser fehlerfrei verifiziert.

**Externes Uptime-Monitoring ergänzt (UptimeRobot, kostenlos):** zwei Monitore (Backend `/health`, Frontend-Root), 5-Minuten-Intervall. Bewusste Design-Entscheidung, das GETRENNT vom Playwright-E2E-Test zu lösen, statt den E2E-Test selbst im 5-Minuten-Takt laufen zu lassen — Begründung: GitHub Actions `schedule`-Trigger sind bei wenig aktiven Repos nicht zeitnah garantiert (können sich um viele Minuten verzögern), ein voller Browser-Test alle 5 Minuten ist unnötig schwer für einen reinen "ist es online?"-Check, und ein Render-Free-Tier-Cold-Start hätte bei so kurzem Intervall regelmäßig zu Fehlalarmen geführt. Praxisübliche Trennung: dediziertes Uptime-Tool für schnelle Verfügbarkeits-Checks, E2E-Suite für tiefere Funktionsprüfung in größeren Abständen. Netter Nebeneffekt: die 5-Minuten-Checks halten den Render-Service dauerhaft wach, wodurch der E2E-Test bei seinem wöchentlichen Lauf i.d.R. gar keinen Cold-Start mehr erlebt (siehe unten).

**E2E-Workflow umgebaut, um gegen die echte Staging-Umgebung statt einen lokalen CI-Dev-Server zu laufen:** `.github/workflows/e2e.yml` startet keinen lokalen Vite-Server mehr, Playwright läuft direkt gegen `https://develop-notebooklm-klon.piaheiss.workers.dev`. Neuer Test ("Echte Staging-Verbindung"): loggt sich mit dem bestehenden Testaccount ein und prüft den Redirect zum Dashboard. Damit wird ein grüner Lauf zu einem echten Health-Check der kompletten Kette (Cloudflare-Frontend → Supabase Auth → Render-Backend → Supabase-DB) statt nur eines UI-Smoke-Tests.

**Zwei echte, von der Review-Runde gefundene Probleme, beide behoben:**
1. **Der Test prüfte gar nicht das, was er zu prüfen vorgab.** `incident-responder` fand durch Code-Inspektion (nicht Vermutung): die "Willkommen"-Überschrift auf dem Dashboard rendert synchron und unabhängig vom Ausgang des `GET /notebooks`-Calls ans Backend (der läuft als Fire-and-Forget in einem `useEffect`) — der Test wäre also auch bei komplett offline liegendem Backend grün gewesen. Von `debugger` behoben: `page.waitForResponse(...)` registriert VOR dem Login-Klick (der Request feuert sofort beim Dashboard-Mount), explizite Prüfung auf Status 200 der echten Backend-Antwort statt nur auf sichtbaren Text. Live erneut gegen die echte Staging-Umgebung verifiziert — Laufzeit 44,8s, was zu einem echten Render-Cold-Start passt und bestätigt, dass der Test wirklich auf die reale Netzwerk-Antwort wartet.
2. **Sicherheits-"Zeitbombe" bei Playwright-Traces.** `code-reviewer-pro` fand: die globale `trace: 'on-first-retry'`-Einstellung hätte bei einem künftigen Wechsel des Reporters (aktuell zufällig entschärft, weil der `'github'`-Reporter keinen `playwright-report/`-Ordner erzeugt) das Klartext-Test-Passwort in einem für jeden lesbaren Artifact des öffentlichen Repos landen lassen können. Von `debugger` behoben: der neue Test läuft jetzt über ein eigenes Playwright-Project (`chromium-staging`, per Tag `@staging` von den übrigen 4 Tests getrennt) mit `trace: 'off'` — die anderen 4 Tests behalten ihr bisheriges Trace-Verhalten unverändert.

**Finale Verifikation:** Alle 5 Tests grün gegen die echte Staging-URL (inkl. Lauf ohne Credentials → sauberer Skip statt Fehlschlag, wie vorgesehen).

**Ergebnis:** Phase 5 (DevOps-Ausbau) ist damit vollständig abgeschlossen — Sentry (Error-Tracking + Performance-Tracing + Nutzer-Zuordnung), externes Uptime-Monitoring, und ein E2E-Test, der wirklich die komplette Staging-Kette verifiziert, statt nur oberflächlich UI zu prüfen. Nach dem Commit/Push (Freigabe erhalten) die beiden GitHub-Secrets angelegt (`E2E_TEST_USER_EMAIL`, `E2E_TEST_USER_PASSWORD`) und den Workflow manuell in echtem GitHub Actions ausgelöst — lief grün durch, nicht nur bei lokaler Verifikation.

---

## 2026-09-18 — Produktivumgebung real aufgebaut (Dev→Stage→QA-Gate→Prod-Zielbild umgesetzt)

Ausgangspunkt war eine gemeinsame Architektur-Grafik (Excalidraw, lokal, nicht im Repo — siehe Claude-Memory `diagram-files-stay-local.md`), bei der der Nutzer einen klassischen Dev→Stage→QA-Gate→Prod-Promotion-Workflow beschrieben hat. Dabei kam die entscheidende Frage auf: Supabase Free-Tier erlaubt nur **2 aktive Projekte gleichzeitig** — mit Dev (Cloud) und Staging waren beide Slots schon belegt, ein drittes Projekt für echte Produktion war also nicht direkt möglich.

**Lösung: Dev auf lokalen Supabase-CLI-Stack umgezogen, statt Cloud-Projekt.**
- Docker war bereits installiert, Supabase-CLI per `brew install supabase/tap/supabase` ergänzt.
- `supabase init` in `backend/` ausgeführt — die bestehenden 5 Migrationsdateien (`0001`–`0005`) wurden von der CLI automatisch als ihr eigenes Migrations-Verzeichnis erkannt, keine Anpassung nötig (die versionierte Migrations-Struktur aus Phase 1 zahlt sich hier aus).
- `config.toml` angepasst: Auth-Redirect von Standard `127.0.0.1:3000` auf `localhost:5173` korrigiert, `sources`-Bucket direkt als Code (`[storage.buckets.sources]`) definiert statt wie bei Staging manuell im Dashboard — sauberer, weil versioniert.
- `supabase start`: alle 5 Migrationen liefen automatisch durch, Bucket wurde automatisch erstellt. `backend/.env`/`frontend/.env.local` auf die (öffentlich bekannten) lokalen CLI-Standardwerte umgestellt. End-to-End im Browser verifiziert: Signup → sofortiger Login (lokaler Stack verlangt standardmäßig keine E-Mail-Bestätigung) → Dashboard lädt korrekt.
- Nutzer hat danach das alte Cloud-Dev-Projekt selbst im Supabase-Dashboard gelöscht (kein "Pause"-Button mehr vorhanden, nur noch "Delete") — Slot frei für ein echtes Produktions-Projekt.

**Neues, sauberes Produktions-Supabase-Projekt** nach demselben Verfahren wie Staging angelegt (5 Migrationen, `sources`-Bucket).

**`render.yaml` vervollständigt:** hatte bisher nur 4 von 8 tatsächlich benötigten Env-Var-Deklarationen (`SUPABASE_JWT_SECRET`, `SENTRY_DSN`, `ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE` fehlten) — ergänzt, zusammen mit `region: frankfurt` und `branch: main` (aus einem versehentlich entdeckten Render-Export des Staging-Service übernommen, um konsistent zur Staging-Region zu bleiben).

**Render-Produktion:** Der "Blueprint"-Menüpunkt war im "New +"-Menü nicht auffindbar (UI-Änderung) — stattdessen über den linken Sidebar-Punkt "Blueprints" gefunden, dort aber zunächst nur eine Export-Funktion für den bestehenden Staging-Service angetroffen (nicht das, was gebraucht wurde). Letztlich wurde der Produktions-Service manuell angelegt (analog zu Staging), mit denselben Werten (Branch `main`, Region Frankfurt), die eigentlich für die Blueprint-Variante vorgesehen waren — `render.yaml` bleibt trotzdem als korrekte Dokumentation/Vorlage im Repo.

**Echter Architektur-Fund bei Cloudflare, der die ursprüngliche Annahme korrigiert hat:** Die neue "Workers mit Assets"-Struktur (siehe schon Phase 5, `wrangler deploy` statt `wrangler pages deploy`) hat **kein** eingebautes Production/Preview-Split bei den Umgebungsvariablen wie die klassische "Pages"-Variante — es gibt nur eine einzige, projektweite Variablen-Liste, unabhängig vom Branch. Das hätte bedeutet, dass die für Staging gesetzten Werte (Preview) auch für einen Produktions-Build gegolten hätten. **Fix:** zweites, komplett eigenständiges Cloudflare-Projekt (`notebooklm-klon-prod`) für Produktion angelegt, mit eigenem, unabhängigem Variablen-Satz — analog zur bereits etablierten Trennung bei Supabase und Render.
- Nebenbefund beim Einrichten: ein expliziter `--name`-Override im Deploy-Command wurde von Cloudflares Build-System automatisch auf den Projektnamen zurückkorrigiert ("Failed to match Worker name... Overriding using the CI provided Worker name") — Cloudflare erzwingt also von sich aus, dass der Worker-Name zum Projektnamen passt, was Namens-Kollisionen zwischen den beiden Projekten strukturell verhindert. Der Override war unnötig, aber harmlos.

**Cross-Referenzen fertiggestellt:** `ALLOWED_ORIGINS` in Render-Produktion auf die neue Cloudflare-Prod-URL gesetzt; Supabase Auth "Site URL" im Produktions-Projekt korrekt auf die echte Frontend-URL gesetzt (nicht mehr der Standardwert `localhost:3000`, den wir bei Staging bewusst unkorrigiert gelassen hatten) — live per Bestätigungsmail verifiziert, dass der `redirect_to`-Parameter jetzt tatsächlich auf `https://notebooklm-klon-prod.piaheiss.workers.dev` zeigt statt auf `localhost:3000`.

**End-to-End-Verifikation (komplette Produktionskette):** Testkonto `nlmklon-prod-check@mailinator.com` registriert, Bestätigungsmail über die Mailinator-API abgerufen und verifiziert, Login getestet: Cloudflare-Produktion → Supabase Auth (Produktions-Projekt) → Render-Produktion → Datenbank-Query erfolgreich ("0 Notebooks"). Alle vier Bausteine der Produktionskette funktional bestätigt.

**Noch offen:** QA-Gate technisch über GitHub Branch-Protection-Regeln für `main` erzwingen (aktuell nur als Konvention/Diagramm dokumentiert, nicht technisch durchgesetzt).

---

## 2026-09-18 — Bug gefunden und behoben: UptimeRobot zeigt Produktions-Backend fälschlich als "down"

Nach dem Umstellen der UptimeRobot-Monitore von Staging auf Produktion (auf Nutzerwunsch, da Produktion die kritischere Umgebung ist) zeigte der Backend-Monitor durchgehend "down", obwohl `curl` denselben Endpunkt jederzeit mit `200 OK` beantwortete.

**Root Cause gefunden, nicht vermutet:** Der Incident-Detail-Response von UptimeRobot enthielt den Header `X-Render-Routing: no-deploy` sowie `Server: cloudflare` — Render liegt selbst hinter einer eigenen, von uns nicht konfigurierbaren Cloudflare-Zone. Recherche (siehe Cloudflare-Community-Threads) bestätigte: das ist ein bekanntes, dokumentiertes Problem — Cloudflare blockt standardmäßig bekannte Monitoring-Bot-Signaturen (u.a. UptimeRobots User-Agent/IP-Bereiche), auch wenn der Dienst dahinter einwandfrei läuft. Der parallel laufende Frontend-Monitor (eigene Cloudflare-Zone, von uns kontrolliert) war nicht betroffen — das hat die Diagnose auf "Renders Zone, nicht unsere" eingegrenzt.

**Alternative Tools kurz recherchiert, aber verworfen:** Kein zuverlässiger Beleg gefunden, dass ein bestimmtes kostenloses Monitoring-Tool garantiert an Renders (nicht unserer) Cloudflare-Konfiguration vorbeikommt — bewusst nicht geraten, stattdessen eine Lösung gewählt, die nicht vom Zufall abhängt.

**Fix:** Neuer, eigenständiger Cloudflare Worker `notebooklm-klon-health-proxy` (`infra/health-proxy/`, ca. 20 Zeilen Code) — ruft Renders `/health`-Endpoint serverseitig aus Cloudflares eigenem Netz ab (kein UptimeRobot-Header/IP im eigentlichen Render-Request mehr) und reicht die Antwort unverändert durch. UptimeRobot prüft jetzt diesen Worker statt direkt Render. Per `wrangler login` + `wrangler deploy` direkt lokal deployt (kein Git-Push-Workflow nötig für dieses kleine Stück Infrastruktur). Live mit exakt UptimeRobots eigenem User-Agent-String verifiziert (`curl -A "...UptimeRobot/2.0..."`) — liefert zuverlässig `200 {"status":"ok"}`.

**Ergebnis:** UptimeRobot-Backend-Monitor auf die neue Proxy-URL umgestellt, zeigt seitdem korrekt "Up". Guter Beleg dafür, Fehlermeldungen (Response-Header) genau zu lesen statt vorschnell "Netzwerkproblem" anzunehmen — der entscheidende Hinweis (`X-Render-Routing: no-deploy`, `Server: cloudflare`) stand die ganze Zeit in den Daten, die UptimeRobot selbst schon zeigte.

---

## 2026-09-18 — QA-Gate technisch durchgesetzt (GitHub Branch-Protection für `main`)

Der zu Beginn gemeinsam entworfene Dev→Stage→QA-Gate→Prod-Workflow (siehe Excalidraw-Grafik, lokal) war bis hierhin nur Konvention/Dokumentation, nicht technisch erzwungen. Letzter Baustein: eine echte GitHub-Branch-Protection-Regel für `main`, per `gh api` gesetzt (statt Dashboard-Klickpfad, direkt reproduzierbar):

- **Pull Request Pflicht** vor jedem Merge nach `main` — kein direkter Push mehr möglich.
- **Die drei CI-Checks aus `ci.yml`** (`Secret Scan (Gitleaks)`, `Frontend (Lint, Typecheck, Build)`, `Backend (Lint, Typecheck, Test)`) müssen grün sein, bevor gemergt werden kann.
- **`enforce_admins: true`** ("Include administrators") — bewusst aktiviert, nach expliziter Rückfrage beim Nutzer, welche Konsequenz das hat: die Regel gilt jetzt auch für den Repo-Owner selbst, nicht nur für hypothetische weitere Mitwirkende. Das ändert den bisher in dieser gesamten Session genutzten Workflow (direkter Push auf `main` nach Freigabe) — ab jetzt braucht jede Änderung an `main` einen Pull Request.
- **Keine Review-Pflicht** (`required_approving_review_count: 0`) — bewusst so, weil ein Solo-Projekt ohne weitere Mitwirkende sich sonst selbst blockieren würde (GitHub lässt eigene PRs i.d.R. nicht als Reviewer freigeben).
- Force-Push und Löschen von `main` zusätzlich verboten (Standard-Absicherung).
- Explizit als reversibel eingeordnet und mit dem Nutzer besprochen: die gesamte Regel bzw. einzelne Einstellungen (insb. "Include administrators") lassen sich jederzeit wieder ändern/entfernen.

**Ergebnis:** Aus dem in der Architektur-Grafik entworfenen QA-Gate ist jetzt eine technisch durchgesetzte Regel geworden, kein reines Diagramm/Versprechen mehr — passend zum ursprünglichen Nutzerwunsch, dass "Fehlerfrei? → main" wirklich nur nach bestandener CI passieren kann.

Direkt praktisch erprobt: der PROGRESS.md-Eintrag zu genau dieser Regel musste selbst schon über einen Pull Request laufen (direkter Push auf `main` war ab sofort nicht mehr möglich) — PR #1 erstellt, CI grün abgewartet, gemerged. Der neue Workflow funktioniert also nachweislich.

---

## 2026-09-18 — Impressum & Datenschutzerklärung ergänzt, Font-Hosting geprüft

Nutzerwunsch: rechtliche Absicherung gegen Abmahnungen (u.a. das bekannte deutsche Google-Fonts-Abmahnthema) — Muster-Impressum, Datenschutzerklärung, Fonts selbst hosten statt extern laden.

**Font-Check zuerst (bevor irgendwas umgebaut wurde):** Geprüft, ob überhaupt externe Fonts geladen werden (`index.html`, alle CSS-Dateien durchsucht) — Ergebnis: **nein**, es werden ausschließlich System-Schriftarten verwendet (`system-ui, 'Segoe UI', Roboto, sans-serif` als Fallback-Kette, siehe `frontend/src/index.css`). Kein Google-Fonts-Abmahnrisiko vorhanden, kein Umbau nötig — bewusst nichts "repariert", was nicht kaputt war.

**Neue Seiten `/impressum` und `/datenschutz`:**
- `ImpressumPage.tsx`: Muster-Impressum nach § 5 TMG mit klar sichtbaren `[Platzhalter]` für Name/Adresse/Kontakt — bewusst NICHT mit erfundenen Daten gefüllt (kann/darf ich nicht wissen, und ein falsch ausgefülltes Impressum ist selbst ein häufiger Abmahngrund). Deutlich sichtbarer Warnhinweis oben auf der Seite, dass die Platzhalter vor echtem Betrieb ausgefüllt werden müssen.
- `DatenschutzPage.tsx`: Datenschutzerklärung, inhaltlich auf die tatsächliche Architektur zugeschnitten statt generisches Boilerplate — beschreibt konkret Supabase Auth (Registrierung), hochgeladene Inhalte/Chatverlauf (Supabase DB+Storage), Google Gemini API als Auftragsverarbeiter mit Drittlandtransfer-Hinweis (USA), Hosting bei Render/Cloudflare, Sentry-Fehler-Tracking (mit dem Hinweis auf EU-Rechenzentrum Frankfurt und die bewusst datensparsame `set_user`-Zuordnung aus Phase 5), UptimeRobot, `localStorage`-Nutzung ohne Cookie-Consent-Pflicht (rein technisch notwendig), sowie die Standard-Betroffenenrechte nach DSGVO. Auch hier ein deutlicher Hinweis oben, dass das ein Entwurf/Vorlage ist und keine Rechtsberatung ersetzt.
- Neue `AppFooter.tsx`-Komponente mit Links zu beiden Seiten, in `App.tsx` einmal zentral eingebunden (Sibling zu `<Routes>`) statt in jeder Page einzeln — erscheint dadurch automatisch auf jeder Seite, auch ohne Login (gesetzlich gefordert: Impressum muss ohne Hürden erreichbar sein).
- CSS mobile-first ergänzt (`.legal-page`, `.legal-warning`, `.app-footer` in `App.css`), passend zu den bestehenden Farb-Variablen/Konventionen.

**Verifikation:** `npm run lint`/`npm run build` sauber, live im Browser geprüft (lokaler Dev-Server) — beide Seiten rendern korrekt, sind ohne Login erreichbar (nach `signOut()` erneut aufgerufen, funktioniert weiterhin), Footer erscheint konsistent.

**Ergebnis:** Rechtlich sinnvolle Grundabsicherung vorhanden, aber ausdrücklich als Entwurf markiert — die Platzhalter-Daten müssen vor echtem Live-Betrieb mit echten Nutzer:innen durch echte Angaben ersetzt werden, und beide Texte sollten im Zweifel fachlich gegengelesen werden.

---

## 2026-09-18 — Bug behoben: Chat-Fenster wuchs mit statt intern zu scrollen

Nutzerwunsch: das Chat-Fenster im Notebook soll bei vielen Nachrichten selbst scrollen, nicht die ganze Seite — und auf Desktop-Breite soll seine Höhe an der linken Spalte (Quellen/Präsentation) ausgerichtet sein, nicht an einem festen Viewport-Wert.

**Erster Teilfund:** `.chat-messages` hatte zwar schon `overflow-y: auto`, aber ohne `min-height: 0` auf dem Flex-Kind (Standard-Flexbox-Falle: ein Flex-Item wird nie kleiner als sein Inhalt, außer man setzt das explizit) griff das nie — der Container wuchs stattdessen einfach unbegrenzt mit.

**Zweiter, subtilerer Fund beim Umsetzen der Höhen-Angleichung an die linke Spalte:** `align-items: stretch` im CSS-Grid-Layout plus `min-height: 0`/`overflow: hidden` auf dem Grid-Element selbst reichte NICHT aus — mehrfach live mit injizierten Test-Nachrichten und `getBoundingClientRect()`/`scrollHeight`-Messungen verifiziert, nicht nur angenommen. Grund: die "automatische Minimalgröße wird bei Scroll-Containern ignoriert"-Sonderregel des Grid-Layouts gilt nur für das Element, das selbst `overflow` gesetzt hat (`.chat-messages`), nicht für dessen Elternelement (`.chat-panel`, das eigentliche Grid-Element) — dessen ungekürzter Inhalt floss weiterhin in die automatische Zeilenhöhen-Berechnung ein und blähte dadurch auch die linke Spalte mit auf.

**Fix:** Reines CSS kann "an der Höhe eines Geschwister-Elements ausrichten" und "eigenen, potenziell viel längeren Inhalt intern exakt darauf deckeln" nicht gleichzeitig leisten, wenn die Referenzhöhe selbst inhaltsabhängig ist — dafür ist ein kleines Stück JavaScript nötig. `NotebookPage.tsx`: `ResizeObserver` misst die tatsächliche Höhe der linken Spalte (`.layout-column`) und reicht sie als CSS-Variable (`--chat-panel-match-height`) an einen neuen Wrapper um `ChatPanel` weiter. `App.css`: `.chat-panel` nutzt diese Variable nur innerhalb der Desktop-Media-Query (`height: var(--chat-panel-match-height, 420px)`), mobil bleibt der ursprüngliche `min-height`/`max-height: 70vh`-Fallback unverändert aktiv.

**Verifikation:** Live mit 30 per JS injizierten Test-Nachrichten geprüft (kein echter Gemini-Call nötig für einen reinen Layout-Test) — Unterkante von linker Spalte und Chat-Panel exakt identisch (907px), vorher wie nachher; `chat-messages.scrollHeight` (1789px) deutlich größer als `clientHeight` (603px) bei unverändertem `document.body.scrollHeight` — bestätigt echtes internes Scrollen statt Seiten-Wachstum. Mobile Breite (~500px) separat geprüft: unverändert weiterhin per `max-height: 70vh` gedeckelt, von der Desktop-Änderung unberührt. `npm run lint`/`npm run build` sauber.

---

## 2026-09-18/20 — YouTube- und Audio-Quellen komplett entfernt, RAG-Schwellenwert-Bug gefunden und behoben

Nutzerwunsch: Die YouTube-Quelle funktionierte seit einiger Zeit nicht mehr zuverlässig — YouTube- und Audiodatei-Quellen (mp3/wav/m4a/ogg) sollten deshalb **komplett** entfernt werden (nicht nur in der UI versteckt), analog zum bereits früher komplett entfernten Podcast/Audio-Overview-Feature. Übrig bleiben sollten PDF, Markdown, URL. Zusätzlich: PDF/MD/URL sollten danach nochmal ausgiebig live getestet werden.

**Umsetzung über den Subagent-Workflow, parallel:**
- `python-pro` (Backend): `youtube_extraction.py` und `test_youtube_extraction.py` gelöscht, `transcribe_audio()` aus `gemini_client.py` entfernt, `POST .../sources/youtube`-Endpoint und die Audio-Erkennung im Upload-Endpoint aus `sources.py` entfernt, `YoutubeSourceRequest` aus `schemas.py` entfernt, Audio-Routing aus `text_extraction.py`/`storage.py` entfernt, `youtube-transcript-api` aus `requirements.txt` entfernt. Neue Migration `0006_remove_youtube_audio_sources.sql`: löscht zuerst bestehende `sources`-Zeilen mit `file_type in ('youtube','audio')` (cascadet zu `chunks`), dann wird der `file_type`-CHECK-Constraint auf nur noch `('pdf','md','url')` verengt (Constraint-Name dynamisch ermittelt, gleiches Muster wie `0004`), und die erlaubten MIME-Types im `sources`-Bucket werden auf PDF/Markdown/Plain-Text zurückgesetzt. Lokal wirklich mit `supabase migration up` **und** einem vollen `supabase db reset` angewendet und direkt in der laufenden Postgres-Instanz verifiziert (nicht nur die Datei geschrieben).
- `full-stack-developer` (Frontend): YouTube-Eingabefeld, Audio-Dateiendungen aus der Dropzone, Typ-Badges für YT/Audio aus `SourcesPanel.tsx` entfernt, `addYoutubeSource()` aus `api.ts` entfernt, `file_type`-Typ auf `'pdf' | 'md' | 'url'` verengt, `DatenschutzPage.tsx` korrigiert (die Seite beschreibt bewusst wahrheitsgemäß die tatsächlichen Quellentypen). Live per temporärer, danach sauber zurückgesetzter Preview-Route verifiziert (keine echten Logins für Verifikation genutzt, projektüblich).

**Review-Runde (`code-reviewer-pro` + `incident-responder`) fand einen kleinen echten Fund:** `backend/supabase/config.toml` listete für den lokalen `sources`-Bucket noch die alten Audio-MIME-Types, obwohl Migration `0006` den Bucket in der DB bereits auf PDF/Markdown/Plain-Text zurücksetzt — bei einem künftigen `supabase db reset` hätte das zu Drift zwischen lokaler Config und den Migrationen geführt. Direkt behoben (Liste bereinigt), mit erneutem `supabase db reset` verifiziert: alle 6 Migrationen laufen sauber durch, Config und DB-Zustand sind jetzt konsistent.

**Wichtiger operativer Hinweis von `incident-responder` für den Rollout auf Staging/Produktion:** Migration `0006` darf dort erst **nach** dem Deploy des neuen Backend-/Frontend-Codes eingespielt werden, nicht vorher — sonst könnte ein zeitliches Fenster entstehen, in dem der noch alte Code (der YouTube/Audio anbietet) gegen die schon verschärfte DB-Constraint läuft und einen kryptischen 500er statt einer sauberen Fehlermeldung verursacht.

**Ausgiebiger Live-Test von PDF/MD/URL** (frisches lokales Test-Notebook, drei Quellen: `koalas.pdf`, `wombats.md`, Wikipedia-Artikel zu Quokkas als URL):
- Upload aller drei Typen erfolgreich, Chunks korrekt erzeugt (1 für die kurze MD-Datei, 20 für den längeren Wikipedia-Artikel).
- Löschen einer Quelle (`koalas.pdf`) getestet: DB-Zeile weg, zugehörige `chunks` cascadet weg, **und** die Datei im Storage-Bucket direkt in der laufenden Postgres-Instanz per `psql` verifiziert entfernt (kein verwaister Eintrag) — nicht nur angenommen.
- Während der Chat-Tests mehrfach ein echter, transienter Gemini-503-Fehler ("high demand") aufgetreten — kein eigener Bug, extern, nach kurzer Wartezeit von selbst verschwunden. Backend-Log jedes Mal geprüft, um das von einem echten Bug zu unterscheiden.

**Echter Bug gefunden, nicht durch die YouTube/Audio-Entfernung verursacht, sondern durch mehr Testdaten aufgedeckt:** Frage "Was graben Wombats?" bei gleichzeitig vorhandener, thematisch verwandter aber inhaltlich irrelevanter Quokka-Wikipedia-Quelle im selben Notebook — die Antwort selbst war korrekt (nur aus `wombats.md`), aber die zurückgegebenen **Zitate** enthielten fälschlich 3 Quokka-Ausschnitte. Tatsächliche Ähnlichkeitswerte direkt per Python-Skript nachgerechnet (nicht vermutet): `wombats.md` 0.7748 (relevant), Quokka-Chunks 0.6255–0.6655 (alle irrelevant, aber über dem alten Schwellenwert 0.6). Bestätigt die schon in einer früheren Session dokumentierte Einschränkung: der `chat_similarity_threshold` war an nur einem einzigen Beispielpaar kalibriert (0,81 relevant / 0,53 irrelevant) und generalisiert nicht gut auf thematisch verwandte, aber sachlich andere Inhalte.

**Fix (mit Nutzer-Freigabe):** `chat_similarity_threshold` in `app/config.py` und `backend/.env.example` von 0.6 auf **0.7** angehoben, Kommentar um die neuen Kalibrierungsdaten ergänzt. Bestehender Regressionstest (`test_chat_api.py`, feste Testwerte 0.81/0.53) bleibt unverändert gültig, da beide Werte weiterhin klar auf der jeweils richtigen Seite der neuen Schwelle liegen. Live erneut verifiziert: Wombat-Frage zitiert danach nur noch `wombats.md`; Kontroll-Frage zu Quokkas zitiert weiterhin korrekt die Quokka-Quelle (kein Überfiltern); komplett themenfremde Frage ("Wie kompiliere ich ein Rust-Programm?") liefert weiterhin korrekt 0 Zitate und eine "keine Information"-Antwort. PDF-Quelle abschließend erneut hochgeladen und per Chat-Frage ("Wie viel wiegt ein Koala?") mit korrektem `koalas.pdf`-Zitat verifiziert.

**Finale Checks:** Backend `ruff check .`/`mypy app`/`pytest -q` → **88 Tests grün** (Reduktion von 93 auf 88 durch die entfernten YouTube-/Audio-Testfälle, plus einen neuen Test für abgelehnte Audio-Uploads).

**Ergebnis:** YouTube/Audio vollständig und sauber entfernt (kein toter Code, keine verwaisten Referenzen laut Review), PDF/MD/URL ausgiebig end-to-end verifiziert (Upload, Chat mit korrekten Zitaten, Löschen inkl. Storage-Cleanup), und ein zusätzlicher, durch die gründlichere Testabdeckung erst sichtbar gewordener RAG-Qualitätsbug behoben.

---

## 2026-09-20 — Sicherheits-Audit des Gesamtprojekts (SSRF, Rate-Limiting, Path-Traversal, CSP)

Nutzerwunsch: `code-reviewer-pro` und `incident-responder` sollen nochmal über das gesamte Projekt schauen und gezielt nach Sicherheitslücken suchen (explizit genannt: DDoS-artige Angriffe) — losgelöst von einem konkreten Feature, als eigenständige Audit-Runde. Anschließende Nachfrage: ob sich alle gefundenen Punkte kostenlos beheben lassen, und falls ja, die bewusste Entscheidung hinter jeder Änderung zu dokumentieren, nicht nur den Code-Diff selbst.

### Funde der ersten Audit-Runde

- **Kritisch — SSRF über die URL-Quelle:** `extract_url_content()` rief `trafilatura.fetch_url()` bislang ungeprüft mit der vom Nutzer eingegebenen URL auf. Da der Server (nicht der Browser des Nutzers) den Request ausführt, hätte ein Nutzer den Server zwingen können, interne Dienste anzusprechen (z.B. `http://localhost:6379`) oder Cloud-Metadata-Endpunkte auszulesen (`http://169.254.169.254/...`, liefert bei AWS/GCP häufig IAM-Credentials).
- **Hoch — keine Rate-Limits bei geteiltem API-Key:** Alle Nutzer teilen sich einen einzigen Gemini-API-Key. Ohne Rate-Limiting hätte ein einzelnes missbrauchtes Konto (oder ein Frontend-Bug, der z.B. den Chat in einer Schleife aufruft) das Kontingent für alle Nutzer gleichzeitig erschöpfen können ("noisy neighbor" als Verfügbarkeitsrisiko, nicht nur ein theoretisches DDoS-Szenario).
- **Mittel — Path Traversal über Datei-Uploads:** Der client-gelieferte Dateiname floss ungeprüft in den Storage-Pfad ein; ein Name wie `../../../etc/passwd` hätte den vorgesehenen Pfad verlassen können.
- **Mittel — fehlende Längenbegrenzungen:** Mehrere Freitext-Felder (Chat-Frage, Notiz-Inhalt, Präsentations-Beschreibung, URL) hatten kein `max_length`, ebenfalls ein Verfügbarkeits-/Kontingent-Risiko bei absichtlich überlangen Eingaben.
- **Niedrig/informativ — fehlender CSP-Header:** Keine Content-Security-Policy auf dem ausgelieferten Frontend gesetzt.

### Bewusste Entscheidung: alle Funde kostenlos behoben, keine bezahlte Infrastruktur nötig

Auf Nachfrage geprüft: **jeder** Fund lässt sich mit reinem Code lösen, ohne einen kostenpflichtigen Dienst (kein Redis, kein WAF, kein bezahltes Cloudflare-Plan-Feature) — passend zum durchgängigen Kostenlos-Anspruch dieses Projekts:

- **SSRF-Fix** (`app/services/web_extraction.py`, neue Funktion `_validate_public_url()`): löst den Hostnamen der URL selbst per `socket.getaddrinfo()` auf und prüft **alle** zurückgegebenen IP-Adressen (nicht nur die erste, wegen möglichem Round-Robin-DNS) gegen `ipaddress`-Klassifizierungen (`is_private`, `is_loopback`, `is_link_local`, `is_reserved`, `is_multicast`). Bewusst wird der aufgelöste Hostname geprüft, nicht nur der String in der URL — eine reine Text-Prüfung auf `"localhost"` hätte einen Hostnamen übersehen, der öffentlich aussieht, aber zur Laufzeit auf eine private IP zeigt. Zusätzlich: explizites, kürzeres Download-Timeout (`url_extraction_timeout_seconds`, 10s statt trafilaturas 30s-Default) und eine Obergrenze für extrahierten Text (`max_extracted_url_text_chars`, 200.000 Zeichen) gegen unbegrenzte Chunk-/Embedding-Erzeugung durch eine einzelne, sehr große Zielseite.
  - **Bewusst akzeptiertes Restrisiko (nicht übersehen, sondern abgewogen):** `_validate_public_url()` löst den Hostnamen einmal auf, aber `trafilatura.fetch_url()` löst ihn für den tatsächlichen Abruf gleich danach intern nochmal auf (TOCTOU/DNS-Rebinding) — bei einer Domain mit sehr kurzer TTL könnte sich die Antwort zwischen den beiden Auflösungen ändern. Eine vollständige Behebung (IP-Pinning: die bereits geprüfte IP direkt für den Request verwenden statt den Hostnamen erneut auflösen zu lassen) unterstützt `trafilatura` nicht ohne größeren Eigenbau einer eigenen HTTP-Session. Entscheidung: das Restrisiko bewusst in Kauf nehmen, da der Angriffspfad drei unabhängige Bedingungen gleichzeitig erfordert (eigene Domain mit Kurz-TTL, ein Opfer, das genau diese URL einträgt, exaktes Timing) — dokumentiert als Kommentar direkt an der Stelle im Code, nicht nur hier.
- **Rate-Limiting** (`app/rate_limit.py`, neu, `slowapi`): pro **Nutzer-Konto** limitiert (`request.state.user_id` aus dem verifizierten JWT), nicht pro IP-Adresse — sonst hätten sich mehrere Nutzer hinter derselben IP (Firmennetzwerk/NAT) gegenseitig blockiert, während ein Angreifer ein IP-basiertes Limit einfach über mehrere IPs hätte umgehen können. `key_style="endpoint"` statt des slowapi-Defaults `"url"`, weil unsere Routen `notebook_id` als Pfad-Segment enthalten — sonst hätte jede `notebook_id` ihren eigenen Bucket bekommen und das Limit wäre durch Verteilen auf mehrere Notebooks umgehbar gewesen. In-Memory-Storage (kein Redis) bewusst gewählt, weil Render Free-Tier ohnehin nur eine einzige Instanz erlaubt — ein externer State-Store wäre reiner Overhead ohne Nutzen. Limits: `/chat` 10/Min, `/presentations` 5/Min (teuerster Endpunkt), Datei-/URL-Upload je 10/Min, `DELETE /notebooks/{id}` 20/Min (siehe unten).
- **Path-Traversal-Fix** (`app/services/storage.py`, `_sanitize_filename()`): `ntpath.basename` **und** `posixpath.basename` angewendet (Supabase Storage kennt nur `/`, ein Client könnte aber auch Windows-Backslashes senden), führende Punkte und Null-Bytes entfernt, Fallback auf `"datei"` bei leerem Ergebnis.
- **Längenbegrenzungen** (`app/schemas.py`): `Field(max_length=...)` auf allen Freitext-Feldern ergänzt (Chat-Frage, Notiz, Präsentations-Felder, URL, Notebook-Name).
- **CSP-Header** (`frontend/public/_headers`, neu): `default-src 'self'` als Basis, `connect-src` explizit auf die drei tatsächlich genutzten Hosts erweitert (`*.supabase.co`, `*.onrender.com`, den Sentry-Ingest-Host), `style-src 'self' 'unsafe-inline'` (einziger Inline-Style im Projekt: `NotebookPage.tsx`s `ResizeObserver`-CSS-Variable für die Chat-Fenster-Höhe, siehe Eintrag oben), `frame-ancestors 'none'`. Cloudflares `_headers`-Dateikonvention vorab per Doku-Check verifiziert, dass sie mit dem hier genutzten `[assets]`-Deployment-Modell (nicht dem klassischen Pages-Modus) funktioniert.

### Zweite Review-Runde (auf den Sicherheits-Fixes selbst) und ihre Funde

`code-reviewer-pro` und `incident-responder` haben anschließend die Fixes selbst nochmal geprüft (Review des Reviews) — vier weitere, alle kostenlos behebbare Punkte gefunden:

1. **Echter UX-Bug:** slowapis Standard-429-Handler liefert `{"error": "..."}`, das Frontend (`api.ts`, `parseErrorMessage`) liest aber ausschließlich `body.detail` (wie bei jedem anderen Fehler im Projekt) und fiel deshalb bei jedem Rate-Limit-Treffer auf die rohe, unübersetzte `response.statusText` ("Too Many Requests") zurück. **Fix:** eigener `_handle_rate_limit_exceeded()`-Handler in `app/main.py`, liefert `{"detail": "Zu viele Anfragen. Bitte warte kurz und versuche es erneut."}` — konsistent mit allen anderen Fehlerpfaden im Frontend.
2. **Echte Lücke:** `DELETE /notebooks/{id}` war der einzige mengenmäßig unbegrenzte Server-Loop im Projekt ohne eigenes Rate-Limit (iteriert über alle Source-/Präsentations-Storage-Pfade eines Notebooks, je ein synchroner Supabase-Call). **Fix:** `@limiter.limit("20/minute")` ergänzt — großzügig genug für normales Löschen, eng genug gegen wiederholtes teures Anlegen/Löschen-Muster.
3. **Whitespace-only-Dateinamen-Lücke:** `_sanitize_filename()` prüfte Leerheit vor dem `.strip()`, ein rein aus Leerzeichen bestehender Dateiname (z.B. `"   "`) wäre am `"datei"`-Fallback vorbeigerutscht. **Fix:** `.strip()` vor der Leerheitsprüfung ergänzt.
4. **Unbewiesene Kernbehauptung, jetzt verifiziert (siehe Debugging-Fund unten):** Der Docstring von `_rate_limit_key()` behauptete, das Limit greife garantiert pro Nutzer-Konto statt pro IP, weil FastAPI die `get_current_user_id`-Dependency immer vor der Rate-Limit-Prüfung auflöst — aber kein bestehender Test bewies das, da der Test-Client durchgehend dieselbe Quell-IP nutzt (ein rein IP-basiertes Limit hätte in den bisherigen Tests genauso "funktioniert").

**Debugging-Fund beim Schreiben des Beweis-Tests (`test_rate_limit_is_scoped_per_user_not_per_ip`):** Der erste Testversuch nutzte `app.dependency_overrides[get_current_user_id]`, um zwei verschiedene Nutzer zu simulieren — der Test schlug fehl und deutete zunächst auf genau den befürchteten Bug hin (beide "Nutzer" teilten sich ein Kontingent). Ursache war aber ein Fehler im Testaufbau, kein Produktionsbug: `dependency_overrides` ersetzt die komplette Dependency-Funktion, wodurch der reale Code-Pfad in `app/auth.py`, der `request.state.user_id` setzt, gar nicht mehr läuft — der Rate-Limiter griff also korrekt auf seinen dokumentierten IP-Fallback zurück, weil `request.state.user_id` in diesem Testaufbau nie gesetzt wurde. Test neu geschrieben: zwei echte, unterschiedlich signierte JWTs (`sub: "user-a"` / `sub: "user-b"`) laufen durch die volle, reale Dependency-Resolution, über denselben `TestClient` (garantiert dieselbe Quell-IP). Ergebnis: Nutzer A wird nach 10 Anfragen mit 429 gebremst, Nutzer B (anderer Account, gleiche IP) bekommt direkt danach trotzdem eine 200 — die im Docstring behauptete Pro-Nutzer-Zuordnung ist damit tatsächlich bewiesen, kein Bug in der Produktion, nur eine bis dahin unbewiesene Annahme.

Zusätzlich als bewusste Entscheidung dokumentiert (kein Code-Fix nötig): `incident-responder` merkte an, dass ein Absturz-Neustart-Zyklus (Crash-Loop) des Backend-Prozesses den In-Memory-Rate-Limit-Zähler bei jedem Neustart auf 0 zurücksetzen würde. Als Randfall zweiter Ordnung eingestuft (setzt voraus, dass ein einzelner Nutzer den Prozess trotz der engen 5-10/Minute-Limits überhaupt erst zum Absturz bringen kann) und im Docstring von `app/rate_limit.py` als bewusst akzeptiertes Restrisiko festgehalten statt mit einem externen State-Store behoben, der bei einer einzelnen Render-Free-Tier-Instanz unnötiger Overhead wäre.

### CSP-Verfügbarkeitsrisiko gezielt geprüft

Explizite Sorge (eigene Nachfrage vor dem Ausrollen): könnte der neue CSP-Header die App auf Staging/Produktion unbemerkt kaputt machen, weil ein CSP-Verstoß nur eine Konsolen-Zeile erzeugt, aber weder einen für Endnutzer sichtbaren Fehler noch einen Ausschlag im Server-Monitoring? `incident-responder` hat das gezielt gegen den tatsächlichen Code geprüft (nicht nur die Header-Syntax): Produktions-Build erzeugt genau ein `<script type="module">`-Tag ohne Inline-Scripts, Supabase-Auth läuft rein über `fetch`/XHR (kein OAuth-Redirect, der `frame-src` bräuchte), Backend-Calls gehen an die deklarierte `*.onrender.com`-Domain, keine externen Fonts. Einschätzung: **Risiko niedrig bis moderat, nicht hoch** — die nutzerkritischen Pfade sind sauber abgedeckt. Der einzige nicht abschließend verifizierbare Punkt: der Sentry-Ingest-Host in `connect-src` konnte nicht gegen die echte `VITE_SENTRY_DSN` abgeglichen werden, da diese erst zur Deploy-Zeit über die echte Cloudflare-Pages-Env-Var gesetzt wird — ein Mismatch würde nur die Sentry-Fehlerberichte lautlos blocken, nicht die App selbst unbenutzbar machen.

**Daraus folgender, noch offener Verifikationsschritt vor dem Produktions-Merge** (siehe TODO.md): nach dem nächsten Staging-Deploy mit offener DevTools-Konsole einmal jeden kritischen Pfad manuell durchklicken (Login, Notebook anlegen, Quelle hochladen, Chat-Frage, Präsentation generieren), Network-Tab nach `(blocked:csp)` filtern, und gezielt einen Test-Fehler auslösen, um zu bestätigen, dass er in Sentry ankommt.

### Verifikation

Backend: `ruff check .`, `mypy app`, `pytest -q` → **119 Tests grün** (von 88 auf 119 durch die neuen Sicherheits-Tests: SSRF-Validierung inkl. privater/Loopback-/Link-Local-/Multicast-IPs, Path-Traversal-Fälle inkl. Whitespace-only, Rate-Limit-Grenzwerte pro Endpunkt, der Pro-Nutzer-vs-Pro-IP-Beweistest, `key_style="endpoint"`-Regressionstest). Frontend: `npm run lint`/`npm run build` sauber, `_headers`-Datei landet korrekt in `dist/`.

**Ergebnis:** Alle in der Audit-Runde gefundenen Sicherheits- und Verfügbarkeitslücken kostenlos (reiner Code, keine zusätzliche bezahlte Infrastruktur) behoben, jede bewusste Abwägung (akzeptierte Restrisiken, gewählte Limit-Werte, Key-Funktions-Design) direkt im Code dokumentiert. Einzig offener Punkt vor dem nächsten Produktions-Deploy ist die manuelle CSP-Verifikation auf der echten Staging-Umgebung (siehe oben).

**Rollout abgeschlossen:** Über PR #4 gemerged (CI grün, QA-Gate durchlaufen). Vor dem Einspielen der Migration wurde der erfolgreiche Deploy auf beiden Render-Umgebungen aktiv per HTTP-Check verifiziert (der entfernte `POST .../sources/youtube`-Endpoint liefert jetzt `405 Method Not Allowed` statt der alten Route — der Pfad matcht stattdessen auf die generische `DELETE /sources/{source_id}`-Route, ein eindeutiges Signal, dass der neue Code läuft, nicht nur angenommen). Erst danach Migration `0006` im SQL Editor von Staging und Produktion eingespielt. Damit ist die YouTube/Audio-Entfernung auf allen drei Umgebungen (lokal, Staging, Produktion) vollständig ausgerollt.

---

## 2026-09-21 — Zwei Deploy-Pipeline-Bugs gefunden und behoben (CSP nie live, E2E gegen tote URL)

Ausgangspunkt: der aus dem Sicherheits-Audit offen gebliebene Verifikationsschritt — CSP-Header vor dem Produktions-Merge live auf Staging prüfen (siehe oben). PR #6 (Sicherheits-Hardening) war zu diesem Zeitpunkt bereits nach `develop` gepusht und alle CI-Checks grün, inklusive eines grünen Cloudflare-"Workers Builds"-Checks für den Staging-Build.

### Bug 1: Cloudflare-Staging-Projekt deployte Builds nie live

Der CSP-Header fehlte auf der echten Staging-URL trotz grünem Build. Direkt im Cloudflare-Dashboard nachverfolgt statt geraten: Der Tab "Deployments" des Projekts `notebooklm-klon-staging` zeigte, dass die aktive Version weiterhin ein 19 Stunden alter Stand war — der neue, erfolgreich gebaute Commit stand mit 0% Traffic in der Versions-Historie, wurde aber nie promotet.

**Root Cause:** Unter Settings → Builds → Branch control stand "Production branch" auf **`main`**, obwohl dieses Projekt inhaltlich die Staging-Umgebung ist und auf `develop` reagieren soll. Cloudflares Git-Integration führt bei einem Push auf den konfigurierten Production-Branch den vollen `Deploy`-Befehl aus (100% Traffic); bei jedem anderen Branch — inklusive `develop`, solange "Builds for non-production branches" aktiv ist — läuft nur `wrangler versions upload` (Preview-Version ohne Traffic-Zuweisung). Zum Vergleich geprüft: Das zweite Projekt `notebooklm-klon-prod` hat "Production branch" korrekt auf `main` stehen — dort hat es immer funktioniert, weil die Einstellung von Anfang an richtig war.

**Fix:** "Production branch" auf `develop` umgestellt (vom Nutzer im Dashboard selbst vorgenommen), anschließend die bereits gebaute, aber nie promotete Version einmalig über "Promote version" auf 100% Traffic gesetzt (Cloudflare-Dashboard, live gemeinsam mit dem Nutzer durchgeführt). Verifiziert: `curl -I` gegen die echte Staging-URL zeigt danach alle vier neuen Security-Header (`content-security-policy`, `x-content-type-options`, `x-frame-options`, `referrer-policy`).

**Bewusste Entscheidung — kein zusätzlicher CI/CD-Schritt gebaut:** Die eigentliche Frage war, ob dafür eine eigene Pipeline-Automatisierung (z.B. ein `wrangler deploy`-Schritt in `ci.yml`) nötig ist. Antwort: nein — es war ein einmaliger Konfigurationsfehler, keine fehlende Fähigkeit. Cloudflares native Git-Integration deployt bei jedem künftigen `develop`-Push jetzt automatisch mit 100% Traffic, genau wie sie es beim korrekt konfigurierten Produktions-Projekt schon die ganze Zeit getan hat. Eine selbstgebaute Lösung wäre eine Dopplung vorhandener, nativer Funktionalität gewesen.

### Bug 2: E2E-Workflow testete seit Tagen gegen eine tote URL

Zur endgültigen Verifikation (Login + echter Backend-Call, nicht nur Header-Check) wurde `e2e.yml` manuell per `workflow_dispatch` gegen `develop` ausgelöst — alle 5 Tests schlugen fehl, auch die 4 rein clientseitigen (Login-/Signup-Formular-Rendering, Redirect-Schutz), die mit dem CSP-Fix gar nichts zu tun haben sollten.

**Root Cause:** `E2E_BASE_URL` in `.github/workflows/e2e.yml` war fest auf `https://develop-notebooklm-klon.piaheiss.workers.dev` gesetzt — dieselbe Branch-Alias-URL, die schon zu Beginn dieser Debugging-Sitzung Cloudflares generische "There is nothing here yet"-Seite zeigte. Diese URL hatte tatsächlich funktioniert: ein Lauf vom 18.09. mit identischer URL war 5/5 grün. Zwischen dem 18.09. und heute wurde das Staging-Cloudflare-Projekt im Zuge des separaten Produktions-Projekts auf den Namen `notebooklm-klon-staging` umbenannt/reorganisiert — die alte `develop-notebooklm-klon`-Branch-Alias-Subdomain existiert seitdem nicht mehr, aber `e2e.yml` wurde nie nachgezogen. Da der Workflow nur wöchentlich/manuell läuft, ist das drei Tage lang unbemerkt geblieben.

**Fix:** `E2E_BASE_URL` auf `https://notebooklm-klon-staging.piaheiss.workers.dev` korrigiert (die tatsächliche, im Dashboard unter "Domains" verifizierte Worker-URL), committed und nach `develop` gepusht (nachdem ein erster, verfrühter `workflow_dispatch`-Versuch noch gegen den alten, ungepushten `develop`-Stand lief und abgebrochen wurde). Erneuter Lauf: die 4 clientseitigen Tests liefen danach durch — der eigentliche Login-Test blieb aber hängen (`TimeoutError` beim Warten auf die `GET /notebooks`-Antwort), was zu Bug 3 führte.

### Bug 3: Render-Staging-Backend erlaubte die neue Frontend-Origin nicht per CORS (live, nicht nur ein Test-Problem)

Der Login-Test kam bis zum Dashboard-Redirect, aber der `GET /notebooks`-Request wurde nie beobachtet. Direkt nachvollzogen statt geraten: ein manueller CORS-Preflight-Check (`curl -X OPTIONS .../notebooks` mit `Origin: https://notebooklm-klon-staging.piaheiss.workers.dev`) lieferte `400 Disallowed CORS origin` — der Browser hätte den eigentlichen `GET`-Request also nie abgeschickt (anders als bei einer reinen CORS-Response-Blockade feuert hier gar kein Netzwerk-Request, was exakt zum beobachteten `waitForResponse`-Timeout passt).

**Root Cause:** `ALLOWED_ORIGINS` im Render-Staging-Backend (`notebooklm-klon-api-staging`) stand noch auf der alten, toten URL `https://develop-notebooklm-klon.piaheiss.workers.dev` — derselbe Umbenennungs-Vorfall wie bei Bug 2, diesmal auf der Backend-Seite nie nachgezogen. **Das ist kein reines Test-Artefakt, sondern hat bis zu diesem Fund echte Logins auf der aktuell laufenden Staging-Seite verhindert.**

**Fix:** `ALLOWED_ORIGINS` im Render-Dashboard auf `https://notebooklm-klon-staging.piaheiss.workers.dev` korrigiert, "Save, rebuild, and deploy" ausgelöst. Nach Abschluss des Redeploys erneuter CORS-Preflight-Check: `200` statt `400`. Kleiner Zwischenfall bei der manuellen Bearbeitung im Render-Dashboard: ein Fehlklick landete zunächst auf dem Lösch-Icon der `ALLOWED_ORIGINS`-Zeile statt auf "anzeigen" — sofort per "Rückgängig"-Icon korrigiert, bevor gespeichert wurde, kein Datenverlust.

**Finale Verifikation:** `.github/workflows/e2e.yml` erneut per `workflow_dispatch` gegen `develop` laufen lassen — **5/5 Tests grün (4,8s)**, inklusive des echten Login-Tests mit erfolgreichem `GET /notebooks`-Call gegen die komplette reale Kette (Cloudflare-Frontend → Supabase Auth → Render-Backend → Supabase-DB).

**Ergebnis:** Drei unabhängige, durch dieselbe Infrastruktur-Reorganisation (Aufteilung in separate Staging-/Prod-Cloudflare-Projekte) entstandene Drift-Bugs gefunden und behoben — keiner davon eine Regression durch den Sicherheits-Hardening-Code selbst, aber alle drei hätten unentdeckt dafür gesorgt, dass weder der neue CSP-Header noch normale Nutzer-Logins zuverlässig auf Staging funktionieren, ohne dass CI (die nur Build-Erfolg, nicht Live-Traffic, CORS oder die tatsächliche Ziel-URL prüft) das angezeigt hätte. Gutes Beispiel dafür, warum ein echter, gegen die Live-Umgebung laufender E2E-Test (statt nur Unit-/Build-Checks) einen eigenständigen Wert hat.

**Merge nach Produktion (PR #6) und Produktions-Verifikation:** Nach grüner CI (inkl. des neuen `e2e.yml`-Fixes) gemerged. Da Bug 1 und Bug 3 reine Dashboard-Einstellungen waren (nicht im Repo-Code), betrafen sie ausschließlich das Staging-Projekt — das Produktions-Cloudflare-Projekt (`notebooklm-klon-prod`) hatte "Production branch" von Anfang an korrekt auf `main` stehen, und das Produktions-Render-Backend (`notebooklm-klon-api`) hatte `ALLOWED_ORIGINS` bereits korrekt gesetzt. Trotzdem vorsichtshalber nach dem Merge direkt verifiziert statt einfach angenommen: `curl` gegen die echte Produktions-URL (`notebooklm-klon-prod.piaheiss.workers.dev`) zeigt alle vier Security-Header, und ein CORS-Preflight-Check gegen das Produktions-Backend (`notebooklm-klon-api.onrender.com`) mit der echten Produktions-Origin liefert korrekt `200`/`access-control-allow-origin`. Der automatische Deploy auf `main`-Push hat wie erwartet ohne manuelles Nacharbeiten funktioniert.

**Letzter offener Punkt aus der CSP-Checkliste — Sentry-Ingest-Host verifiziert:** Auf der deployten Staging-Seite über die Browser-Konsole einen bewusst eindeutig markierten Test-Fehler ausgelöst (`throw new Error('csp-sentry-test-<Timestamp>')`). Der zugehörige Netzwerk-Request an `o4512106312171520.ingest.de.sentry.io` lieferte `200` (nicht von der CSP geblockt), und der Fehler erschien wenige Minuten später im Sentry-Dashboard unter dem Frontend-Projekt, exakt mit der eindeutigen Test-Marke wiedererkennbar. Damit ist der einzige zuvor nicht abschließend verifizierbare Punkt der CSP-Einführung (siehe oben) bestätigt: der Sentry-Ingest-Host in `connect-src` ist korrekt und deckt die reale, zur Deploy-Zeit gesetzte `VITE_SENTRY_DSN` ab.

---

## 2026-09-21 — Erneuter Gesamt-Check: ein echter Bug, drei Robustheits-Verbesserungen, kein Datenleck

Nutzerwunsch: nach dem Abschluss der Sicherheits-/Deploy-Runde nochmal einen kompletten Check über das gesamte Projekt — sowohl auf Bugs/Fehler als auch gezielt auf sensible Daten, die weder im Browser noch im Repository sichtbar sein sollten (explizit genannt: DB-URLs, Secrets).

**Eigene Direkt-Verifikation vor dem Review-Einsatz** (um die Subagenten nicht dieselbe Grundarbeit doppelt machen zu lassen): `.gitignore`-Abdeckung geprüft, komplette Git-Historie nach gängigen Secret-Mustern durchsucht (Supabase-Service-Key-Präfixe, Gemini-`AIza`-Präfix, Postgres-Connection-Strings, private Keys) — keine Treffer. Den tatsächlich deployten Frontend-JS-Bundle heruntergeladen und durchsucht: einziger gefundener JWT-artiger String ist der Supabase-`anon`-Key, per Base64-Decode des Payloads bestätigt `"role":"anon"` (nicht `service_role`) — korrekt, da der Anon-Key laut Design öffentlich sein darf. Backend-Fehlerantworten (422/401) geben keine Stack-Traces preis, kein `debug=True`. Ein vermeintliches Sourcemap-File (`.js.map`) entpuppte sich beim genaueren Hinsehen als reiner SPA-Fallback (`index.html`, wegen `not_found_handling = "single-page-application"`), kein echtes Sourcemap wird ausgeliefert.

**`code-reviewer-pro`** (Gesamt-Codebase auf Bugs) fand vier Punkte — davon einer nach eigener Prüfung widerlegt:
- ❌ **Falsch-positiv, widerlegt:** Die gemeldete "kritische" Behauptung, Supabase-`DELETE`-Aufrufe würden leere `response.data` liefern und dadurch fälschlich 404 statt Erfolg zurückgeben. Direkt im installierten `postgrest`-Package nachgesehen (`.venv/lib/python3.12/site-packages/postgrest/_sync/request_builder.py`): `delete()` hat `returning=ReturnMethod.representation` als Standardwert — die gelöschten Zeilen werden also standardmäßig zurückgegeben. Kein Bug; passt zur bereits mehrfach dokumentierten Live-Verifikation von Lösch-Vorgängen in früheren Phasen. Guter Beleg dafür, eine als "kritisch" gemeldete Behauptung vor dem Umsetzen an der tatsächlichen Bibliotheks-Implementierung zu verifizieren, statt sie ungeprüft zu übernehmen.
- ✅ **Echter Bug:** `.md`-Upload mit ungültigem UTF-8-Encoding (z.B. Windows-1252/Latin-1 aus älteren oder Windows-Editoren) ließ `content.decode("utf-8")` in `text_extraction.py` ungeschützt crashen — propagierte als generischer 500 statt einer verständlichen 422-Meldung.
- Drei Robustheits-Verbesserungen (kein funktionaler Bug, aber schlechte Fehler-UX): Gemini-API-Fehler (Kontingent/Service down — live bereits als transiente 503 "high demand" beobachtet) gaben in Chat und Präsentationsgenerierung einen generischen 500 statt einer erklärenden Meldung; ungültiges JSON von Gemini bei Präsentationen ebenso; eine fehlgeschlagene Chat-Antwort wurde im Frontend als Fake-`assistant`-Nachricht angezeigt, die das Backend nie persistiert — verschwand nach einem Reload spurlos, während die echte Frage stehen blieb.

**`incident-responder`** (gezielt Datenlecks: Backend-Logging, Frontend-Hardcoding, API-Response-Schemas, RLS-Policies, committete Config-Dateien, Git-Historie) fand **keine Secrets/DB-Credentials**: Logging gibt nirgends JWT-Inhalte/Passwörter/vollständige Request-Bodies aus, `SourceOut`/`PresentationOut` filtern `storage_path` (enthält `user_id` im Klartext) beim Serialisieren korrekt heraus, alle sechs relevanten Tabellen haben lückenlose RLS-Policies, `render.yaml` deklariert Secrets korrekt mit `sync: false`, nie eine echte `.env`-Datei in der Git-Historie. Ein Fund außerhalb der Secret-Kategorie: der private Cloudflare-Kontoname `piaheiss` steht im Klartext in `e2e.yml` und mehreren `PROGRESS.md`-Stellen (über die `*.piaheiss.workers.dev`-Subdomains) — deanonymisiert den Repo-Betreiber, ist aber kein Sicherheitsrisiko für die Anwendung selbst. Auf Nutzerwunsch nicht behoben (bewusste Entscheidung, nicht übersehen).

**Fixes umgesetzt** (alle vier vom Nutzer bestätigten Punkte, der widerlegte Delete-"Bug" ausgenommen):
- `text_extraction.py`: `UnicodeDecodeError` beim Markdown-Decode wird jetzt als `ValueError` mit klarer Meldung weitergereicht; `sources.py` fängt das beim Upload-Endpoint ab und liefert `422` statt `500`.
- `gemini_client.py`: `generate_answer()` und `generate_presentation_outline()` fangen `google.genai.errors.APIError` jetzt ab und liefern `503` mit einer verständlichen deutschen Meldung statt eines generischen 500; ungültiges JSON von Gemini bei der Präsentationsgliederung liefert `422` statt `500`.
- `ChatPanel.tsx`: fehlgeschlagene Chat-Antworten landen nicht mehr als Fake-Nachricht im (scheinbar persistierten) Nachrichtenverlauf, sondern in einem separaten, klar als session-lokal erkennbaren Fehlerzustand (`.chat-error`-Klasse in `App.css`) — kein Reload-Inkonsistenz-Effekt mehr.
- Sechs neue Regressionstests ergänzt (ungültiges Encoding auf Unit- und API-Ebene, `APIError`→503 für beide Gemini-Funktionen, ungültiges JSON→422).

**Verifikation:** Backend `ruff check .`/`mypy app`/`pytest -q` → **124 Tests grün**. Frontend `npm run lint`/`npm run build` → sauber.

**Ergebnis:** Ein echter, kleiner Produktions-Bug behoben, drei Fehler-UX-Verbesserungen umgesetzt, kein einziges Secret/keine DB-URL im Repo, in der Git-Historie oder im ausgelieferten Frontend gefunden — die einzige gefundene "Exposition" ist der private Cloudflare-Kontoname (PII, kein Sicherheitsrisiko, bewusst nicht behoben).

---

## 2026-09-21 — Live-Vorfall: Gemini-Chat scheiterte im Live-Test, drei zusammenhängende Funde

Beim eigenen Live-Test der laufenden App (Staging und Produktion) schlug der Chat wiederholt mit `503 KI-Service ist momentan nicht verfügbar` fehl. Direkt gegen echte Logs verifiziert statt geraten (Render-Logs, Sentry) — keiner der drei folgenden Funde war eine Regression durch eigenen Code.

**Fund 1 — echte, transiente Gemini-"high demand"-503er:** Sentry zeigte wiederholte `ServerError: This model is currently experiencing high demand` für `gemini-3.6-flash`, extern von Googles eigener AI-Studio-Statusseite bestätigt ("Free-tier requests use sheddable capacity"). **Fix:** `_call_with_retry()` in `gemini_client.py` ergänzt — bei einem `ServerError` wird nach 1,5s automatisch einmal erneut versucht, bevor der Fehler beim Nutzer ankommt. Zwei neue Regressionstests (Retry-Erfolg, Retry-Erschöpfung).

**Fund 2 — echtes, hartes Kontingent-Limit:** Zusätzlich zu den 503ern zeigte Sentry einen `ClientError`: "Quota exceeded ... limit: 20, model: gemini-3.6-flash" — das kostenlose Kontingent von 20 `generate_content`-Aufrufen/Minute war ausgeschöpft, mitverursacht durch eigene Diagnose-Skripte, die direkt gegen die Gemini-API liefen (am `slowapi`-Rate-Limiter der App vorbei, der nur Aufrufe über die eigenen Endpunkte begrenzt, nicht direkte Skript-Aufrufe).

**Fix (Modellwechsel):** Mehrere Kandidaten **live gegen die echte API getestet** statt der Doku/Modell-Liste blind vertraut: `gemini-2.5-flash` → 404 (für diesen Account nicht verfügbar), `gemini-flash-latest` → 503, `gemini-3.5-flash` und `gemini-3.7-flash` → beide erfolgreich. Standardmodell auf `gemini-3.7-flash` umgestellt.

**Fund 3 — unabhängiger Bug, beim Live-Test entdeckt:** Eine Quelle mit dem Titel `[Hiring] DevOps Engineer @Everlast Consulting GmbH` ließ den Storage-Upload mit `StorageApiError: Invalid key` fehlschlagen. **Root Cause:** `[`, `]` und `@` sind keine gültigen Supabase-Storage-Key-Zeichen — kein Pfad-Traversal-Risiko (davon bereits durch `basename()`/`lstrip(".")` getrennt abgedeckt), sondern eine reine Zeichen-Validitäts-Frage. **Fix:** `_sanitize_filename()` in `storage.py` von einer Verbotsliste (einzelne Sonderzeichen) auf eine Erlaubnisliste umgestellt (`[^A-Za-z0-9 ._-]` → `_`) — deckt jedes zukünftige ungültige Zeichen ab, nicht nur die bereits bekannten. Verifiziert direkt gegen die echte, nicht gemockte lokale Supabase-Storage-API (Python-Skript mit dem exakten Fundtitel, Upload + Cleanup erfolgreich).

**Erneuter Rückfall nach dem Modellwechsel:** Rund eine Stunde nach dem Deploy von `gemini-3.7-flash` zeigte Sentry denselben "high demand"-503, jetzt für `gemini-3.7-flash` selbst — Kapazitätsengpässe werden bei Google offenbar pro Modell unabhängig verwaltet, ein einzelner Modellwechsel ist also keine dauerhafte Lösung. **Fix:** `_generate_content_with_fallback()` ergänzt — hält der `ServerError` beim primären Modell auch nach dem Einmal-Retry an, weicht `generate_answer`/`generate_presentation_outline` automatisch auf ein zweites, unabhängiges Modell aus (`gemini_chat_model_fallback`, Standard `gemini-3.5-flash`, live am selben Tag stabil), statt nur denselben überlasteten Endpunkt erneut zu versuchen. Zusätzlich dabei eine bereits bekannte Lücke geschlossen: `embed_texts()` hatte (anders als die beiden `generate_content`-Funktionen) keinen `APIError`-Fang und hätte einen anhaltenden Embedding-Fehler als generischen 500 statt einer klaren 503 durchgereicht (in Sentry mehrfach als "Unhandled" markiert). Vier neue Regressionstests (Fallback-Erfolg, Fallback-Erschöpfung, `embed_texts`-503).

**Verifikation:** Backend `ruff check`/`ruff format --check`/`mypy app`/`pytest -q` → **129 Tests grün**.

**Ergebnis:** Kein einziger der drei live beobachteten Fehler war ein Bug im eigenen Code — zwei waren echte, dokumentierte Google-seitige Free-Tier-Grenzen (Kapazität, Kontingent), einer ein unabhängiger, vorher unentdeckter Zeichen-Validitäts-Bug. Die Konsequenz aus dem wiederholten Modell-Flip (3.6 → 3.7, beide zeitweise überlastet) war eine strukturelle statt einer punktuellen Lösung: automatischer Modell-Fallback statt eines weiteren einmaligen Modellwechsels.

**Nachtrag noch am selben Tag — der Fallback allein löste "lädt ewig" nicht:** Direkt nach dem Deploy erneut live getestet: Der Chat lud diesmal nicht in Sekunden, sondern über **3,5 Minuten**, bevor endlich ein 503 ankam. Live in den Render-Logs nachverfolgt statt geraten: die erste Anfrage an `gemini-3.7-flash` brauchte ~9s bis zum Fehler, der Retry auf demselben Modell aber **über 2,5 Minuten**, und erst danach griff der neue Fallback auf `gemini-3.5-flash` — der ebenfalls mit 503 endete (beide Modelle gleichzeitig unter "high demand", nicht nur eines).

**Root Cause:** `genai.Client(...)` wurde ohne `http_options.timeout` initialisiert. Direkt im SDK-Quellcode nachgesehen (`google/genai/_api_client.py`): ohne explizites Timeout setzt die SDK `max_allowed_time = float('inf')` — ein einzelner Aufruf kann also technisch unbegrenzt lange auf eine Antwort warten. Bei Googles aktuellem "high demand"-Zustand kam die 503-Antwort dadurch teils erst nach Minuten statt Sekunden — für den Nutzer ununterscheidbar von einem echten Hänger, obwohl der Code "korrekt" auf eine (nur sehr späte) Antwort wartete. In Kombination mit Retry (1×) und Fallback (1×) konnte sich das im Extremfall zu einer mehrminütigen Gesamt-Wartezeit für eine einzige Chat-Nachricht aufsummieren.

**Fix:** `http_options=types.HttpOptions(timeout=30_000)` (30s) beim Client-Setup ergänzt, begrenzt jeden einzelnen Versuch. Da ein Timeout dabei als `httpx.TimeoutException` auftritt — strukturell unabhängig von `google.genai.errors.APIError`, direkt im SDK-Quellcode verifiziert (`_HTTPX_TRANSIENT_EXC`) — wurde dieser Fall an allen relevanten Stellen (`_call_with_retry`, `_generate_content_with_fallback`, sowie die äußeren Fänge in `embed_texts`/`generate_answer`/`generate_presentation_outline`) gleichwertig zu `ServerError` behandelt, statt ungefangen als generischer 500 durchzuschlagen. Drei neue Regressionstests (Timeout-Retry-Erfolg, Timeout bei primärem UND Fallback-Modell → sauberes 503, Timeout bei `embed_texts` → 503).

**Verifikation:** Backend `ruff check`/`ruff format --check`/`mypy app`/`pytest -q` → **132 Tests grün**.

**Ergebnis:** Ein automatischer Modell-Fallback allein reicht nicht, wenn jeder einzelne Versuch selbst unbegrenzt lange dauern kann — Resilienz-Maßnahmen wie Retry/Fallback brauchen ein Timeout als Voraussetzung, sonst multiplizieren sie im schlimmsten Fall nur die Wartezeit statt sie zu verkürzen. Der zugrundeliegende Google-seitige Kapazitätsengpass selbst bleibt bestehen (beide Modelle gleichzeitig betroffen); der Fix macht das Verhalten der App dabei aber vorhersehbar (max. ~90s statt potenziell unbegrenzt) statt eines scheinbaren Hängers.
