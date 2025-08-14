from fastapi import FastAPI


app = FastAPI()


@app.get("/all_courses")
async def all_courses():
    pass

@app.get("/{course_id}")
async def get_course_info(course_id):
    pass

@app.get("/{course_id}/{step_course}")
async def get_course_step(course_id, step_course):
    pass
