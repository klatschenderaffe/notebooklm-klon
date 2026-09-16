from pydantic import BaseModel


class SourceOut(BaseModel):
    id: str
    filename: str
    file_type: str
    created_at: str


class ChatRequest(BaseModel):
    question: str


class ChatCitation(BaseModel):
    filename: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]


class PresentationRequest(BaseModel):
    topic: str
    source_ids: list[str] | None = None
