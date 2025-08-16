# app/ws/manager.py
from __future__ import annotations
import uuid
from typing import Dict, Set
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..crud import messages as crud_messages


class ConnectionManager:
    """
    Manages active WebSocket connections for chat sessions.
    Handles joining, leaving, broadcasting, and saving messages to DB.
    """

    def __init__(self) -> None:
        # session_id -> set(websockets)
        self.active: Dict[uuid.UUID, Set[WebSocket]] = {}

    # -------------------------
    # Connection Management
    # -------------------------

    async def connect(self, session_id: uuid.UUID, websocket: WebSocket):
        """Accept a new WebSocket connection and track it by session_id."""
        await websocket.accept()
        self.active.setdefault(session_id, set()).add(websocket)

    def _cleanup_ws(self, session_id: uuid.UUID, websocket: WebSocket):
        """Remove a WebSocket from tracking, cleanup if session is empty."""
        self.active.get(session_id, set()).discard(websocket)
        if not self.active.get(session_id):
            self.active.pop(session_id, None)

    async def disconnect(self, session_id: uuid.UUID, websocket: WebSocket):
        """Disconnect and remove a WebSocket from tracking."""
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        self._cleanup_ws(session_id, websocket)

    # -------------------------
    # Broadcasting
    # -------------------------

    async def broadcast(self, session_id: uuid.UUID, message: dict):
        """
        Send a JSON message to all clients in the same session.
        Automatically removes disconnected sockets.
        """
        dead = []
        for ws in list(self.active.get(session_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(session_id, ws)

    # -------------------------
    # Database Interaction
    # -------------------------

    async def save_message(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID | None,
        role: models.MessageRole | str,
        content: str,
        tool_calls: list | None = None,
        tool_metadata: dict | None = None
    ) -> models.Message:
        """Save a chat message to the database using CRUD and return it."""

        def _save():
            db: Session = SessionLocal()
            try:
                # Validate role
                role_str = str(role)
                if role_str not in models.MessageRole._value2member_map_:
                    raise ValueError(f"Invalid role: {role_str}")

                # Normalize tool_calls and tool_metadata
                tool_calls_norm = crud_messages._normalize_tool_calls(tool_calls)
                tool_metadata_norm = tool_metadata or {}

                return crud_messages.create_message(
                    db=db,
                    session_id=session_id,
                    user_id=user_id if role_str == "user" else None,
                    role=role_str,
                    content=content,
                    tool_calls=tool_calls_norm,
                    tool_metadata=tool_metadata_norm,
                )
            finally:
                db.close()

        return await run_in_threadpool(_save)


# Global instance for use across app
manager = ConnectionManager()
