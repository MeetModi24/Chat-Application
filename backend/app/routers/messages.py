from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List
from ..db import get_db
from .. import models
from ..crud import messages as crud_messages
from ..schemas import MessageCreate, MessageOut
from ..auth.deps import get_current_user

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["messages"])

@router.get("", response_model=list[MessageOut])
def get_messages(
    session_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    roles: Optional[List[str]] = Query(None),
    since: Optional[str] = Query(None, description="ISO datetime string, inclusive"),
    order_desc: bool = Query(False),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # verify session ownership
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs, total = crud_messages.list_messages(db, session_id=session_id, limit=limit, offset=offset, roles=roles, since=since, order_desc=order_desc)
    # optionally include total count in header — for now return list; client can call a /count if needed
    return msgs

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def post_message(
    session_id: uuid.UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # store message (user_id only set if role == user)
    uid = user.id if payload.role == "user" else None
    msg = crud_messages.create_message(
        db,
        session_id=session_id,
        user_id=uid,
        role=payload.role,
        content=payload.content,
        tool_calls=[t.dict() for t in (payload.tool_calls or [])] if payload.tool_calls else None,
        metadata=payload.metadata,
    )
    return msg
