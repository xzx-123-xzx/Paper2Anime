from fastapi import APIRouter
from .routes import document, project, task, webhook, settings
from .websocket import router as websocket_router

api_router = APIRouter()
api_router.include_router(document.router, prefix="/documents", tags=["文档"])
api_router.include_router(project.router, prefix="/projects", tags=["项目"])
api_router.include_router(task.router, prefix="/tasks", tags=["任务"])
api_router.include_router(settings.router, prefix="/settings", tags=["设置"])
api_router.include_router(webhook.router, prefix="/webhooks", tags=["回调"])

ws_router = APIRouter()
ws_router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])