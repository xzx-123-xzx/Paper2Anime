import json
from typing import Dict, Any, Optional

from common.logger import my_logger as logger

class ProgressTracker:
    """进度追踪器 - 用于更新项目状态并推送 WebSocket"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._ws_manager = None
    
    def set_ws_manager(self, ws_manager):
        """设置 WebSocket 管理器"""
        self._ws_manager = ws_manager
    
    async def update_progress(self, project_id: str, node: str, progress: float, status: str, extra: Dict[str, Any] = None):
        """更新进度"""
        data = {
            "type": "progress",
            "project_id": project_id,
            "node": node,
            "progress": progress,
            "status": status,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        if extra:
            data.update(extra)
        
        # 保存到 Redis
        if self.redis:
            try:
                self.redis.hset(f"progress:{project_id}", node, json.dumps(data))
                self.redis.set(f"progress:{project_id}:total", progress)
            except Exception as e:
                logger.warning(f"Redis 保存进度失败: {e}")
        
        # 推送 WebSocket
        if self._ws_manager:
            await self._ws_manager.send_to_project(project_id, data)
        
        logger.info(f"进度更新: {project_id} - {node} - {progress}%")
    
    async def update_status(self, project_id: str, status: str, error_message: str = None):
        """更新状态"""
        data = {
            "type": "status",
            "project_id": project_id,
            "status": status,
            "error_message": error_message,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        if self._ws_manager:
            await self._ws_manager.send_to_project(project_id, data)
    
    async def notify_complete(self, project_id: str, final_video_url: str = None, thumbnail_url: str = None):
        """通知完成"""
        data = {
            "type": "complete",
            "project_id": project_id,
            "status": "completed",
            "final_video_url": final_video_url,
            "thumbnail_url": thumbnail_url,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        if self._ws_manager:
            await self._ws_manager.send_to_project(project_id, data)
    
    async def notify_error(self, project_id: str, error_message: str):
        """通知错误"""
        data = {
            "type": "error",
            "project_id": project_id,
            "status": "failed",
            "error_message": error_message,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        if self._ws_manager:
            await self._ws_manager.send_to_project(project_id, data)
    
    def get_progress(self, project_id: str) -> Optional[Dict]:
        """获取进度"""
        if not self.redis:
            return None
        
        try:
            total = self.redis.get(f"progress:{project_id}:total") or 0
            nodes = self.redis.hgetall(f"progress:{project_id}")
            return {
                "total": float(total),
                "nodes": {k: json.loads(v) for k, v in nodes.items()}
            }
        except Exception as e:
            logger.warning(f"获取进度失败: {e}")
            return None

# 全局进度追踪器
progress_tracker = ProgressTracker()