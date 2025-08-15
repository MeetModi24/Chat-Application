from __future__ import annotations
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models
import secrets
from datetime import timedelta, datetime, timezone
from sqlalchemy.exc import IntegrityError


def create_session(db: Session, user_id: uuid.UUID, title: str) -> models.ChatSession:
    session = models.ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    add_owner_as_participant(db, session.id, user_id)
    return session


def get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .join(models.ChatSessionParticipant)
        .filter(
            models.ChatSession.id == session_id,
            models.ChatSessionParticipant.user_id == user_id
        )
        .first()
    )


def list_sessions(db: Session, user_id: uuid.UUID) -> List[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user_id)
        .order_by(models.ChatSession.created_at.desc())
        .all()
    )

def list_sessions_for_user(db: Session, user_id: uuid.UUID) -> list[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .join(models.SessionParticipant, models.SessionParticipant.session_id == models.ChatSession.id)
        .filter(models.SessionParticipant.user_id == user_id)
        .all()
    )


def update_session(db: Session, chat_session: models.ChatSession, title: str) -> models.ChatSession:
    chat_session.title = title
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return chat_session


def delete_session(db: Session, chat_session: models.ChatSession) -> None:
    db.delete(chat_session)
    db.commit()

def add_owner_as_participant(db: Session, session_id: uuid.UUID, owner_id: uuid.UUID):
    row = models.ChatSessionParticipant(session_id=session_id, user_id=owner_id, role="owner")
    db.add(row)
    db.commit()

def add_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID, role: str = "member"):
    row = models.ChatSessionParticipant(session_id=session_id, user_id=user_id, role=role)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # already a participant
    return row

def is_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    return db.query(models.ChatSessionParticipant)\
        .filter(models.ChatSessionParticipant.session_id == session_id,
                models.ChatSessionParticipant.user_id == user_id)\
        .first() is not None

def list_participants(db: Session, session_id: uuid.UUID) -> List[models.ChatSessionParticipant]:
    return db.query(models.ChatSessionParticipant)\
        .filter(models.ChatSessionParticipant.session_id == session_id)\
        .order_by(models.ChatSessionParticipant.joined_at)\
        .all()

# invites
def _invite_token() -> str:
    return secrets.token_urlsafe(32)

def create_invites(db: Session, session_id: uuid.UUID, emails: List[str], created_by: uuid.UUID, expires_in_hours: int = 72) -> List[models.ChatInvite]:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours) if expires_in_hours else None
    out = []
    existing = {
        i.email for i in db.query(models.ChatInvite)
            .filter(models.ChatInvite.session_id == session_id,
                    models.ChatInvite.revoked == False)
            .all()
    }
    for email in emails:
        email = email.lower().strip()
        if email in existing:
            continue    
        inv = models.ChatInvite(
            session_id=session_id,
            email=email.lower().strip(),
            token=_invite_token(),
            expires_at=expires_at,
            created_by_user_id=created_by,
        )
        db.add(inv)
        out.append(inv)
    db.commit()
    for inv in out:
        db.refresh(inv)
    return out

def get_invite_by_token(db: Session, token: str) -> Optional[models.ChatInvite]:
    return db.query(models.ChatInvite).filter(models.ChatInvite.token == token).first()

def accept_invite(db: Session, invite: models.ChatInvite, user_id: uuid.UUID):
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise ValueError("Invite expired")
    invite.accepted_by_user_id = user_id
    invite.accepted_at = datetime.now(timezone.utc)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite

def revoke_invite(db: Session, invite_id: uuid.UUID, session_id: uuid.UUID):
    inv = db.query(models.ChatInvite)\
        .filter(models.ChatInvite.id == invite_id,
                models.ChatInvite.session_id == session_id)\
        .first()
    if inv:
        inv.revoked = True
        db.commit()
        db.refresh(inv)
    return inv
