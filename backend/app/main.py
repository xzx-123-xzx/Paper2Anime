from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from common.logger import my_logger as logger

from backend.app.core.config import settings
from backend.app.api.v1 import api_router, ws_router
from backend.app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("数据库初始化完成")
    yield
    logger.info("服务关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="文档转动画短视频一站式平台",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")


@app.get("/")
async def root():
    return {"message": "Paper2Anime API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
