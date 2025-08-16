from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
from typing import List
from ..db import get_db
from .. import models
from ..crud import messages as crud_messages
from ..crud import sessions as crud_sessions
from ..schemas import MessageCreate, MessageOut
from ..auth.deps import get_current_user

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["messages"])


def _require_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> models.ChatSession:
    """Ensure that the given user is a participant in the chat session."""
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not crud_sessions.is_participant(db, session_id, user_id):
        raise HTTPException(status_code=403, detail="Not a participant")
    return session

@router.get("", response_model=List[MessageOut])
def get_messages(
    session_id: uuid.UUID,
    order_desc: bool = Query(False, description="Sort messages in descending order by creation time"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _require_participant(db, session_id, user.id)
    return crud_messages.list_messages_all(db, session_id=session_id, order_desc=order_desc)

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def post_message(
    session_id: uuid.UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _require_participant(db, session_id, user.id)
    return crud_messages.create_message(
        db,
        session_id=session_id,
        user_id=user.id if payload.role == "user" else None,
        role=payload.role,
        content=payload.content,
        tool_calls=[t.dict() for t in payload.tool_calls] if payload.tool_calls else None,
        tool_metadata=payload.tool_metadata,
    )
