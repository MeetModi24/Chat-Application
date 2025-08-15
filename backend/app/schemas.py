from __future__ import annotations
import uuid
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from uuid import UUID
import re
from datetime import datetime


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

class ToolCall(BaseModel):
    """Represents a single tool interaction (example shape)."""
    tool: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    tool_calls: Optional[Any] = None  # <-- Allow any JSON-serializable
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
