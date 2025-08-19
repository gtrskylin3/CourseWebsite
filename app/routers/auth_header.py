from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status, Request
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse, UserLoginScheme, TokenInfo
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils.pw_utils import check_pw, hash_pw
from app.config import settings
from app.utils.jwt_token import jwt_encode_token, token_to_payload

from jwt.exceptions import InvalidSubjectError, InvalidTokenError, PyJWTError, ExpiredSignatureError

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/auth/login")

sessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(prefix="/auth")

@router.post("/login")
async def login_authenticate(session: sessionDep, user_data: Annotated[UserLoginScheme, Form()], request: Request):
    user = await session.scalar(select(User).where(User.username == user_data.username))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please register before login",
        )
    if check_pw(user_data.password, user.hashed_password):
        access_token = jwt_encode_token(
            payload={
                "sub": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        )
        return TokenInfo(access_token=access_token, token_type="Bearer")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )


async def get_current_user(
    # user_data: Annotated[UserLoginScheme, Form()],
    session: sessionDep,
    token: str = Depends(oauth2_scheme),  
) -> User:
    print(token)
    try:
        payload = token_to_payload(token=token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401,
                                detail="Invalid token payload")
        user = await session.scalar(select(User).where(User.id == int(user_id)))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except (InvalidSubjectError, InvalidTokenError, PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
                

@router.post("/me", response_model=UserResponse)
async def get_auth_user(
    user: User = Depends(get_current_user)
):
    return user