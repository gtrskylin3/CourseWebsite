from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Response
from app.models.users import User
from app.schemas import UserCreateScheme, UserLoginScheme, UserScheme
import jwt
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.dp_depends import get_db

sessionDep = Annotated[AsyncSession, Depends(get_db)]

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
    to_encode.update(
        exp=expire, 
        iat=now)
    jwt_token = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
    return jwt_token

def token_to_payload(
    token: str,
    public_key = settings.public_key.read_text(),
    algorithm = "RS256"
) -> dict:
    try:
        payload = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    

def create_access_token(user: User, response: Response):
    payload={
        "sub": str(user.id),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
    }
    payload.update(type="access_token")
    access_token = jwt_encode_token(payload)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # запрещает JS доступ
        secure=True,  # только HTTPS
        samesite="lax",  # или "strict", если у тебя нет кросс-доменных запросов,
        max_age=60*60
    )
    return access_token

def create_refresh_token(response: Response, user : User):
    payload={
        "sub": str(user.id),
        "username": user.username
    }
    payload.update(type="refresh_token")
    refresh_token = jwt_encode_token(payload, expires_delta=timedelta(days=60))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # запрещает JS доступ
        secure=True,  # только HTTPS
        samesite="lax",  # или "strict", если у тебя нет кросс-доменных запросов,
        max_age=60*60*60*60
    )
    return refresh_token


async def check_token_by_type(token: str, token_type):
    data = token_to_payload(token)
    current_type = data.get("type")
    if current_type == token_type:
        return True
    raise HTTPException(401, f"Invalid token {current_type!r} expected {token_type!r}")
