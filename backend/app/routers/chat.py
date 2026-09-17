from fastapi import APIRouter, Depends

from app.schemas import ChatCitation, ChatMessageOut, ChatRequest, ChatResponse
from app.services import history_store, vector_store
from app.services.gemini_client import embed_texts, generate_answer
from app.services.notebooks_store import require_owned_notebook_id

router = APIRouter(prefix="/notebooks/{notebook_id}", tags=["chat"])


@router.get("/chat/history", response_model=list[ChatMessageOut])
def get_chat_history(notebook_id: str = Depends(require_owned_notebook_id)) -> list[dict]:
    return history_store.list_chat_messages(notebook_id)


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest, notebook_id: str = Depends(require_owned_notebook_id)
) -> ChatResponse:
    history_store.insert_chat_message(notebook_id, "user", request.question, [])

    [query_embedding] = embed_texts([request.question], task_type="RETRIEVAL_QUERY")
    matches = vector_store.similarity_search(notebook_id, query_embedding)

    answer = generate_answer(request.question, [match["content"] for match in matches])
    citations = [
        ChatCitation(filename=match["filename"], excerpt=match["content"][:280])
        for match in matches
    ]

    history_store.insert_chat_message(
        notebook_id, "assistant", answer, [c.model_dump() for c in citations]
    )

    return ChatResponse(answer=answer, citations=citations)
