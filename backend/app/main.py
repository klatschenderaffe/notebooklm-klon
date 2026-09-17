import logging

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.routers import chat, health, notebooks, notes, presentations, sources

logger = logging.getLogger(__name__)


class CatchAllExceptionsMiddleware(BaseHTTPMiddleware):
    """Wandelt unbehandelte Exceptions in eine JSON-500-Antwort um.

    Ein @app.exception_handler(Exception) reicht dafür NICHT aus: FastAPI/Starlette
    routet Handler für die generische Exception-Klasse an ServerErrorMiddleware, die
    außerhalb von CORSMiddleware liegt — die Antwort bekäme dann keine
    Access-Control-Allow-Origin-Header und der Browser würde nur "Failed to fetch"
    melden. Diese Middleware muss deshalb NACH CORSMiddleware registriert werden
    (app.add_middleware wrappt in Aufruf-Reihenfolge von außen nach innen), damit ihre
    Antwort noch durch CORSMiddleware läuft.

    Wichtig: `app.add_middleware()` fügt jede Middleware VORNE in die interne Liste ein
    (nicht an), d.h. die zuletzt registrierte Middleware liegt am nächsten am Router.
    Damit diese Middleware innerhalb (näher am Router) von CORSMiddleware landet, MUSS
    sie VOR CORSMiddleware registriert werden (siehe Reihenfolge der add_middleware-
    Aufrufe unten) — sonst greift der Fix nicht.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unbehandelter Fehler bei %s %s", request.method, request.url.path)
            # Sentrys ASGI-Hook liegt außerhalb der per app.add_middleware() registrierten
            # Middlewares (siehe sentry_sdk/integrations/starlette.py, patch_asgi_app) und
            # bekommt Exceptions deshalb nie zu sehen, die hier abgefangen und nicht erneut
            # geworfen werden. Ohne diesen expliziten Aufruf würde Sentry strukturell NIE
            # einen der hier behandelten Fehler melden. capture_exception() ist ein No-Op,
            # falls Sentry nicht initialisiert wurde (kein SENTRY_DSN gesetzt).
            sentry_sdk.capture_exception()
            return JSONResponse(status_code=500, content={"detail": "Interner Serverfehler"})


def _init_sentry() -> None:
    """Initialisiert Sentry Error-Tracking, falls ein DSN konfiguriert ist.

    Bei leerem SENTRY_DSN (Standard, z.B. lokale Entwicklung/CI ohne Sentry-Account) ist
    dies ein reines No-Op — sentry_sdk.init wird dann NICHT aufgerufen. Nur
    Error-Tracking, kein Performance-Tracing (traces_sample_rate wird bewusst nicht
    gesetzt, Standard dafür ist None/aus).

    Diese Funktion läuft als bare Top-Level-Call beim Modul-Import, VOR `app =
    FastAPI(...)`. sentry_sdk.init() muss deshalb gegen Exceptions abgesichert werden:
    ein ungültiger SENTRY_DSN (z.B. Tippfehler in einer Render-Env-Var) darf niemals den
    kompletten Import von app/main.py und damit den Backend-Start verhindern — ein
    defektes Monitoring-Setup darf den Service nicht lahmlegen. Im Fehlerfall bleibt
    Sentry einfach inaktiv (wie bei leerem DSN) und der Fehler wird nur geloggt.
    """
    if not settings.sentry_dsn:
        return

    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    try:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            integrations=[StarletteIntegration(), FastApiIntegration()],
        )
    except Exception:
        logger.warning(
            "Sentry-Initialisierung fehlgeschlagen, Error-Tracking bleibt inaktiv", exc_info=True
        )


_init_sentry()

app = FastAPI(title="NotebookLM-Klon API")

app.add_middleware(CatchAllExceptionsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(notebooks.router)
app.include_router(sources.router)
app.include_router(notes.router)
app.include_router(chat.router)
app.include_router(presentations.router)
