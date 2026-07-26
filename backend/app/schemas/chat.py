import uuid
import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    disclaimer: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ReportGenerateResponse(BaseModel):
    id: uuid.UUID
    pdf_path: str
    generated_at: datetime.datetime

    class Config:
        from_attributes = True
