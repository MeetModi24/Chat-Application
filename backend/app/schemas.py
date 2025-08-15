from __future__ import annotations
import uuid
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from uuid import UUID
import re
from datetime import datetime
from enum import Enum


# --- User ---
class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr

    class Config:
        from_attributes = True

# --- Chat Session ---
class ChatSessionCreate(BaseModel):
    title: str = Field(default="Untitled Session", max_length=255)

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)

class ChatSessionOut(BaseModel):
    id: uuid.UUID
    title: str
    owner_id: uuid.UUID
    participants: List[SessionParticipantOut] = []

    class Config:
        from_attributes = True

# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # user_id (uuid string)
    email: EmailStr
    exp: int

# --- Message ---
class MessageRole(str, Enum):
    user = "user"
    agent = "agent"
    system = "system"
    tool = "tool"

class ToolCall(BaseModel):
    """Represents a single tool interaction (example shape)."""
    tool: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- participants ---
class SessionParticipantOut(BaseModel):
    user_id: uuid.UUID
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

# --- invites ---
class InviteCreate(BaseModel):
    emails: List[EmailStr]  # invite multiple at once
    expires_in_hours: Optional[int] = 72  # default 3 days

class InviteOut(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    email: EmailStr
    token: str
    expires_at: Optional[datetime]
    accepted_by_user_id: Optional[uuid.UUID]
    accepted_at: Optional[datetime]
    revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class InviteAcceptRequest(BaseModel):
    token: str

