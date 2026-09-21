from pydantic import BaseModel, Field

# Großzügig bemessene Obergrenzen für Freitext-Eingabefelder. Ohne max_length könnte
# ein Client beliebig große Payloads senden, die unnötig viel Speicher/CPU beim
# Chunking/Embedding binden oder (bei question/content) den Gemini-Kontext sprengen.
# Die konkreten Werte orientieren sich an realistischer Nutzung, nicht an einem
# technischen Minimum -- z.B. ist eine 5000-Zeichen-Chatfrage bereits sehr lang für
# eine einzelne Frage, aber immer noch harmlos für den Server.
_SHORT_TEXT_MAX_LENGTH = 500
_LONG_TEXT_MAX_LENGTH = 5000
_URL_MAX_LENGTH = 2000


class NotebookOut(BaseModel):
    id: str
    name: str
    created_at: str


class NotebookCreate(BaseModel):
    name: str = Field(max_length=_SHORT_TEXT_MAX_LENGTH)


class NotebookUpdate(BaseModel):
    name: str = Field(max_length=_SHORT_TEXT_MAX_LENGTH)


class SourceOut(BaseModel):
    id: str
    filename: str
    file_type: str
    created_at: str


class UrlSourceRequest(BaseModel):
    url: str = Field(max_length=_URL_MAX_LENGTH)


class ChatRequest(BaseModel):
    question: str = Field(max_length=_LONG_TEXT_MAX_LENGTH)


class ChatCitation(BaseModel):
    filename: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]


class PresentationRequest(BaseModel):
    topic: str = Field(max_length=_SHORT_TEXT_MAX_LENGTH)
    source_ids: list[str] | None = None
    design_description: str | None = Field(default=None, max_length=_LONG_TEXT_MAX_LENGTH)
    tone: str | None = Field(default=None, max_length=_SHORT_TEXT_MAX_LENGTH)
    slide_count_hint: str | None = Field(default=None, max_length=_SHORT_TEXT_MAX_LENGTH)


class NoteCreate(BaseModel):
    content: str = Field(max_length=_LONG_TEXT_MAX_LENGTH)


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
