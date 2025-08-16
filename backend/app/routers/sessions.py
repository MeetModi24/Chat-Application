# app/routers/sessions.py
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas import (
    ChatSessionCreate, ChatSessionOut, ChatSessionUpdate,
    InviteCreate, InviteOut, InviteAcceptRequest, SessionParticipantOut
)
from ..auth.deps import get_current_user
from ..crud import sessions as crud_sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])


# --- utils ---
def _require_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> models.ChatSession:
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not crud_sessions.is_participant(db, session_id, user_id):
        raise HTTPException(status_code=403, detail="Not a participant")
    return session


# --- create session (owner is also participant) ---
# @router.post("", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: ChatSessionCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    chat_session = crud_sessions.create_session(db, user_id=user.id, title=payload.title)
    # crud_sessions.add_owner_as_participant(db, chat_session.id, user.id)
    return chat_session


# --- list my sessions ---
@router.get("", response_model=List[ChatSessionOut])
@router.get("/", response_model=List[ChatSessionOut])
def list_my_sessions(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud_sessions.list_sessions_for_user(db, user.id)


# --- get a session ---
@router.get("/{session_id}", response_model=ChatSessionOut)
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return chat_session


# --- update session ---
@router.put("/{session_id}", response_model=ChatSessionOut)
def update_session(
    session_id: uuid.UUID,
    payload: ChatSessionUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if payload.title:
        chat_session = crud_sessions.update_session(db, chat_session, title=payload.title)
    return chat_session


# --- delete session ---
@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    crud_sessions.delete_session(db, chat_session)
    return


# --- invite multiple users by email ---
@router.post("/{session_id}/invites", response_model=List[InviteOut])
def create_session_invites(
    session_id: uuid.UUID,
    payload: InviteCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Only owner can invite
    own = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == user.id
    ).first()
    if not own:
        raise HTTPException(status_code=403, detail="Only owner can invite")

    invites = crud_sessions.create_invites(
        db, session_id, payload.emails, created_by=user.id,
        expires_in_hours=payload.expires_in_hours
    )

    # Email sending stub
    # for inv in invites:
    #     background.add_task(send_invite_email, inv.email, inv.token, session_id)

    return invites


# --- accept invite by token ---
@router.post("/invites/accept", response_model=InviteOut)
def accept_invite(
    payload: InviteAcceptRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    inv = crud_sessions.get_invite_by_token(db, payload.token)
    if not inv or inv.revoked:
        raise HTTPException(status_code=404, detail="Invite invalid")
    if inv.expires_at and inv.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Invite expired")

    crud_sessions.add_participant(db, inv.session_id, user.id)
    crud_sessions.accept_invite(db, inv, user.id)
    return inv


# --- join session without invite ---
@router.post("/{session_id}/join")
def join_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    crud_sessions.add_participant(db, session_id, user.id)
    return {"status": "joined"}


# --- list participants ---
@router.get("/{session_id}/participants", response_model=List[SessionParticipantOut])
def get_participants(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _require_participant(db, session_id, user.id)
    return crud_sessions.list_participants(db, session_id)
