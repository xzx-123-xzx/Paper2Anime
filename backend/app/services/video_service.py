import os
import uuid
import httpx
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from common.logger import my_logger as logger

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VIDEOS_STORAGE_PATH = PROJECT_ROOT / "storage" / "videos"


class VideoGenerationService:
    def __init__(self):
        self.api_key = os.getenv("MINMAX_VIDEO_API_KEY", "")
        self.api_url = os.getenv("MINMAX_VIDEO_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis")
        self.model = os.getenv("MINMAX_VIDEO_MODEL", "wan2.7-t2v")
        self.task_query_url = "https://dashscope.aliyuncs.com/api/v1/tasks"
        VIDEOS_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    
    async def generate(
        self,
        prompt: str,
        scene_id: str = "",
        reference_images: Optional[Dict[str, Any]] = None,
        duration: float = 5.0,
        save_local: bool = True
    ) -> Dict[str, Any]:
        logger.info(f"生成视频: scene_id={scene_id}, duration={duration}s, 模型: {self.model}")
        
        if not self.api_key:
            raise ValueError("未配置百炼视频 API Key，请在 .env 文件中设置 MINMAX_VIDEO_API_KEY")
        
        # 百炼视频 API 只支持特定时长，强制调整为支持的值
        # wan2.7-t2v 支持 5-60 秒
        actual_duration = max(5, min(60, int(duration)))
        if actual_duration != int(duration):
            logger.info(f"视频时长调整为: {actual_duration}s (原时长: {duration}s)")
        
        try:
            # 步骤1: 创建异步任务
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-DashScope-Async": "enable"
                    },
                    json={
                        "model": self.model,
                        "input": {
                            "prompt": prompt
                        },
                        "parameters": {
                            "resolution": "720P",
                            "ratio": "16:9",
                            "duration": actual_duration,
                            "prompt_extend": True,
                            "watermark": False
                        }
                    }
                )
                
                logger.info(f"创建视频任务响应状态码: {response.status_code}")
                logger.info(f"创建视频任务响应内容: {response.text[:500]}")
                
                if response.status_code != 200:
                    raise RuntimeError(f"百炼视频 API 创建任务失败 HTTP {response.status_code}: {response.text[:500]}")
                
                result = response.json()
                task_id = result.get("output", {}).get("task_id", "")
                
                if not task_id:
                    raise ValueError(f"百炼视频 API 返回成功但没有 task_id。完整响应: {response.text[:1000]}")
                
                logger.info(f"视频任务创建成功，task_id: {task_id}")
            
            # 步骤2: 轮询等待任务完成 (视频生成通常需要 1-5 分钟)
            video_url = await self._wait_for_task_completion(task_id, max_wait=600)
            
            if not video_url:
                raise ValueError("视频任务完成但没有获取到视频 URL")
            
            # 步骤3: 下载并保存视频到本地
            local_path = ""
            if save_local and video_url:
                local_path = await self._download_and_save_video(video_url, scene_id)
            
            return {
                "url": video_url,
                "path": local_path,
                "status": "success"
            }
                    
        except httpx.HTTPError as e:
            logger.error(f"视频生成 HTTP 错误: {type(e).__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"视频生成异常: {type(e).__name__}: {e}")
            raise
    
    async def _wait_for_task_completion(self, task_id: str, max_wait: int = 600) -> str:
        """轮询等待任务完成，返回视频 URL"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(max_wait // 15):
                await asyncio.sleep(15)
                
                response = await client.get(
                    f"{self.task_query_url}/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"查询视频任务失败 HTTP {response.status_code}")
                    continue
                
                result = response.json()
                task_status = result.get("output", {}).get("task_status", "")
                
                logger.info(f"视频任务状态: {task_status} (轮询第 {i+1} 次)")
                
                if task_status == "SUCCEEDED":
                    video_url = result.get("output", {}).get("video_url", "")
                    if video_url:
                        logger.info(f"视频生成成功: {video_url[:100]}...")
                        return video_url
                    raise ValueError(f"视频任务成功但无法解析视频 URL。响应: {response.text[:500]}")
                
                elif task_status == "FAILED":
                    error_msg = result.get("output", {}).get("message", "未知错误")
                    raise RuntimeError(f"视频生成任务失败: {error_msg}")
                
                elif task_status in ["PENDING", "RUNNING"]:
                    continue
                
                else:
                    logger.warning(f"未知视频任务状态: {task_status}")
        
        raise RuntimeError(f"视频任务超时，等待了 {max_wait} 秒仍未完成")
    
    async def _download_and_save_video(self, url: str, scene_id: str) -> str:
        """下载并保存视频到本地 storage"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    filename = f"{scene_id or 'scene'}_{uuid.uuid4().hex[:8]}.mp4"
                    filepath = VIDEOS_STORAGE_PATH / filename
                    filepath.write_bytes(response.content)
                    logger.info(f"视频已保存到: {filepath}")
                    return str(filepath)
                else:
                    raise RuntimeError(f"下载视频失败 HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            raise
    
    def generate_sync(
        self,
        prompt: str,
        scene_id: str = "",
        reference_images: Optional[Dict[str, Any]] = None,
        duration: float = 5.0,
        save_local: bool = True
    ) -> Dict[str, Any]:
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.generate(prompt, scene_id, reference_images, duration, save_local)
                )
                return future.result()
        except RuntimeError:
            return asyncio.run(self.generate(prompt, scene_id, reference_images, duration, save_local))
        except Exception as e:
            logger.error(f"generate_sync 异常: {type(e).__name__}: {e}")
            raise
