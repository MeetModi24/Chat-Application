from __future__ import annotations
import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from uuid import UUID
import re



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