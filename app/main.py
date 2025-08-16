from fastapi import FastAPI
from app.routers.course import router as course 
from app.routers.steps import router as steps 
from app.routers.users import router as users
from app.routers.auth import router as auth
import uvicorn

app = FastAPI()
app.include_router(course)
app.include_router(steps)
users.include_router(auth)
app.include_router(users)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)



