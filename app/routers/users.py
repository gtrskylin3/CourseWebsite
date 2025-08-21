from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, update, insert
from app.schemas import CourseResponse, UserCreateScheme, UserResponse
from app.models import User, Course, UserCourseProgress, Step
from app.backend.dp_depends import get_db
from app.utils.pw_utils import hash_pw
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.utils.current_user import get_current_user
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

@router.get("/my_courses")
async def user_courses(
    session: sessionDep,
    user: User = Depends(get_current_user)
):
    user_courses_all = await session.scalars(select(Course).where(Course.progress == user.progress))
    courses = []
    for course in user_courses_all.all():
            course_data = CourseResponse(
                id = course.id,
                title=course.title,
                description=course.description
            )
            courses.append(course_data)
    if not courses:
         raise HTTPException(status_code=404, detail="User progress not found")
    return {"status_code": status.HTTP_200_OK, "courses": courses}
