from __future__ import annotations
import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

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

# --- Message ---
class MessageCreate(BaseModel):
    role: str
    content: str

class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str

    class Config:
        from_attributes = True