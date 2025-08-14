from app.backend.dp_depends import get_db
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select, insert, delete, update
from typing import Optional, Annotated
from app.schemas import CreateCourse, CourseResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Course, User, Step

router = APIRouter(prefix="/course", tags=["course"])

sessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/")
async def get_courses(session: sessionDep):
    all_courses = await session.scalars(select(Course).where(Course.is_active == True))
    all_courses = all_courses.all()
    if all_courses:
        # courses = [{"id": c.id, "title": c.title, "description": c.description} for c in all_courses]
        courses = []
        for course in all_courses:
            course_data = CourseResponse(
                id = course.id,
                title=course.title,
                description=course.description
            )
            courses.append(course_data)
        return {"status_code": status.HTTP_200_OK, "courses": courses}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="There is no active course."
    )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(session: sessionDep, course_id: int):
    course = await session.scalar(
        select(Course).where(Course.is_active == True, Course.id == course_id)
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no active course."
        )
    return CourseResponse(
        id=course.id, title=course.title, description=course.description
    )


@router.post("/")
async def create_course(session: sessionDep, course_data: CreateCourse):
    await session.execute(
        insert(Course).values(
            title=course_data.title, description=course_data.description
        )
    )
    await session.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Successful"}
