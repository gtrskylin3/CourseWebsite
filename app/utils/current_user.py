from fastapi import Depends, HTTPException, Request, status 
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse, UserLoginScheme, TokenInfo
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils.pw_utils import check_pw, hash_pw
from app.config import settings
from app.utils.jwt_token import token_to_payload, jwt_encode_token
import jwt
from jwt.exceptions import (
    InvalidSubjectError,
    InvalidTokenError,
    PyJWTError,
    ExpiredSignatureError,
)

# from app.routers.auth_cookie import get_token_from_cookie

sessionDep = Annotated[AsyncSession, Depends(get_db)]



async def get_token_from_cookie(
    request: Request,
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token



async def get_current_user(
    session: sessionDep, token: str = Depends(get_token_from_cookie)
):
    try:
        payload = token_to_payload(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = await session.scalar(select(User).where(User.id == int(user_id)))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except (InvalidSubjectError, InvalidTokenError, PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )