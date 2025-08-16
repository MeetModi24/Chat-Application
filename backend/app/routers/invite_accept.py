# app/routers/invite_accept.py
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..crud import sessions as crud_sessions
from ..schemas import InviteAcceptRequest, InviteOut
from ..auth.deps import get_current_user
from datetime import datetime, timezone

router = APIRouter(tags=["invites"])

@router.post("/invites/accept", response_model=InviteOut)
def accept_invite_endpoint(
    payload: InviteAcceptRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    inv = crud_sessions.get_invite_by_token(db, payload.token)
    if not inv or inv.revoked:
        raise HTTPException(status_code=404, detail="Invite invalid")
    if inv.expires_at and inv.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Invite expired")

    # mark invite accepted
    inv = crud_sessions.accept_invite(db, inv, user.id)

    # add participant (idempotent)
    crud_sessions.add_participant(db, inv.session_id, user.id)

    return inv
