# routers/users.py
from fastapi import APIRouter, Depends
from .deps import get_current_user
from ..schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def read_users_me(current_user = Depends(get_current_user)):
    return current_user
