from datetime import datetime, timedelta, timezone
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Form,
    HTTPException,
    Response,
    status,
    Request,
)
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse, UserLoginScheme, TokenInfo
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils.pw_utils import check_pw, hash_pw
from app.utils.current_user import get_current_user
from app.config import settings
from app.utils.jwt_token import token_to_payload, jwt_encode_token
import jwt
from jwt.exceptions import (
    InvalidSubjectError,
    InvalidTokenError,
    PyJWTError,
    ExpiredSignatureError,
)

from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/cookie_auth", tags=["Auth"])

sessionDep = Annotated[AsyncSession, Depends(get_db)]



@router.post("/login", status_code=201)
async def login_cookie(
    session: sessionDep,
    user_data: Annotated[UserLoginScheme, Form()],
    response: Response,
):
    user = await session.scalar(select(User).where(User.username == user_data.username))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if check_pw(user_data.password, user.hashed_password):
        access_token = jwt_encode_token(
            payload={
                "sub": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
            }
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # запрещает JS доступ
            secure=True,  # только HTTPS
            samesite="lax",  # или "strict", если у тебя нет кросс-доменных запросов,
            max_age=60*60*60*60
        )
        return TokenInfo(access_token=access_token, token_type="Cookie")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/me", response_model=UserResponse)
async def get_active_user(user: User = Depends(get_current_user)):
    return user


@router.get("/logout")
async def logout_user(response: Response, user: User = Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {
        "user": UserResponse(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            id=user.id,
        ),
        "message": "Logged out",
    }
