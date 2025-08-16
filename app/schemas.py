from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class CreateCourse(BaseModel):
    title: str = Field(max_length=32)
    description: str | None = Field(max_length=150) 


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)




class CreateStep(BaseModel):
    title: str = Field(..., max_length=32)
    text_content: Optional[str] = Field(None)
    image_url: Optional[str] = Field(None)
    video_url: Optional[str] = Field(None)
    is_end: Optional[bool] = Field(default=False)

class StepResponse(BaseModel):
    id: int
    title: str
    text_content: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    course_id: int
    is_end: bool

    model_config = ConfigDict(from_attributes=True)

class StepListItem(BaseModel):
    title: str
    step_image: Optional[str] = None
    text_content: Optional[str] = None  
    video_url: Optional[str] = None
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class StepListResponse(BaseModel):
    status_code: int
    course_id: int
    steps: List[StepListItem]

class UserCreateScheme(BaseModel):
    first_name: str = Field(max_length=32)
    last_name:  str = Field(max_length=32)
    username: str = Field(max_length=32)
    password: str = Field(max_length=32)

class UserLoginScheme(BaseModel):
    username: str = Field(max_length=32)
    password: str = Field(max_length=32)

class UserResponse(BaseModel):
    id: int
    first_name: str 
    last_name:  str 
    username: str 
    model_config = ConfigDict(
        from_attributes=True
    )

class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"