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
    tool_metadata: Optional[dict] = None,  # renamed
) -> models.Message:
    """Create a new message in a chat session."""
    message = models.Message(
        session_id=session_id,
        user_id=user_id,
        role=models.MessageRole(role),
        content=content,
        tool_calls=_normalize_tool_calls(tool_calls),
        tool_metadata=tool_metadata or {},  # renamed
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def list_messages_all(
    db: Session,
    session_id: uuid.UUID,
    order_desc: bool = False
) -> List[models.Message]:
    """Return all messages for a session, ordered by created_at."""
    q = db.query(models.Message).filter(models.Message.session_id == session_id)
    q = q.order_by(desc(models.Message.created_at)) if order_desc else q.order_by(models.Message.created_at)
    messages = q.all()
    for m in messages:
        m.tool_calls = _normalize_tool_calls(m.tool_calls)
        if m.tool_metadata is None:
            m.tool_metadata = {}
    return messages

def _normalize_tool_calls(tool_calls):
    """Ensure tool_calls is always a list."""
    if not tool_calls:
        return []
    if isinstance(tool_calls, dict):
        return [tool_calls]
    return tool_calls
