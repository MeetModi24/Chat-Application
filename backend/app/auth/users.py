# app/routers/users.py
from fastapi import APIRouter, Depends
from ..auth.deps import get_current_user
from ..schemas import UserOut
from .. import models

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Return the currently authenticated user's details."""
    return current_user

