from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.backend.db import Base
from typing import TYPE_CHECKING, Optional
from app.models import *



class UserCourseProgress(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    current_step_id: Mapped[int] = mapped_column(ForeignKey("steps.id"), nullable=True)
    is_completed: Mapped[bool] = mapped_column(server_default="false")

    user: Mapped["User"] = relationship("User", back_populates="progress")
    course: Mapped["Course"] = relationship("Course", back_populates="progress")
    current_step: Mapped["Step"] = relationship("Step")