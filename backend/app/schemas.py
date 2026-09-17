from pydantic import BaseModel


class NotebookOut(BaseModel):
    id: str
    name: str
    created_at: str


class NotebookCreate(BaseModel):
    name: str


class NotebookUpdate(BaseModel):
    name: str


class SourceOut(BaseModel):
    id: str
    filename: str
    file_type: str
    created_at: str


class UrlSourceRequest(BaseModel):
    url: str


class YoutubeSourceRequest(BaseModel):
    url: str


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
    design_description: str | None = None
    tone: str | None = None
    slide_count_hint: str | None = None


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: str
    content: str
    created_at: str


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[ChatCitation]
    created_at: str


class PresentationOut(BaseModel):
    id: str
    title: str
    topic: str
    created_at: str
