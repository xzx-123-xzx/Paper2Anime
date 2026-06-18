from fastapi import APIRouter, Request
from common.logger import my_logger as logger

router = APIRouter()

@router.post("/minimax")
async def minimax_webhook(request: Request):
    """MinMax 回调"""
    body = await request.json()
    logger.info(f"收到 MinMax 回调: {body}")
    return {"status": "received"}
