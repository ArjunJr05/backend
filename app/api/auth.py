from fastapi import APIRouter, HTTPException, Depends
from app.core.auth import UserCreate, UserLogin, Token, create_user, authenticate_user, get_current_user, TokenData

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    return await create_user(user.email, user.password)

@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    return await authenticate_user(user.email, user.password)

@router.get("/me")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "uid": current_user.uid
    }
