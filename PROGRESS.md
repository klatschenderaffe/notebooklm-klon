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
