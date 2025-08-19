from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
import jwt
from app.config import settings


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
    try:
        payload = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")