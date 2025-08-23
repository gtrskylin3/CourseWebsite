from fastapi import Depends, HTTPException, Request, Response, status 
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse, UserLoginScheme, TokenInfo
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils.pw_utils import check_pw, hash_pw
from app.config import settings
from app.utils.jwt_token import check_token_by_type, create_access_token, token_to_payload, jwt_encode_token
import jwt
from jwt.exceptions import (
    InvalidSubjectError,
    InvalidTokenError,
    PyJWTError,
    ExpiredSignatureError,
)

# from app.routers.auth_cookie import get_token_from_cookie

sessionDep = Annotated[AsyncSession, Depends(get_db)]



async def get_access_token_from_cookie(
    request: Request,
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

async def get_refresh_token_from_cookie(
    request: Request,
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    await check_token_by_type(token, "refresh_token")
    
    return token


async def get_user_from_sub(session: sessionDep, payload:dict) -> User:
    try:
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

async def get_current_user(
    session: sessionDep, 
    token: str = Depends(get_access_token_from_cookie)
):
    payload = token_to_payload(token)
    user = await get_user_from_sub(session=session, payload=payload)
    return user
   
async def create_access_token_by_refresh_token(
    response: Response,
    session: sessionDep, 
    refresh_token: str = Depends(get_refresh_token_from_cookie)
):
    await check_token_by_type(refresh_token, "refresh_token")
    payload = token_to_payload(refresh_token)
    user = await get_user_from_sub(session=session, payload=payload)
    return create_access_token(user, response)
