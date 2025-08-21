from app.backend.dp_depends import get_db
from fastapi import Body, Depends, APIRouter, HTTPException, status
from sqlalchemy import select, insert, delete, update
from typing import Optional, Annotated
from app.schemas import CreateCourse, CourseResponse, StepResponse, UserProgressResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models import Course, User, Step, UserCourseProgress
from app.utils.current_user import get_current_user


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
                id=course.id, title=course.title, description=course.description
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


@router.post("/start/{course_id}")
async def start_course(
    course_id: int,
    session: sessionDep,
    user: User = Depends(get_current_user),
):
    step = await session.scalar(
        select(Step)
        .where(Step.course_id == course_id, Step.is_active == True)
        .order_by(Step.order.asc())
    )
    if not step:
        raise HTTPException(status_code=404, detail="Course has no active steps")

    user_progress = await session.get(
        UserCourseProgress, {"user_id": user.id, "course_id": course_id}
    )
    if not user_progress:
        user_progress = UserCourseProgress(
            user_id=user.id, course_id=course_id, current_step_id=step.id
        )
        session.add(user_progress)
        await session.commit()
        await session.refresh(user_progress)
        return {
            "start": "Successful",
            "first_step": StepResponse(
                id=step.id,
                title=step.title,
                text_content=step.text_content,
                image_url=step.image_url,
                video_url=step.video_url,
                course_id=step.course_id,
                is_end=step.is_end,
            ),
        }
    return {
        "message": "User has already started the course",
        "user_progress": UserProgressResponse(
            user_id=user_progress.user_id,
            course_id=user_progress.course_id,
            current_step_id=user_progress.current_step_id,
        ),
    }


@router.get("/progress/{course_id}", response_model=UserProgressResponse)
async def get_user_progress(
    course_id: int,
    session: sessionDep,
    user: User = Depends(get_current_user),
):
    user_progress = await session.get(
        UserCourseProgress, {"user_id": user.id, "course_id": course_id}
    )
    if not user_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no progress in this course",
        )
    return user_progress


@router.get("/{course_id}/back", response_model=StepResponse)
async def back_step_course(
    course_id: int,
    session: sessionDep,
    user: User = Depends(get_current_user),
):
    user_progress = await session.scalar(
        select(UserCourseProgress).
        options(joinedload(UserCourseProgress.current_step)).
        filter_by(user_id = user.id,course_id = course_id),    
    )
    
    if not user_progress or not user_progress.current_step:
        raise HTTPException(404, "User progress or step not found")
    back_step_order = user_progress.current_step.order - 1
    if back_step_order == 0:
        back_step_order = 1
    back_step = await session.scalar(
        select(Step)
        .where(Step.course_id == course_id, 
               Step.is_active == True, 
               Step.order == back_step_order))
    if not back_step:
        raise HTTPException(
            status_code=404,
            detail=f"Step with order: {back_step_order}, not found"
        )
    user_progress.current_step_id = back_step.id
    await session.commit()
    return back_step

@router.get("/{course_id}/next", response_model=StepResponse)
async def next_step_course(
    course_id: int,
    session: sessionDep,
    user: User = Depends(get_current_user),
):
    user_progress = await session.scalar(
        select(UserCourseProgress).
        options(joinedload(UserCourseProgress.current_step)).
        filter_by(user_id = user.id,course_id = course_id),    
    )
    
    if not user_progress or not user_progress.current_step:
        raise HTTPException(404, "User progress or step not found")
    next_step_order = user_progress.current_step.order + 1
    next_step = await session.scalar(
        select(Step)
        .where(Step.course_id == course_id, 
               Step.is_active == True, 
               Step.order == next_step_order))
    if not next_step:
        raise HTTPException(
            status_code=404,
            detail=f"Step with order: {next_step_order}, not found"
        )
    user_progress.current_step_id = next_step.id
    await session.commit()
    return next_step



@router.delete("/reset/{course_id}")
async def restart_course(
    course_id: int,
    session: sessionDep, 
    user: User=Depends(get_current_user), 
):
    user_progress = await session.scalar(select(UserCourseProgress).filter_by(user_id=user.id, course_id=course_id))
    if not user_progress:
        raise HTTPException(404, "No user progress in this course")
    await session.delete(user_progress)
    await session.commit()
    return {"message": "Progress successfully deleted",
            "deleted_progress": UserProgressResponse(
                user_id=user.id,
                course_id=course_id,
                current_step_id=user_progress.current_step_id
            )}
