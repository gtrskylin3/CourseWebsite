from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.backend.db import Base
from app.models import *
from typing import Optional


class Step(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32), unique=True)
    text_content: Mapped[str] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    video_url: Mapped[str] = mapped_column(nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    course: Mapped['Course'] = relationship(back_populates="steps")
    order: Mapped[int] = mapped_column(default=1)  # номер шага внутри курса

    is_active: Mapped[bool] = mapped_column(default=True)
    is_end: Mapped[bool] = mapped_column(default=False)
    
