from __future__ import annotations
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from alembic import command
from alembic.config import Config
from .db import engine, Base, get_db
from .routers.sessions import router as sessions_router
from .auth.router import router as auth_router
from .routers import messages as messages_router
from .auth.deps import get_current_user
from .ws.manager import manager
from . import models
from jose import JWTError
from .auth.utils import decode_token

app = FastAPI(title="Insurge AI Backend")
origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_migrations():
    """
    Run Alembic migrations programmatically to latest head.
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@app.on_event("startup")
def on_startup():
    # Run DB migrations on startup
    run_migrations()


@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(messages_router.router)

# --- WebSocket with JWT: pass ?token=<JWT> on connect ---
@app.websocket("/ws/sessions/{session_id}")
async def session_ws(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    # Expect token in query string
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # policy violation
        return

    try:
        claims = decode_token(token)
    except JWTError:
        await websocket.close(code=1008)
        return

    user_id = claims.get("sub")
    email = claims.get("email")
    try:
        sid = uuid.UUID(session_id)
        uid = uuid.UUID(user_id)
    except Exception:
        await websocket.close(code=1003)
        return

    user = db.query(models.User).filter(models.User.id == uid, models.User.email == email).first()
    if not user:
        await websocket.close(code=1008)
        return

    session = db.query(models.ChatSession).filter(models.ChatSession.id == sid, models.ChatSession.user_id == user.id).first()
    if not session:
        await websocket.close(code=1008)
        return

    await manager.connect(sid, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            role = data.get("role", "user")
            content = data.get("content", "")
            tool_calls = data.get("tool_calls")
            metadata = data.get("metadata")

            if not content and not tool_calls:
                continue  # skip empty messages with no tool calls

            from .models import MessageRole
            r = MessageRole(role) if role in {"user", "agent", "system"} else MessageRole.user

            await manager.save_message(
                sid,
                user_id=user.id if r == MessageRole.user else None,
                role=r,
                content=content,
                tool_calls=tool_calls,
                metadata=metadata
            )

            await manager.broadcast(
                sid,
                {
                    "role": r.value,
                    "content": content,
                    "tool_calls": tool_calls,
                    "metadata": metadata
                }
            )
    except WebSocketDisconnect:
        await manager.disconnect(sid, websocket)
    except Exception:
        await manager.disconnect(sid, websocket)
