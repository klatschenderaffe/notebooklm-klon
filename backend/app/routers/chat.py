from fastapi import APIRouter, Depends

from app.schemas import ChatCitation, ChatRequest, ChatResponse
from app.services import vector_store
from app.services.gemini_client import embed_texts, generate_answer
from app.services.notebooks_store import require_owned_notebook_id

router = APIRouter(prefix="/notebooks/{notebook_id}", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest, notebook_id: str = Depends(require_owned_notebook_id)
) -> ChatResponse:
    [query_embedding] = embed_texts([request.question], task_type="RETRIEVAL_QUERY")
    matches = vector_store.similarity_search(notebook_id, query_embedding)

    answer = generate_answer(request.question, [match["content"] for match in matches])
    citations = [
        ChatCitation(filename=match["filename"], excerpt=match["content"][:280])
        for match in matches
    ]
    return ChatResponse(answer=answer, citations=citations)
