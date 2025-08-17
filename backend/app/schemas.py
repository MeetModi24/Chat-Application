from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Base Config for ORM Models
# ============================================================

class ORMBase(BaseModel):
    """Base schema enabling Pydantic ORM mode."""
    class Config:
        from_attributes = True  # Allows converting from SQLAlchemy models


# ============================================================
# User Schemas
# ============================================================

class UserBase(ORMBase):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserOut(UserBase):
    id: uuid.UUID


# ============================================================
# Authentication Schemas
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user ID in string format
    email: EmailStr
    exp: int  # Unix timestamp for expiry


# ============================================================
# Chat Session Schemas
# ============================================================

class ChatSessionBase(ORMBase):
    title: str = Field(default="Untitled Session", max_length=255)


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)

class ChatSessionOut(ChatSessionBase):
    id: uuid.UUID
    created_at: datetime 
    user_id: uuid.UUID     # add owner
    # Optional: Include participants or owner if needed later


# ============================================================
# Message Schemas
# ============================================================

class MessageRole(str, Enum):
    user = "user"
    agent = "agent"
    system = "system"
    tool = "tool"


class ToolCall(BaseModel):
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
    tool_metadata: Optional[Dict[str, Any]] = None  # renamed

class MessageOut(ORMBase):
    id: uuid.UUID
    role: MessageRole
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_metadata: Optional[Dict[str, Any]] = None  # renamed
    created_at: datetime
    
    
# ============================================================
# Participant Schemas
# ============================================================

class SessionParticipantOut(ORMBase):
    session_id: uuid.UUID 
    user_id: uuid.UUID
    role: str
    joined_at: datetime    

class SessionParticipantCreate(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    role: str = "member"


# ============================================================
# Invite Schemas
# ============================================================

class InviteCreate(BaseModel):
    email: EmailStr   
    expires_in_hours: Optional[int] = Field(
        default=72, ge=1, le=720
    )  # allow None for "no expiry"


class InviteOut(ORMBase):
    id: uuid.UUID
    session_id: uuid.UUID
    email: EmailStr
    token: str
    expires_at: Optional[datetime]
    accepted_by_user_id: Optional[uuid.UUID]
    accepted_at: Optional[datetime]
    revoked: bool
    created_at: datetime
    created_by_user_id: Optional[uuid.UUID]
     # Extra fields for frontend
    inviter_email: Optional[str]
    session_name: Optional[str]


class InviteAcceptRequest(BaseModel):
    token: str
