from app.backend.db import session_maker

async def get_db():
    async with session_maker() as session:
        yield session



