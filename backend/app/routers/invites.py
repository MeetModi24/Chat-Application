# app/routers/invites.py
from __future__ import annotations
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..crud import sessions as crud_sessions
from ..schemas import InviteCreate, InviteOut, InviteAcceptRequest
from ..auth.deps import get_current_user

router = APIRouter(prefix="/sessions/{session_id}/invites", tags=["invites"])


@router.post("", response_model=List[InviteOut], status_code=status.HTTP_201_CREATED)
def create_session_invites(
    session_id: uuid.UUID,
    payload: InviteCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Only owner can create invites
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only owner can invite")

    invites = crud_sessions.create_invites(
        db, session_id=session_id, emails=payload.emails,
        created_by=user.id, expires_in_hours=payload.expires_in_hours
    )

    # optionally: schedule background email tasks here (not implemented)
    return invites


@router.get("", response_model=List[InviteOut])
def list_invites_for_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Only owner can list outstanding invites (you can relax this if desired)
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only owner can list invites")

    invites = db.query(models.ChatInvite).filter(models.ChatInvite.session_id == session_id).all()
    return invites


# NOTE: this endpoint accepts a token and is not nested under /sessions/{id}
# it belongs to a global invites router or you can mount it here via a different prefix.
