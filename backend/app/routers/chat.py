from fastapi import APIRouter, Depends, Request

from app.config import settings
from app.rate_limit import limiter
from app.schemas import ChatCitation, ChatMessageOut, ChatRequest, ChatResponse
from app.services import history_store, vector_store
from app.services.gemini_client import embed_texts, generate_answer
from app.services.notebooks_store import require_owned_notebook_id

router = APIRouter(prefix="/notebooks/{notebook_id}", tags=["chat"])


@router.get("/chat/history", response_model=list[ChatMessageOut])
def get_chat_history(notebook_id: str = Depends(require_owned_notebook_id)) -> list[dict]:
    return history_store.list_chat_messages(notebook_id)


@router.post("/chat", response_model=ChatResponse)
# 10/Minute: teuerster Endpunkt (Embedding-Call + Gemini-Chat-Call pro Anfrage) auf
# einem geteilten API-Key -- siehe app/rate_limit.py. Großzügig genug für eine normale
# Chat-Konversation, eng genug um eine Endlosschleife (Bug oder Missbrauch) wirksam zu
# bremsen, bevor sie das Kontingent für alle Nutzer erschöpft.
@limiter.limit("10/minute")
def chat(
    request: Request,
    chat_request: ChatRequest,
    notebook_id: str = Depends(require_owned_notebook_id),
) -> ChatResponse:
    history_store.insert_chat_message(notebook_id, "user", chat_request.question, [])

    [query_embedding] = embed_texts([chat_request.question], task_type="RETRIEVAL_QUERY")
    all_matches = vector_store.similarity_search(notebook_id, query_embedding)
    matches = [m for m in all_matches if m["similarity"] >= settings.chat_similarity_threshold]
    # Live gefunden: der reine Schwellenwert-Filter konnte den besten -- oft einzigen
    # inhaltlich passenden -- Treffer komplett ausschließen, wenn seine Ähnlichkeit nur
    # knapp unter dem Schwellenwert lag (z.B. 0.62 bei 0.7), obwohl die Antwort
    # nachweislich in der Quelle stand. match_chunks liefert bereits absteigend nach
    # Ähnlichkeit sortiert (siehe "order by ... <=> ..." in der SQL-Funktion), daher ist
    # all_matches[0] immer der beste verfügbare Treffer für dieses Notebook. Der wird
    # jetzt immer aufgenommen, unabhängig vom Schwellenwert -- der filtert nur noch
    # zusätzliche, schwächere Treffer heraus, die reine Ähnlichkeits-Zufallstreffer sein
    # könnten (siehe test_chat_filters_out_low_similarity_matches).
    if all_matches and not matches:
        matches = [all_matches[0]]

    answer = generate_answer(chat_request.question, [match["content"] for match in matches])
    citations = [
        ChatCitation(filename=match["filename"], excerpt=match["content"][:280])
        for match in matches
    ]

    history_store.insert_chat_message(
        notebook_id, "assistant", answer, [c.model_dump() for c in citations]
    )

    return ChatResponse(answer=answer, citations=citations)
