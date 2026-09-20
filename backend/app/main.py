import logging

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.rate_limit import limiter
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
    dies ein reines No-Op — sentry_sdk.init wird dann NICHT aufgerufen. Das
    Performance-Tracing (traces_sample_rate) ist über settings.sentry_traces_sample_rate
    konfigurierbar (Standard: 1.0 = 100%, siehe app/config.py für die Kontingent-
    Überlegung bei echtem Produktivbetrieb).

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
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[StarletteIntegration(), FastApiIntegration()],
        )
    except Exception:
        logger.warning(
            "Sentry-Initialisierung fehlgeschlagen, Error-Tracking bleibt inaktiv", exc_info=True
        )


_init_sentry()

app = FastAPI(title="NotebookLM-Klon API")


def _handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Eigener 429-Handler statt slowapis `_rate_limit_exceeded_handler`-Default.

    Der slowapi-Default liefert `{"error": "Rate limit exceeded: ..."}` -- das Frontend
    (siehe frontend/src/api.ts, parseErrorMessage) liest bei Fehlerantworten aber
    ausschließlich das Feld `detail` (wie bei jedem anderen HTTPException-basierten
    Fehler in diesem Backend) und fällt sonst auf die rohe HTTP-Statustext-Meldung
    zurück. Ohne diesen eigenen Handler sähen Nutzer bei jedem 429 die unübersetzte
    Meldung "Too Many Requests" statt eines verständlichen deutschen Hinweises.
    """
    return JSONResponse(
        status_code=429,
        content={"detail": "Zu viele Anfragen. Bitte warte kurz und versuche es erneut."},
    )

# app.state.limiter wird von slowapi intern gelesen (siehe slowapi/extension.py), und
# von den @limiter.limit(...)-Decorators auf den einzelnen Router-Endpunkten verwendet
# (siehe app/rate_limit.py für die Begründung des In-Memory-Limiters und den
# Rate-Limit-Key). RateLimitExceeded ist eine starlette.exceptions.HTTPException-
# Unterklasse und wird deshalb -- genau wie ein normales `raise HTTPException(...)` in
# einem Endpunkt -- von Starlettes ExceptionMiddleware behandelt, welche INNERHALB
# dieser add_middleware-Aufrufe liegt. Der 429-Response erreicht
# CatchAllExceptionsMiddleware also nie als unbehandelte Exception und wird nicht
# fälschlich zu einem generischen 500 (siehe tests/test_rate_limit.py für den Nachweis).
app.state.limiter = limiter
# Eigener Handler statt slowapis Default (_rate_limit_exceeded_handler) -- siehe
# Begründung in _handle_rate_limit_exceeded() oben. Der Ignore-Kommentar unten bleibt
# trotzdem nötig, aber aus einem saubereren Grund als beim slowapi-Default: FastAPIs
# add_exception_handler() erwartet einen Handler, der generisch auf `Exception`
# typisiert ist, während unser Handler bewusst eng auf `RateLimitExceeded` typisiert
# ist (mehr Typsicherheit innerhalb der Funktion selbst). Laufzeitverhalten ist davon
# unberührt -- siehe tests/test_rate_limit.py für den Nachweis.
app.add_exception_handler(RateLimitExceeded, _handle_rate_limit_exceeded)  # type: ignore[arg-type]

app.add_middleware(CatchAllExceptionsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
# Wichtig: CORS schützt NUR Browser-JavaScript, das von einer fremden Origin aus
# Requests an dieses Backend schickt (der Browser blockt dort die Response für das
# aufrufende JS, falls die Origin nicht erlaubt ist). Ein direkter Server-zu-Server-
# oder curl/Skript-Request wird von CORS überhaupt nicht eingeschränkt -- Browser sind
# die einzige Stelle, die CORS-Header auswertet. Der eigentliche Zugriffsschutz ist
# deshalb die JWT-Pflicht auf den meisten Endpunkten (siehe app/auth.py), nicht CORS.

app.include_router(health.router)
app.include_router(notebooks.router)
app.include_router(sources.router)
app.include_router(notes.router)
app.include_router(chat.router)
app.include_router(presentations.router)
