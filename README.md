# NotebookLM-Klon

Ein minimalistischer, selbst gehosteter Klon von [Google NotebookLM](https://notebooklm.google/): PDF- oder Markdown-Dateien hochladen und per KI ausschließlich auf Basis dieser Dateien Fragen stellen (Retrieval-Augmented Generation) sowie Präsentationen daraus generieren.

Der gesamte Projektverlauf — inklusive aller Entscheidungen, Probleme und Debugging-Schritte — wird fortlaufend in [`PROGRESS.md`](./PROGRESS.md) dokumentiert.

## Architektur

| Bereich | Technologie |
|---|---|
| Frontend | React + Vite + TypeScript, gehostet auf [Cloudflare Pages](https://pages.cloudflare.com) |
| Backend | Python (FastAPI), gehostet auf [Render](https://render.com) |
| LLM & Embeddings | [Google Gemini API](https://aistudio.google.com) |
| Vektordatenbank | [Supabase](https://supabase.com) (Postgres + pgvector) |
| Datei-Storage | Supabase Storage |
| Präsentations-Export | PPTX-Download (`python-pptx`) |
| CI/CD | GitHub Actions (Lint, Type-Check, Tests, Build, Gitleaks Secret-Scan) |

Details und Begründungen zu jeder Entscheidung stehen im Interview-Verlauf in `PROGRESS.md`.

## Projektstruktur

```
.
├── frontend/           React + Vite + TypeScript App (Cloudflare Pages)
│   └── wrangler.toml    Cloudflare Pages Build-Konfiguration
├── backend/             FastAPI App (Render)
├── .github/workflows/    CI/CD-Pipelines
├── render.yaml           Render Blueprint (Backend)
└── PROGRESS.md            Chronologischer Projekt-Verlauf
```

## Lokale Entwicklung

### Voraussetzungen
- Node.js 26+
- Python 3.12+

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # Werte eintragen (siehe unten)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # bei Bedarf VITE_API_URL anpassen
npm run dev
```

Die App ist dann unter `http://localhost:5173` erreichbar, das Backend unter `http://localhost:8000`.

## Supabase Setup

1. Projekt auf [supabase.com](https://supabase.com) anlegen.
2. Beim Projekt-Setup unter „Data API"-Optionen: **Enable Data API** an, **Automatically expose new tables** aus (nur relevant für `anon`/`authenticated`, siehe Grants unten), **Enable automatic RLS** an (schadet `service_role` nicht, siehe unten).
3. **SQL Editor** → Inhalt von [`backend/supabase/schema.sql`](./backend/supabase/schema.sql) ausführen. Das Schema enthält auch die nötigen `GRANT`-Statements für `service_role` — ohne "Automatically expose new tables" vergibt Supabase bei per SQL angelegten Tabellen sonst keine Rechte, selbst für `service_role` nicht (`service_role` umgeht zwar immer Row-Level-Security, aber nicht die separate SQL-`GRANT`-Ebene).
4. **Storage** → neuer Bucket `sources`, **privat** (kein "Public bucket"), Size-Limit 20 MB (passend zu `MAX_UPLOAD_SIZE_BYTES` in `backend/app/config.py`), erlaubte MIME-Types: `application/pdf`, `text/markdown`, `text/x-markdown`, `text/plain`.
5. **Project Settings → Data API** → **Project URL** kopieren. Wichtig: die reine Projekt-URL (`https://<ref>.supabase.co`) verwenden, **nicht** die dort ebenfalls angezeigte REST-Endpoint-URL mit `/rest/v1/`-Suffix — der `supabase-py`-Client hängt diesen Pfad selbst an.
6. Dort ebenfalls den **`service_role`**-Key kopieren (nicht `anon public`).
7. Beide Werte in `backend/.env` eintragen (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).

## Secrets & Umgebungsvariablen

**Dieses Repository ist öffentlich.** Es dürfen niemals echte API-Keys oder Zugangsdaten committet werden.

- Lokal: Werte in `.env` / `.env.local` eintragen (per `.gitignore` von Git ausgeschlossen).
- Produktiv: Werte direkt in den Secret-Verwaltungen von [Cloudflare Pages](https://developers.cloudflare.com/pages/configuration/build-configuration/#environment-variables), [Render](https://render.com/docs/configure-environment-variables) und den [GitHub-Actions-Secrets](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions) hinterlegen.
- Jeder Push wird zusätzlich automatisch per [Gitleaks](https://github.com/gitleaks/gitleaks) auf versehentlich committete Secrets gescannt (`.github/workflows/ci.yml`).

Benötigte Variablen stehen in `backend/.env.example` und `frontend/.env.example`.

## Deployment

- **Frontend (Cloudflare Pages):** Repo im [Cloudflare-Dashboard](https://dash.cloudflare.com) unter "Workers & Pages" verbinden, Build-Verzeichnis `frontend`, Build-Command `npm run build`, Output-Verzeichnis `dist` (siehe `frontend/wrangler.toml`). Danach automatisches Deployment bei jedem Push auf `main`.
- **Backend (Render):** Deployment über das Blueprint in `render.yaml`.

## Tests & Qualitätssicherung

Läuft automatisch in CI bei jedem Push/PR (`.github/workflows/ci.yml`):
- Frontend: `oxlint` (Linting), `tsc` (Type-Check), `vite build` (Build-Check)
- Backend: `ruff` (Linting), `mypy` (Type-Check), `pytest` (Unit-Tests)
- Gitleaks (Secret-Scan)
