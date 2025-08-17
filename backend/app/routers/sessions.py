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
    InviteCreate, InviteOut, InviteAcceptRequest, SessionParticipantOut,
    SessionParticipantCreate
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

# ------------------------------------------------------------
# Invites
# ------------------------------------------------------------

@router.post("/{session_id}/invites", response_model=InviteOut)
def create_session_invite(
    session_id: uuid.UUID,
    payload: InviteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not crud_sessions.is_participant(db, session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to invite")

    # 🔹 Ensure invitee email belongs to an existing user
    invitee = crud_sessions.get_user_by_email(db, payload.email)
    if not invitee:
        raise HTTPException(status_code=400, detail="Invalid email: no such user")

    inv = crud_sessions.create_invite(
        db=db,
        session_id=session_id,
        email=payload.email,
        created_by=current_user.id,
        expires_in_hours=payload.expires_in_hours,
    )
    if not inv:
        raise HTTPException(status_code=400, detail="Active invite already exists")
    return inv


@router.get("/me/invites", response_model=List[InviteOut])
def list_my_invites(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get all pending invites for the logged-in user."""
    return crud_sessions.list_user_invites(db, current_user.email)


@router.post("/invites/accept", response_model=InviteOut)
def accept_session_invite(
    payload: InviteAcceptRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    invite = crud_sessions.get_invite_by_token(db, payload.token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    try:
        accepted = crud_sessions.accept_invite(db, invite, current_user.id)
        return accepted
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/invites/{invite_id}/revoke", response_model=InviteOut)
def revoke_session_invite(
    session_id: uuid.UUID,
    invite_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not crud_sessions.is_participant(db, session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to revoke invite")

    inv = crud_sessions.revoke_invite(db, invite_id, session_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invite not found")
    return inv

# ------------------------------------------------------------
# Participants
# ------------------------------------------------------------

@router.get("/{session_id}/participants", response_model=List[SessionParticipantOut])
def get_participants(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not crud_sessions.is_participant(db, session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view participants")
    return crud_sessions.list_participants(db, session_id)


@router.post("/{session_id}/participants", response_model=SessionParticipantOut)
def add_session_participant(
    session_id: uuid.UUID,
    payload: SessionParticipantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not crud_sessions.is_participant(db, session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to add participants")

    participant = crud_sessions.add_participant(
        db, session_id, payload.user_id, payload.role
    )
    return participant
