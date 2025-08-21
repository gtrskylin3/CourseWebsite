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
            order=step.order,
            status= "Закончен" if step.is_end else "Не закончен"
        )

        steps_data.append(step_item)
    return StepListResponse(
        status_code=status.HTTP_200_OK,
        course_id=course_id,
        steps=steps_data
    )
