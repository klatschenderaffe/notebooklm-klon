import logging

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
            return JSONResponse(status_code=500, content={"detail": "Interner Serverfehler"})


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
