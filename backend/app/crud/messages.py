from typing import List, Optional, Tuple
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
    m = models.Message(
        session_id=session_id,
        user_id=user_id,
        role=models.MessageRole(role),
        content=content,
        tool_calls=tool_calls,
        metadata=metadata,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def list_messages(
    db: Session,
    session_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    roles: Optional[List[str]] = None,
    since: Optional[str] = None,
    order_desc: bool = False,
) -> Tuple[List[models.Message], int]:
    """
    Returns (messages, total_count)
    Supports limit/offset pagination. If you want cursor pagination we can add next.
    """
    q = db.query(models.Message).filter(models.Message.session_id == session_id)
    if roles:
        enums = [models.MessageRole(r) for r in roles]
        q = q.filter(models.Message.role.in_(enums))
    if since:
        # since should be ISO datetime string; rely on DB to compare strings if client passes ISO
        from sqlalchemy import text
        q = q.filter(models.Message.created_at >= since)
    total = q.count()
    if order_desc:
        q = q.order_by(desc(models.Message.created_at))
    else:
        q = q.order_by(models.Message.created_at)
    q = q.offset(offset).limit(limit)
    return q.all(), total
