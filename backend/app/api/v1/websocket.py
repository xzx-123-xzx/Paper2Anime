import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from common.logger import my_logger as logger

router = APIRouter()

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """连接"""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info(f"WebSocket 连接: project_id={project_id}")
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """断开连接"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket 断开: project_id={project_id}")
    
    async def send_to_project(self, project_id: str, data: dict):
        """向项目发送消息"""
        if project_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.warning(f"发送消息失败: {e}")
                    disconnected.add(connection)
            
            for conn in disconnected:
                self.active_connections[project_id].discard(conn)

manager = ConnectionManager()

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket 端点"""
    await manager.connect(websocket, project_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"收到 WebSocket 消息: {data}")
            
            # 可以处理客户端发送的心跳消息
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect(websocket, project_id)