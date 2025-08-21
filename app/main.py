from fastapi import FastAPI
from app.routers.course import router as course 
from app.routers.steps import router as steps 
from app.routers.users import router as users
from app.routers.admin import router as admin
from app.routers.auth_header import router as auth
from app.routers.auth_cookie import router as auth_cookie
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(course)
app.include_router(steps)
app.include_router(admin)
users.include_router(auth_cookie)
app.include_router(users)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)



