from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from .utils import decode_token
import logging
logger = logging.getLogger(__name__)

def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return authorization.split(" ", 1)[1].strip()

def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> models.User:
    logger.debug(f"Authorization header: {authorization}")
    token = _extract_bearer_token(authorization)
    try:
        payload = decode_token(token)
        logger.debug(f"Decoded JWT payload: {payload}")
    except JWTError as e:
        logger.error(f"JWT decode failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        logger.error("Token payload missing required fields")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == user_id, models.User.email == email).first()
    if not user:
        logger.error(f"No matching user found for ID={user_id}, email={email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user