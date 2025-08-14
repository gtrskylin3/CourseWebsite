from fastapi import FastAPI
from app.routers.course import router as course 
from app.routers.steps import router as steps 
import uvicorn

app = FastAPI()
app.include_router(course)
app.include_router(steps)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)