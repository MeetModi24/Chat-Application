# app/routers/participants.py
from __future__ import annotations
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..crud import sessions as crud_sessions
from ..schemas import SessionParticipantOut
from ..auth.deps import get_current_user

router = APIRouter(tags=["participants"])

@router.get("/sessions/{session_id}/participants", response_model=List[SessionParticipantOut])
def get_participants(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # must be participant
    if not crud_sessions.is_participant(db, session_id, user.id):
        raise HTTPException(status_code=403, detail="Not a participant")
    return crud_sessions.list_participants(db, session_id)


@router.post("/sessions/{session_id}/participants", response_model=SessionParticipantOut)
def add_participant_endpoint(
    session_id: uuid.UUID,
    payload: dict,  # you can create a schema for adding (email or user_id)
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # only owner can add directly (or allow participant invite flow)
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only owner can add participants")

    # Expect payload = {"user_id": "<uuid>"} or {"email": "x@y.com"} - implement accordingly
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    p = crud_sessions.add_participant(db, session_id=session_id, user_id=uuid.UUID(user_id))
    return p
