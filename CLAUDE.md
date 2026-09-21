# NotebookLM-Klon — Projektkontext für Claude Code

Dieses Dokument beschreibt Architektur, Konventionen und Arbeitsweise dieses Projekts, damit Claude Code (oder andere KI-gestützte Werkzeuge) konsistent mit den bestehenden Entscheidungen weiterarbeiten kann.

## Projektüberblick

Ein NotebookLM-Klon: Nutzer laden Quellen (PDF, Markdown, URLs) in ein Notebook hoch und stellen Fragen dazu; die Antworten basieren ausschließlich auf den hochgeladenen Quellen (Retrieval-Augmented Generation) inklusive Zitatnachweis. Zusätzlich können aus den Quellen automatisch Präsentationen (PPTX) generiert werden.

**Stack:**
- **Backend:** Python 3.12, FastAPI, gehostet auf Render.
- **Frontend:** React 19, Vite, TypeScript, gehostet auf Cloudflare Workers (Workers-with-Assets-Modell, SPA-Fallback für Client-Side-Routing).
- **Datenbank/Auth/Storage:** Supabase (Postgres mit pgvector für Embeddings, Row-Level-Security für Multi-User-Isolation, Supabase Auth, Supabase Storage für Original-Dateien).
- **KI:** Google Gemini API (`google-genai` SDK) für Chat-Antworten, Präsentationsgliederungen und Embeddings.
- **Monitoring:** Sentry (Error- und Performance-Tracking, Backend und Frontend getrennt), UptimeRobot für Health-Checks.

## Repository-Struktur

```
backend/          FastAPI-Anwendung (app/), Tests (tests/), Supabase-Migrationen (supabase/migrations/)
frontend/         React/Vite-Anwendung (src/)
e2e/              Playwright End-to-End-Tests (laufen gegen echte Staging-Deployments)
infra/health-proxy/   Kleiner Cloudflare Worker, der Health-Checks für UptimeRobot proxy't
  (Render blockt bekannte Monitoring-Bot-Signaturen auf eigener Cloudflare-Zone;
  dieser Worker ruft /health stattdessen serverseitig ab)
.github/workflows/    CI/CD-Pipelines (ci.yml, e2e.yml)
.claude/agents/       Projektspezifische Subagenten für strukturierte Entwicklung
  (full-stack-developer, python-pro, code-reviewer, incident-responder, debugger)
PROGRESS.md       Chronologisches Änderungs-/Debugging-Log (wird nach jedem
                  wesentlichen Schritt aktualiert, inklusive Fehlschlägen und deren
                  Behebung — nicht nur Erfolge)
```

## Umgebungen

Drei vollständig getrennte Umgebungen, jeweils mit eigenem Deployment und eigener Datenbank:

| Umgebung | Frontend | Backend | Auslöser |
|---|---|---|---|
| **Lokal (Dev)** | `npm run dev` (Vite, localhost) | `uvicorn app.main:app --reload` gegen lokalen Supabase-CLI-Stack | manuell |
| **Staging** | Cloudflare Workers (Staging-Projekt) | Render (Staging-Service) | automatisch bei Push auf `develop` |
| **Produktion** | Cloudflare Workers (Produktions-Projekt) | Render (Produktions-Service) | automatisch bei Push auf `main` (= Merge eines PRs) |

Beide Cloudflare-Projekte und beide Render-Services sind über native Git-Integration direkt an ihre jeweilige Branch gekoppelt — kein manueller Deploy-Schritt nötig.

## Branch-Strategie & Git-Workflow

- `main` ist geschützt: Pull-Request-Pflicht auch für den Repo-Owner, mindestens 3 grüne CI-Checks (Secret Scan, Frontend, Backend), kein Force-Push.
- `develop` ist der aktive Arbeits-Branch und entspricht der Staging-Umgebung.
- Üblicher Ablauf für eine Änderung:
  1. Lokal committen (auf `main` oder einem Feature-Branch).
  2. `develop` auf den neuen Stand bringen und pushen → löst automatisch das Staging-Deployment aus.
  3. Auf der echten Staging-URL verifizieren (nicht nur auf grüne CI vertrauen).
  4. Pull Request von `develop` nach `main` erstellen, auf alle CI-Checks warten.
  5. Erst nach explizitem Review mergen → löst automatisch das Produktions-Deployment aus.
  6. Auch auf Produktion kurz verifizieren.
- Ein dedizierter End-to-End-Test (`e2e.yml`, Playwright) läuft regelmäßig und bei Bedarf manuell gegen die echte Staging-URL (nicht nur lokal) — prüft u. a. echten Login und einen echten Backend-Call.

## Backend: Entwicklung & Qualitätssicherung

```bash
cd backend
source .venv/bin/activate
ruff check app/ tests/          # Linting
ruff format --check app/ tests/ # Formatierung
mypy app/                       # Typprüfung
pytest -q                       # Tests (Mocks für externe Dienste, keine echten API-Calls)
```

Wichtige Konventionen:
- Externe Dienste (Gemini, Supabase) werden in Tests immer gemockt — nie echte Netzwerkaufrufe in der Test-Suite.
- Fehler von externen Diensten (Timeouts, Kontingent-/Kapazitätsgrenzen) werden nicht ungefangen durchgereicht, sondern als saubere, für Nutzer verständliche HTTP-Fehler (i. d. R. 503) behandelt. Für den Gemini-Chat-Aufruf existiert zusätzlich ein Fallback auf ein zweites, unabhängiges Modell, falls das primäre Modell überlastet ist oder sein Tageskontingent erreicht hat (Kontingente gelten pro Modell, nicht projektweit — siehe `backend/app/services/gemini_client.py`).
- Alle Endpunkte mit Nutzerbezug sind zusätzlich über Supabase Row-Level-Security abgesichert (Verteidigung in der Tiefe, nicht nur Anwendungslogik).
- Rate-Limiting (`slowapi`) ist pro authentifiziertem Nutzer konfiguriert, mit IP-basiertem Fallback für nicht authentifizierte Anfragen.

## Frontend: Entwicklung & Qualitätssicherung

```bash
cd frontend
npm run lint     # oxlint
npm run build    # tsc -b && vite build
npm run dev      # lokaler Dev-Server
```

Wichtige Konventionen:
- CSS wird mobile-first geschrieben: Basis-Styles für schmale Viewports, `min-width`-Media-Queries für größere Bildschirme.
- Fehlerzustände (z. B. fehlgeschlagene Chat-Antworten) werden als eigener, klar erkennbarer UI-Zustand behandelt, nicht als Teil des persistierten Nachrichtenverlaufs.

## Sicherheit

Bereits umgesetzte Maßnahmen (siehe `PROGRESS.md` für Details und Fundgeschichte):
- SSRF-Schutz bei URL-Quellen (keine internen/privaten Adressen abrufbar).
- Path-Traversal- und Storage-Key-Validierung bei Datei-Uploads (Erlaubnisliste statt Verbotsliste für Dateinamen).
- Content-Security-Policy und weitere Sicherheits-Header auf dem Frontend.
- Gitleaks-Secret-Scan als Pflicht-CI-Check.
- Kein Secret wird jemals geloggt oder in Fehlermeldungen zurückgegeben.

## Bekannte Einschränkungen

- Der Gemini API Free Tier hat sowohl kurzfristige Kapazitätsgrenzen ("high demand", 503) als auch harte Tageskontingente pro Modell (429, i. d. R. 20 Anfragen/Tag/Modell, Reset um Mitternacht Pacific Time). Die App reagiert darauf mit einem Fallback-Modell und klaren Fehlermeldungen, kann das zugrundeliegende Kontingent selbst aber nicht erhöhen.
- Render Free Tier: einzelne Instanz, Cold Starts nach Inaktivität (~30–50s bei der ersten Anfrage).
- Supabase Free Tier: maximal 2 aktive Projekte gleichzeitig — daher läuft die lokale Entwicklungsumgebung über die Supabase-CLI (lokaler Postgres) statt über ein drittes Cloud-Projekt.

## Wenn du an diesem Projekt arbeitest

- Lies `PROGRESS.md`, bevor du von einem größeren, bereits dokumentierten Fund/Fix ausgehst — viele auf den ersten Blick plausible Annahmen wurden dort bereits live widerlegt oder bestätigt.
- Verifiziere Verhalten von externen Bibliotheken/APIs nach Möglichkeit direkt (Quellcode lesen, echten Aufruf testen) statt sich auf Trainingsdaten oder Dokumentation allein zu verlassen — externe APIs und Bibliotheksversionen ändern sich schneller, als Dokumentation aktualisiert wird.
- Änderungen an `main` laufen ausschließlich über Pull Requests, auch für den Repo-Owner selbst.
