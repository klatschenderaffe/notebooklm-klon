import pytest
from fastapi.testclient import TestClient

from app.services import vector_store
from tests.conftest import TEST_NOTEBOOK_ID


def test_unhandled_exception_returns_json_500_with_cors_header(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression test: a plain @app.exception_handler(Exception) would return a 500
    WITHOUT CORS headers (FastAPI/Starlette routes it to ServerErrorMiddleware, which
    sits outside CORSMiddleware), causing browsers to report "Failed to fetch" instead
    of the real error. CatchAllExceptionsMiddleware in app/main.py fixes this by
    catching the exception inside the middleware stack, below CORSMiddleware.
    """

    def raise_error(notebook_id: str) -> list[dict[str, str]]:
        raise RuntimeError("boom")

    monkeypatch.setattr(vector_store, "list_sources", raise_error)

    response = client.get(
        f"/notebooks/{TEST_NOTEBOOK_ID}/sources", headers={"Origin": "http://localhost:5173"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Interner Serverfehler"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
