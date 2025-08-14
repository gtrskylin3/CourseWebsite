from app.backend.dp_depends import get_db
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select, insert, delete, update
from typing import Optional, Annotated
from app.schemas import (
    CreateCourse,
    CreateStep,
    StepResponse,
    StepListItem,
    StepListResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Course, User, Step

router = APIRouter(prefix="/steps", tags=["steps"])

sessionDep = Annotated[AsyncSession, Depends(get_db)]


# @router.get("/{course_id}")
# async def get_all_steps(session: sessionDep, course_id: int):
#     all_steps = await session.scalars(select(Step).where(Step.course_id == course_id))
#     all_steps = all_steps.all()

#     if all_steps:
#         response = []
#         for step in all_steps:
#             step_data = {"title": step.title}
#             if step.image_url:
#                 step_data["step_image"] = step.image_url
#             if step.text_content:
#                 step_data["text_content"] = step.text_content
#             if step.video_url:
#                 step_data["video_url"] = step.video_url

#             step_data["status"] = "Закончен" if step.is_end else "Не закончен"
#             response.append(step_data)
#         return {
#             "status_code": status.HTTP_200_OK,
#             "course_id": course_id,
#             "steps": response,
#         }
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="There are no steps in the course"
#     )


@router.get("/{course_id}", response_model=StepListResponse)
async def get_all_steps(session: sessionDep, course_id: int):
    all_steps = await session.scalars(select(Step).where(Step.course_id == course_id))
    all_steps = all_steps.all()

    if not all_steps:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no steps in the course",
        )
    steps_data = []
    for step in all_steps:
        step_item = StepListItem(
            title=step.title,
            step_image=step.image_url,
            text_content=step.text_content,
            video_url=step.video_url,
            status= "Закончен" if step.is_end else "Не закончен"
        )

        steps_data.append(step_item)
    return StepListResponse(
        status_code=status.HTTP_200_OK,
        course_id=course_id,
        steps=steps_data
    )


@router.post("/{course_id}", response_model=StepResponse)
async def create_step(
    session: sessionDep,
    course_id: int,
    step_data: CreateStep,
):
    try:
        new_step = Step(
            title=step_data.title,
            text_content=step_data.text_content,
            image_url=step_data.image_url,
            video_url=step_data.video_url,
            course_id=course_id,
            is_end=step_data.is_end,
        )
        session.add(new_step)
        await session.commit()
        await session.refresh(new_step)
        return {"status_code": status.HTTP_200_OK, "step": new_step}
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No courses found with this course_id",
        )
