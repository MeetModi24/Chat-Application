from __future__ import annotations
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models


def create_session(db: Session, user_id: uuid.UUID, title: str) -> models.ChatSession:
    session = models.ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[models.ChatSession]:
    return db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == user_id,
    ).first()


def list_sessions(db: Session, user_id: uuid.UUID) -> List[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user_id)
        .order_by(models.ChatSession.created_at.desc())
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