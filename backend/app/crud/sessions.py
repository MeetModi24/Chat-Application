from __future__ import annotations
import uuid
import secrets
from datetime import timedelta, datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models
from sqlalchemy import or_

# ============================================================
# Participants CRUD
# ============================================================

def add_owner_as_participant(db: Session, session_id: uuid.UUID, owner_id: uuid.UUID):
    """Ensure session owner is added as participant with role=owner"""
    row = models.ChatSessionParticipant(
        session_id=session_id,
        user_id=owner_id,
        role="owner"
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        row = db.query(models.ChatSessionParticipant).filter_by(
            session_id=session_id, user_id=owner_id
        ).first()
    return row


def add_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID, role: str = "member"):
    """Add a participant, default role=member. Handles duplicate gracefully."""
    row = models.ChatSessionParticipant(
        session_id=session_id,
        user_id=user_id,
        role=role
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()  # already a participant
        row = db.query(models.ChatSessionParticipant).filter_by(
            session_id=session_id, user_id=user_id
        ).first()
    return row


def is_participant(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Check if a user is a participant or the owner of the session"""
    # Direct participant
    if db.query(models.ChatSessionParticipant).filter(
        models.ChatSessionParticipant.session_id == session_id,
        models.ChatSessionParticipant.user_id == user_id
    ).first():
        return True

    # Session owner
    if db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == user_id
    ).first():
        return True

    return False


def list_participants(db: Session, session_id: uuid.UUID) -> List[models.ChatSessionParticipant]:
    """Return all participants of a session, ordered by join time"""
    return (
        db.query(models.ChatSessionParticipant)
        .filter(models.ChatSessionParticipant.session_id == session_id)
        .order_by(models.ChatSessionParticipant.joined_at)
        .all()
    )



# --- Sessions ---
def create_session(db: Session, user_id: uuid.UUID, title: str) -> models.ChatSession:
    session = models.ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .outerjoin(models.ChatSessionParticipant)
        .filter(
            models.ChatSession.id == session_id,
            ((models.ChatSessionParticipant.user_id == user_id) |
             (models.ChatSession.user_id == user_id))  # include owner
        )
        .first()
    )



def list_sessions_for_user(db: Session, user_id: uuid.UUID) -> List[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .outerjoin(
            models.ChatSessionParticipant,
            models.ChatSessionParticipant.session_id == models.ChatSession.id
        )
        .filter(
            (models.ChatSessionParticipant.user_id == user_id) |
            (models.ChatSession.user_id == user_id)  # include owner
        )
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


# ============================================================
# Invites CRUD
# ============================================================

def _invite_token() -> str:
    return secrets.token_urlsafe(32)

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_invite(
    db: Session,
    session_id: uuid.UUID,
    email: str,
    created_by: uuid.UUID,
    expires_in_hours: Optional[int] = 72,
) -> Optional[models.ChatInvite]:
    """Create a single invite for given email, skipping existing active one"""
    email = email.lower().strip()

    # Check if active invite already exists
    existing = db.query(models.ChatInvite).filter(
        models.ChatInvite.session_id == session_id,
        models.ChatInvite.email == email,
        models.ChatInvite.revoked == False
    ).first()

    if existing:
        return None

    expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        if expires_in_hours else None
    )

    inv = models.ChatInvite(
        session_id=session_id,
        email=email,
        token=_invite_token(),
        expires_at=expires_at,
        created_by_user_id=created_by,
    )

    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def get_invite_by_token(db: Session, token: str) -> Optional[models.ChatInvite]:
    """Retrieve invite by its token"""
    return db.query(models.ChatInvite).filter(models.ChatInvite.token == token).first()


def accept_invite(db: Session, invite: models.ChatInvite, user_id: uuid.UUID):
    """Accept invite if not expired or revoked, link to user"""
    if invite.revoked:
        raise ValueError("Invite has been revoked")
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise ValueError("Invite expired")

    invite.accepted_by_user_id = user_id
    invite.accepted_at = datetime.now(timezone.utc)

    db.add(invite)
    db.commit()
    db.refresh(invite)

    # Add user as participant
    add_participant(db, invite.session_id, user_id)

    return invite


def revoke_invite(db: Session, invite_id: uuid.UUID, session_id: uuid.UUID):
    """Mark invite as revoked"""
    inv = db.query(models.ChatInvite).filter(
        models.ChatInvite.id == invite_id,
        models.ChatInvite.session_id == session_id
    ).first()
    if inv:
        inv.revoked = True
        db.commit()
        db.refresh(inv)
    return inv

def list_user_invites(db: Session, email: str) -> List[models.ChatInvite]:
    return (
        db.query(models.ChatInvite)
        .filter(
            models.ChatInvite.email == email,
            models.ChatInvite.revoked.is_(False),
            models.ChatInvite.accepted_at.is_(None),
            or_(
                models.ChatInvite.expires_at.is_(None),
                models.ChatInvite.expires_at > datetime.now(timezone.utc)
            )
        )

        .all()
    )