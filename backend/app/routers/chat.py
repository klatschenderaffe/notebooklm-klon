from fastapi import APIRouter

from app.schemas import ChatCitation, ChatRequest, ChatResponse
from app.services import vector_store
from app.services.gemini_client import embed_texts, generate_answer

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    [query_embedding] = embed_texts([request.question], task_type="RETRIEVAL_QUERY")
    matches = vector_store.similarity_search(query_embedding)

    answer = generate_answer(request.question, [match["content"] for match in matches])
    citations = [
        ChatCitation(filename=match["filename"], excerpt=match["content"][:280])
        for match in matches
    ]
    return ChatResponse(answer=answer, citations=citations)
