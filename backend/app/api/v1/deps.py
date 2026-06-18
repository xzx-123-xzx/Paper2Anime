from fastapi import Header, HTTPException, Depends
from typing import Optional
from common.logger import my_logger as logger
from ...core.security import verify_token


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        return "default_user"
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = verify_token(token)
        if payload:
            return payload.get("sub", "default_user")
    return "default_user"
