import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from common.logger import my_logger as logger

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "user_settings.json"
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULTS = {
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com",
    "minmax_api_key": "",
    "mysql_host": "localhost",
    "mysql_port": 3306,
    "mysql_user": "root",
    "mysql_password": "",
    "mysql_database": "paper2anime",
    "storage_type": "local",
    "local_storage_path": "./storage",
}

class SettingsUpdate(BaseModel):
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: Optional[str] = None
    minmax_api_key: Optional[str] = None
    mysql_host: Optional[str] = None
    mysql_port: Optional[int] = None
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_database: Optional[str] = None
    storage_type: Optional[str] = None
    local_storage_path: Optional[str] = None

class SettingsResponse(BaseModel):
    deepseek_api_key: str
    deepseek_base_url: str
    minmax_api_key: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    storage_type: str
    local_storage_path: str

router = APIRouter()

def _load_settings() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"读取用户设置失败: {e}")
    return dict(DEFAULTS)

def _save_settings(data: Dict[str, Any]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get("/", response_model=SettingsResponse)
async def get_settings():
    settings = _load_settings()
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in settings.items() if k in DEFAULTS and v is not None})
    return merged

@router.put("/", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    current = _load_settings()
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in current.items() if k in DEFAULTS and v is not None})

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in DEFAULTS:
            merged[key] = value

    try:
        _save_settings(merged)
        logger.info("用户设置已保存")
    except Exception as e:
        logger.error(f"保存设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存设置失败: {e}")

    return merged
