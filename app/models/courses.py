from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.backend.db import Base
from app.models import *
from typing import Optional


class Course(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), unique=True)
    description: Mapped[str] = mapped_column(String(150), nullable=True)
    progress: Mapped[list['UserCourseProgress']] = relationship(
    "UserCourseProgress", back_populates="course"
    )
    steps: Mapped[list["Step"]] = relationship(back_populates="course")
    is_active: Mapped[bool] = mapped_column(default=True)


