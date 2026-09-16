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
