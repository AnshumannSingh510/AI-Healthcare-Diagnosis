import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.chat import ChatHistory
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_client import generate_response, MEDICAL_SYSTEM_PROMPT

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    answer = await generate_response(payload.question, system=MEDICAL_SYSTEM_PROMPT)
    if settings.DISCLAIMER.lower() not in answer.lower():
        answer = f"{answer}\n\n{settings.DISCLAIMER}"

    entry = ChatHistory(user_id=current_user.id, question=payload.question, answer=answer)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return ChatResponse(
        id=entry.id, question=entry.question, answer=entry.answer,
        disclaimer=settings.DISCLAIMER, created_at=entry.created_at,
    )


@router.get("/chat/{user_id}/history", response_model=list[ChatResponse])
def chat_history(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    entries = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.asc()).all()
    return [
        ChatResponse(id=e.id, question=e.question, answer=e.answer, disclaimer=settings.DISCLAIMER, created_at=e.created_at)
        for e in entries
    ]
