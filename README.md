# NotebookLM-Klon

Ein minimalistischer, selbst gehosteter Klon von [Google NotebookLM](https://notebooklm.google/): PDF-, Markdown- oder URL-Quellen hochladen und per KI ausschließlich auf Basis dieser Quellen Fragen stellen (Retrieval-Augmented Generation, inklusive Zitatnachweis) sowie Präsentationen daraus generieren.

Der gesamte Projektverlauf — inklusive aller Entscheidungen, Probleme und Debugging-Schritte — wird fortlaufend in [`PROGRESS.md`](./PROGRESS.md) dokumentiert. Architektur, Konventionen und der Entwicklungs-Workflow stehen in [`CLAUDE.md`](./CLAUDE.md).

## Architektur

| Bereich | Technologie |
|---|---|
| Frontend | React + Vite + TypeScript, gehostet auf [Cloudflare Workers](https://developers.cloudflare.com/workers/) (Workers-with-Assets, SPA-Fallback) |
| Backend | Python (FastAPI), gehostet auf [Render](https://render.com) |
| LLM & Embeddings | [Google Gemini API](https://aistudio.google.com), mit Modell-Fallback bei Kapazitäts-/Kontingent-Grenzen |
| Datenbank | [Supabase](https://supabase.com) (Postgres + pgvector für Embeddings, Row-Level-Security) |
| Datei-Storage | Supabase Storage (getrennte Buckets für Quellen und generierte Präsentationen) |
| Präsentations-Export | PPTX-Download (`python-pptx`) |
| Monitoring | [Sentry](https://sentry.io) (Error- & Performance-Tracking), [UptimeRobot](https://uptimerobot.com) (Health-Checks) |
| CI/CD | GitHub Actions (Lint, Type-Check, Unit-Tests, Build, Gitleaks Secret-Scan, Playwright E2E-Tests gegen Staging) |

Details und Begründungen zu jeder Entscheidung stehen im chronologischen Verlauf in `PROGRESS.md`.

## Projektstruktur

```
.
├── frontend/               React + Vite + TypeScript App (Cloudflare Workers)
│   └── wrangler.toml        Cloudflare-Workers-Konfiguration (Assets + SPA-Fallback)
├── backend/                 FastAPI App (Render)
│   └── supabase/migrations/ Versionierte Datenbank-Migrationen
├── e2e/                     Playwright End-to-End-Tests (laufen gegen echtes Staging)
├── infra/health-proxy/      Cloudflare Worker, proxy't Health-Checks für UptimeRobot
├── .github/workflows/       CI/CD-Pipelines
├── render.yaml              Render Blueprint (Backend, Produktion)
├── CLAUDE.md                Architektur, Konventionen, Entwicklungs-Workflow
└── PROGRESS.md               Chronologischer Projekt-Verlauf
```

## Lokale Entwicklung

### Voraussetzungen
- Node.js 26+
- Python 3.12+
- [Supabase CLI](https://supabase.com/docs/guides/cli) (für die lokale Datenbank, siehe unten)

### Lokale Datenbank (Supabase CLI)

```bash
cd backend
supabase start   # startet lokalen Postgres + Storage + Auth via Docker
```

Das gibt lokale API-URL, `anon`-Key und `service_role`-Key aus — diese in `backend/.env` eintragen (siehe unten). Die versionierten Migrationen in `backend/supabase/migrations/` werden dabei automatisch angewendet.

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # Werte eintragen, siehe .env.example für Details
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# VITE_SUPABASE_URL und VITE_SUPABASE_ANON_KEY sind Pflichtfelder (die App startet
# sonst nicht) -- Werte aus dem lokalen `supabase start`-Output oder dem
# Supabase-Projekt eintragen. VITE_API_URL nur anpassen, falls das Backend nicht
# unter http://localhost:8000 läuft.
npm run dev
```

Die App ist dann unter `http://localhost:5173` erreichbar, das Backend unter `http://localhost:8000`.

## Cloud-Setup (Staging/Produktion)

Für ein eigenes, in der Cloud gehostetes Supabase-Projekt (statt der lokalen CLI):

1. Projekt auf [supabase.com](https://supabase.com) anlegen.
2. **SQL Editor** → alle Dateien aus [`backend/supabase/migrations/`](./backend/supabase/migrations/) der Reihe nach ausführen (oder `supabase db push` mit verknüpftem Projekt).
3. **Storage** → zwei Buckets anlegen, beide **privat** (kein "Public bucket"):
   - `sources` (Größenlimit passend zu `MAX_UPLOAD_SIZE_BYTES` in `backend/app/config.py`, Standard 20 MB; erlaubte MIME-Types: `application/pdf`, `text/markdown`, `text/x-markdown`, `text/plain`)
   - `presentations` (für generierte PPTX-Dateien)
4. **Project Settings → Data API** → **Project URL** kopieren (die reine Projekt-URL, **nicht** die REST-Endpoint-URL mit `/rest/v1/`-Suffix — der `supabase-py`-Client hängt diesen Pfad selbst an).
5. Dort ebenfalls den **`service_role`**-Key kopieren (nicht `anon public`) sowie separat den **`anon`**-Key für das Frontend.
6. Werte in `backend/.env` (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`) und `frontend/.env.local` (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`) eintragen.

## Secrets & Umgebungsvariablen

**Dieses Repository ist öffentlich.** Es dürfen niemals echte API-Keys oder Zugangsdaten committet werden.

- Lokal: Werte in `.env` / `.env.local` eintragen (per `.gitignore` von Git ausgeschlossen).
- Produktiv: Werte direkt in den Secret-Verwaltungen von [Cloudflare Workers](https://developers.cloudflare.com/workers/configuration/environment-variables/), [Render](https://render.com/docs/configure-environment-variables) und den [GitHub-Actions-Secrets](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions) hinterlegen.
- Jeder Push wird zusätzlich automatisch per [Gitleaks](https://github.com/gitleaks/gitleaks) auf versehentlich committete Secrets gescannt (`.github/workflows/ci.yml`).

Benötigte Variablen stehen in `backend/.env.example` und `frontend/.env.example`.

## Deployment

Zwei vollständig getrennte Cloud-Umgebungen (Staging und Produktion), jeweils mit eigenem Cloudflare-Workers-Projekt, eigenem Render-Service und eigenem Supabase-Projekt — beide über native Git-Integration automatisch an ihre jeweilige Branch gekoppelt:

- Push auf `develop` → automatisches Deployment auf **Staging**.
- Push auf `main` (= Merge eines Pull Requests) → automatisches Deployment auf **Produktion**.

Für die Produktions-Backend-Konfiguration dient [`render.yaml`](./render.yaml) als Blueprint; das Staging-Backend ist separat als eigener Render-Service eingerichtet.

## Branch-Strategie

- **`main`** ist geschützt: Pull-Request-Pflicht auch für den Repo-Owner, mindestens 3 grüne CI-Checks (Secret Scan, Frontend, Backend), kein Force-Push. Ein Push auf `main` (per Merge) löst automatisch das Produktions-Deployment aus.
- **`develop`** ist der aktive Arbeits-Branch und entspricht der Staging-Umgebung — ein Push löst automatisch das Staging-Deployment aus.
- Üblicher Ablauf: auf `develop` committen und pushen → auf der echten Staging-URL verifizieren → Pull Request nach `main` erstellen → nach grüner CI und Review mergen → auf Produktion verifizieren.
- Ein dedizierter End-to-End-Test ([`e2e.yml`](./.github/workflows/e2e.yml), Playwright) läuft regelmäßig und bei Bedarf manuell gegen die echte Staging-URL — prüft u. a. echten Login und einen echten Backend-Call.

## Tests & Qualitätssicherung

Läuft automatisch in CI bei jedem Push/PR (`.github/workflows/ci.yml`):
- Frontend: `oxlint` (Linting), `tsc` (Type-Check), `vite build` (Build-Check)
- Backend: `ruff` (Linting), `mypy` (Type-Check), `pytest` (Unit-Tests, externe Dienste gemockt)
- Gitleaks (Secret-Scan)

Zusätzlich, regelmäßig gegen die echte Staging-Umgebung (`.github/workflows/e2e.yml`):
- Playwright End-to-End-Tests (echter Login-Flow, echter Backend-Call)

## Sicherheit

U. a. umgesetzt (Details und Fundgeschichte in `PROGRESS.md`): SSRF-Schutz bei URL-Quellen, Path-Traversal- und Storage-Key-Validierung bei Uploads, Row-Level-Security auf allen nutzerbezogenen Tabellen, Rate-Limiting pro Nutzer, Content-Security-Policy und weitere Sicherheits-Header, automatischer Secret-Scan in CI.
