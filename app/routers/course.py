from app.backend.dp_depends import get_db
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select, insert, delete, update

router = APIRouter("/course", tags=['course'])


