import jwt
import pytest
from fastapi.testclient import TestClient

import app.routers.chat as chat_router
import app.routers.presentations as presentations_router
import app.services.notebooks_store as notebooks_store
from app.config import settings
from app.main import app
from tests.conftest import TEST_NOTEBOOK_ID

CHAT_URL = f"/notebooks/{TEST_NOTEBOOK_ID}/chat"
PRESENTATIONS_URL = f"/notebooks/{TEST_NOTEBOOK_ID}/presentations"


def _stub_chat_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        chat_router.history_store,
        "insert_chat_message",
        lambda notebook_id, role, content, citations: None,
    )
    monkeypatch.setattr(chat_router, "embed_texts", lambda texts, task_type: [[0.1, 0.2]])
    monkeypatch.setattr(
        chat_router.vector_store,
        "similarity_search",
        lambda notebook_id, query_embedding, match_count=6: [],
    )
    monkeypatch.setattr(chat_router, "generate_answer", lambda question, context_chunks: "Antwort")


def test_chat_endpoint_returns_429_after_limit_exceeded(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """chat ist auf 10/Minute limitiert (siehe app/routers/chat.py). Die ersten 10
    Anfragen innerhalb einer Minute müssen durchgehen, die 11. muss mit 429
    abgelehnt werden, statt das geteilte Gemini-Kontingent unbegrenzt zu belasten."""
    _stub_chat_dependencies(monkeypatch)

    for _ in range(10):
        response = client.post(CHAT_URL, json={"question": "Frage?"})
        assert response.status_code == 200

    response = client.post(CHAT_URL, json={"question": "Frage?"})
    assert response.status_code == 429


def test_chat_rate_limit_response_is_not_swallowed_into_generic_500(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression-Absicherung für die in app/main.py dokumentierte Reihenfolge:
    RateLimitExceeded muss von Starlettes ExceptionMiddleware behandelt werden, BEVOR
    CatchAllExceptionsMiddleware sie zu einem generischen 500 verwandeln könnte -- und
    die Response muss trotzdem (wie jede andere Antwort) einen CORS-Header tragen."""
    _stub_chat_dependencies(monkeypatch)

    for _ in range(10):
        client.post(CHAT_URL, json={"question": "Frage?"})

    response = client.post(
        CHAT_URL, json={"question": "Frage?"}, headers={"Origin": "http://localhost:5173"}
    )

    assert response.status_code == 429
    assert response.json() != {"detail": "Interner Serverfehler"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_rate_limit_response_uses_detail_field_with_german_message(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Das Frontend (frontend/src/api.ts, parseErrorMessage) liest bei Fehlerantworten
    ausschließlich `body.detail`. slowapis eigener Default-Handler liefert stattdessen
    `{"error": "..."}`, was im Frontend unbemerkt auf die rohe, unübersetzte
    HTTP-Statustext-Meldung zurückfallen würde -- siehe app/main.py,
    _handle_rate_limit_exceeded."""
    _stub_chat_dependencies(monkeypatch)

    for _ in range(10):
        client.post(CHAT_URL, json={"question": "Frage?"})

    response = client.post(CHAT_URL, json={"question": "Frage?"})

    assert response.status_code == 429
    assert response.json() == {
        "detail": "Zu viele Anfragen. Bitte warte kurz und versuche es erneut."
    }


def _bearer_header_for(user_id: str) -> dict[str, str]:
    token = jwt.encode(
        {"sub": user_id, "aud": "authenticated"}, "test-secret", algorithm="HS256"
    )
    return {"Authorization": f"Bearer {token}"}


def test_rate_limit_is_scoped_per_user_not_per_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Beweist die zentrale Behauptung im Docstring von app.rate_limit._rate_limit_key:
    das Limit greift pro Nutzer-Konto (request.state.user_id, gesetzt von der
    get_current_user_id-Dependency VOR der Rate-Limit-Prüfung), nicht pro IP-Adresse.

    Bewusst OHNE dependency_overrides für get_current_user_id: ein Override würde die
    echte Dependency (und damit das Setzen von request.state.user_id, siehe
    app/auth.py) komplett umgehen -- der Rate-Limiter würde dann selbst bei
    unterschiedlichen "Nutzern" auf den in _rate_limit_key dokumentierten
    IP-Fallback zurückfallen und der Test würde einen Bug vortäuschen, der gar keiner
    ist. Stattdessen laufen hier zwei echte, unterschiedlich signierte JWTs (also
    zwei verschiedene user_id-Werte) durch die volle, reale Dependency-Resolution --
    über denselben TestClient und damit garantiert dieselbe Quell-IP. Erschöpft
    Nutzer A sein Kontingent, muss Nutzer B direkt danach trotzdem noch durchkommen --
    nur getrennte Buckets pro Nutzer-Konto erklären das."""
    monkeypatch.setattr(settings, "supabase_jwt_secret", "test-secret")
    _stub_chat_dependencies(monkeypatch)
    monkeypatch.setattr(
        notebooks_store,
        "get_owned_notebook",
        lambda user_id, notebook_id: {"id": notebook_id, "user_id": user_id, "name": "Test"},
    )
    test_client = TestClient(app)

    user_a_headers = _bearer_header_for("user-a")
    for _ in range(10):
        response = test_client.post(CHAT_URL, json={"question": "Frage?"}, headers=user_a_headers)
        assert response.status_code == 200
    response = test_client.post(CHAT_URL, json={"question": "Frage?"}, headers=user_a_headers)
    assert response.status_code == 429

    user_b_headers = _bearer_header_for("user-b")
    response = test_client.post(CHAT_URL, json={"question": "Frage?"}, headers=user_b_headers)
    assert response.status_code == 200


def test_presentations_endpoint_returns_429_after_limit_exceeded(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """create_presentation ist auf 5/Minute limitiert (teuerster Endpunkt, siehe
    app/routers/presentations.py)."""
    monkeypatch.setattr(
        presentations_router.vector_store,
        "chunks_for_sources",
        lambda notebook_id, source_ids: [],
    )

    for _ in range(5):
        response = client.post(PRESENTATIONS_URL, json={"topic": "Testthema"})
        # Ohne Quellen liefert der Endpunkt 422 -- uns interessiert hier nur, dass die
        # Anfrage überhaupt durch die Rate-Limit-Prüfung kommt, nicht der Fachfehler.
        assert response.status_code == 422

    response = client.post(PRESENTATIONS_URL, json={"topic": "Testthema"})
    assert response.status_code == 429


def test_rate_limit_is_scoped_per_endpoint_not_per_notebook_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression-Test für key_style="endpoint" in app/rate_limit.py: notebook_id
    steht als Pfad-Segment in der URL. Mit dem slowapi-Default (key_style="url")
    bekäme jede notebook_id ihren eigenen Rate-Limit-Bucket, und ein Nutzer könnte das
    Limit umgehen, indem er auf mehrere Notebooks verteilt. Zwei verschiedene
    notebook_ids müssen sich deshalb dasselbe Kontingent teilen."""
    _stub_chat_dependencies(monkeypatch)
    other_notebook_url = "/notebooks/33333333-3333-3333-3333-333333333333/chat"

    for _ in range(5):
        assert client.post(CHAT_URL, json={"question": "Frage?"}).status_code == 200
    for _ in range(5):
        assert client.post(other_notebook_url, json={"question": "Frage?"}).status_code == 200

    response = client.post(CHAT_URL, json={"question": "Frage?"})
    assert response.status_code == 429
