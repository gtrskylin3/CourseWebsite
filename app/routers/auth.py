from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, status, Request
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse, UserLoginScheme, TokenInfo
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils import check_pw, hash_pw
from app.config import settings
import jwt

# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

sessionDep = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter(prefix="/auth")


def jwt_encode_token(
    payload: dict,
    private_key = settings.private_key.read_text(),
    algorithm = "RS256",
    expires_delta: timedelta | None = None
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(exp=expire, iat=now)
    jwt_token = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
    return jwt_token

def token_to_payload(
    token: str,
    public_key = settings.public_key.read_text(),
    algorithm = "RS256"
) -> dict:
    payload = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
    return payload

@router.post("/login")
async def login_authenticate(session: sessionDep, user_data: UserLoginScheme, request: Request):
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


@router.post("/token")
async def test_check(token: str = Body()):
    try:
        # token = credentials.credentials
        payload = token_to_payload(
            token=token,
        )
        print(payload)
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )