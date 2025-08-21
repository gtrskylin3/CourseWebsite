from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select
from app.backend.dp_depends import get_db
from app.schemas import CourseResponse, CreateCourse, CreateStep, StepResponse, UserResponse
from app.utils.admin_check import is_admin 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models import Course, User, Step, UserCourseProgress
from typing import Annotated


router = APIRouter(prefix="/admin", dependencies=[Depends(is_admin)], tags=["admin"])

sessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/course-create")
async def create_course(session: sessionDep, course_data: CreateCourse):
    await session.execute(
        insert(Course).values(
            title=course_data.title, description=course_data.description
        )
    )
    await session.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Successful"}



@router.post("/step-create/{course_id}")
async def create_step(
    session: sessionDep,
    course_id: int,
    step_data: CreateStep,
):
    try:
        new_step = Step(
            title=step_data.title,
            order=step_data.order,
            text_content=step_data.text_content,
            image_url=step_data.image_url,
            video_url=step_data.video_url,
            course_id=course_id,
            is_end=step_data.is_end,
        )
        session.add(new_step)
        await session.commit()
        await session.refresh(new_step)
        return {"status_code": status.HTTP_200_OK,
                 "step": StepResponse(
                    id=new_step.id,
                    title=new_step.title,
                    text_content=new_step.text_content,
                    image_url=new_step.image_url,
                    video_url=new_step.video_url,
                    course_id=course_id,
                    is_end=new_step.is_end
                 )}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No courses found with this course_id",
        )


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
