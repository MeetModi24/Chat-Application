from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..schemas import ChatSessionCreate, ChatSessionOut, ChatSessionUpdate
from ..crud import sessions as crud_sessions
from ..auth.deps import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: ChatSessionCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    chat_session = crud_sessions.create_session(db, user_id=user.id, title=payload.title)
    return chat_session

@router.get("/", response_model=list[ChatSessionOut])
def list_my_sessions(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud_sessions.list_sessions(db, user_id=user.id)

@router.get("/{session_id}", response_model=ChatSessionOut)
def get_session(session_id: uuid.UUID, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return chat_session

@router.put("/{session_id}", response_model=ChatSessionOut)
def update_session(session_id: uuid.UUID, payload: ChatSessionUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if payload.title:
        chat_session = crud_sessions.update_session(db, chat_session, title=payload.title)
    return chat_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: uuid.UUID, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    chat_session = crud_sessions.get_session(db, session_id=session_id, user_id=user.id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    crud_sessions.delete_session(db, chat_session)
    return
