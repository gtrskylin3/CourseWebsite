from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, update, insert
from app.schemas import UserCreateScheme, UserResponse
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from app.utils.pw_utils import hash_pw
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import bcrypt

sessionDep = Annotated[AsyncSession, Depends(get_db)]


router = APIRouter(prefix="/users", tags=['user'])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(session: sessionDep, user_data: UserCreateScheme):
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        hashed_password=hash_pw(password=user_data.password),
    )
    session.add(user)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")

    await session.refresh(instance=user)
    # return UserResponse(
    #         status_code= status.HTTP_200_OK,
    #         id=user.id,
    #         username=user.username,
    #         first_name=user.first_name,
    #         last_name=user.last_name,
    #     )
    return user

@router.get("/all")
async def get_all_users(session: sessionDep) -> list[UserResponse]:
    users = await session.scalars(select(User).where(User.is_active == True))
    users = users.all()
    response = [UserResponse(id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username) for user in users]
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not exists"
        )
    return response
