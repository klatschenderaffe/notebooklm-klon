# NotebookLM-Klon

Ein minimalistischer, selbst gehosteter Klon von [Google NotebookLM](https://notebooklm.google/): PDF- oder Markdown-Dateien hochladen und per KI ausschließlich auf Basis dieser Dateien Fragen stellen (Retrieval-Augmented Generation) sowie Präsentationen daraus generieren.

Der gesamte Projektverlauf — inklusive aller Entscheidungen, Probleme und Debugging-Schritte — wird fortlaufend in [`PROGRESS.md`](./PROGRESS.md) dokumentiert.

## Architektur

| Bereich | Technologie |
|---|---|
| Frontend | React + Vite + TypeScript, gehostet auf [Netlify](https://netlify.com) |
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
├── frontend/           React + Vite + TypeScript App (Netlify)
├── backend/             FastAPI App (Render)
├── .github/workflows/    CI/CD-Pipelines
├── netlify.toml         Netlify Build-Konfiguration
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

## Secrets & Umgebungsvariablen

**Dieses Repository ist öffentlich.** Es dürfen niemals echte API-Keys oder Zugangsdaten committet werden.

- Lokal: Werte in `.env` / `.env.local` eintragen (per `.gitignore` von Git ausgeschlossen).
- Produktiv: Werte direkt in den Secret-Verwaltungen von [Netlify](https://docs.netlify.com/environment-variables/overview/), [Render](https://render.com/docs/configure-environment-variables) und den [GitHub-Actions-Secrets](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions) hinterlegen.
- Jeder Push wird zusätzlich automatisch per [Gitleaks](https://github.com/gitleaks/gitleaks) auf versehentlich committete Secrets gescannt (`.github/workflows/ci.yml`).

Benötigte Variablen stehen in `backend/.env.example` und `frontend/.env.example`.

## Deployment

- **Frontend (Netlify):** automatisches Deployment bei Push auf `main`, Konfiguration in `netlify.toml`.
- **Backend (Render):** Deployment über das Blueprint in `render.yaml`.

## Tests & Qualitätssicherung

Läuft automatisch in CI bei jedem Push/PR (`.github/workflows/ci.yml`):
- Frontend: `oxlint` (Linting), `tsc` (Type-Check), `vite build` (Build-Check)
- Backend: `ruff` (Linting), `mypy` (Type-Check), `pytest` (Unit-Tests)
- Gitleaks (Secret-Scan)
