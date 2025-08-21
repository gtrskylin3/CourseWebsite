from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.backend.db import Base
from app.models import *
from typing import Optional

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32), unique=False)
    last_name: Mapped[str] = mapped_column(String(32), unique=False)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    progress: Mapped[list['UserCourseProgress']] = relationship(
        "UserCourseProgress", back_populates="user"
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default="false")

