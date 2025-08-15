from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from .. import models


def create_message(
    db: Session,
    session_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    role: str,
    content: str,
    tool_calls: Optional[list] = None,
    metadata: Optional[dict] = None,
) -> models.Message:
    message = models.Message(
        session_id=session_id,
        user_id=user_id,
        role=models.MessageRole(role),
        content=content,
        tool_calls=tool_calls or [],
        metadata=metadata or {},
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, session_id: uuid.UUID, order_desc: bool = False) -> List[models.Message]:
    """Return all messages for a session, ordered by created_at."""
    q = db.query(models.Message).filter(models.Message.session_id == session_id)
    q = q.order_by(desc(models.Message.created_at)) if order_desc else q.order_by(models.Message.created_at)
    messages = q.all()

    # Ensure tool_calls is always a list
    for m in messages:
        if m.tool_calls is None:
            m.tool_calls = []
        elif isinstance(m.tool_calls, dict):
            m.tool_calls = [m.tool_calls]
    return messages
