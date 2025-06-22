from fastapi import FastAPI
from api.short import router_short
from api.user import router_user
app = FastAPI(title="短链实战项目")
app.include_router(router_short)
app.include_router(router_user)

@app.on_event("startup")
async def startup():
    from db.database import Base, async_engine
    from models.model import ShortUrl, User
    async def init_create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    await init_create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    pass
