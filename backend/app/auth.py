from typing import Any

import jwt
import sentry_sdk
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from app.config import settings

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")
    return _jwks_client


def _decode_token(token: str) -> dict[str, Any]:
    """Supabase-Projekte signieren Auth-JWTs entweder mit einem legacy HS256-Secret
    (SUPABASE_JWT_SECRET) oder mit neueren asymmetrischen Signing Keys (ES256/RS256,
    verifiziert über den öffentlichen JWKS-Endpunkt). Welches Verfahren aktiv ist, steht
    im 'alg'-Header des Tokens selbst — daher wird hier zur Laufzeit verzweigt statt sich
    auf eine Annahme festzulegen."""
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg", "HS256")

    if algorithm == "HS256":
        key: Any = settings.supabase_jwt_secret
    else:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        key = signing_key.key

    return jwt.decode(token, key, algorithms=[algorithm], audience="authenticated")


def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")

    token = auth_header.removeprefix("Bearer ")
    try:
        payload = _decode_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Ungültiges oder abgelaufenes Token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Ungültiges Token")

    user_id = str(user_id)
    # Ordnet Sentry-Fehlerreports dieser Anfrage einem Nutzer zu, damit z.B. wiederholte
    # Fehler eines einzelnen Nutzers erkennbar sind. Bewusst NUR die user_id (keine
    # E-Mail/IP/sonstigen PII) statt des pauschalen send_default_pii=True-Schalters, um
    # keine unnötigen personenbezogenen Daten an Sentry zu übermitteln. set_user()
    # schreibt nur in den aktuellen Scope und ist ein No-Op, falls Sentry gar nicht
    # initialisiert wurde (kein SENTRY_DSN gesetzt) — siehe sentry_sdk.Scope.set_user.
    sentry_sdk.set_user({"id": user_id})

    # Für app/rate_limit.py: das Rate-Limit soll pro Nutzer statt pro IP greifen (siehe
    # Begründung dort), aber der Rate-Limit-Key wird von slowapi nur mit dem rohen
    # Request aufgerufen, nicht mit den von FastAPI aufgelösten Dependency-Werten. Da
    # diese Dependency IMMER vor dem eigentlichen Endpunkt (und damit vor der
    # Rate-Limit-Prüfung) läuft, kann der Rate-Limiter die hier einmal verifizierte
    # user_id einfach aus dem Request-State wiederverwenden, statt das JWT ein zweites
    # Mal zu decodieren.
    request.state.user_id = user_id

    return user_id
