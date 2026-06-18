import os
import uuid
import httpx
import asyncio
from typing import Dict, Any
from pathlib import Path
from common.logger import my_logger as logger

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
IMAGES_STORAGE_PATH = PROJECT_ROOT / "storage" / "images"


class ImageGenerationService:
    def __init__(self):
        self.api_key = os.getenv("MINMAX_IMAGE_API_KEY", "")
        self.api_url = os.getenv("MINMAX_IMAGE_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation")
        self.model = os.getenv("MINMAX_IMAGE_MODEL", "wan2.7-image-pro")
        self.task_query_url = "https://dashscope.aliyuncs.com/api/v1/tasks"
        IMAGES_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    
    async def generate(self, prompt: str, character_name: str = "", save_local: bool = True) -> Dict[str, Any]:
        logger.info(f"生成图片: {character_name or 'scene'}, 模型: {self.model}")
        
        if not self.api_key:
            raise ValueError("未配置百炼图片 API Key，请在 .env 文件中设置 MINMAX_IMAGE_API_KEY")
        
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
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "text": prompt
                                        }
                                    ]
                                }
                            ]
                        },
                        "parameters": {
                            "size": "1024*1024",
                            "n": 1
                        }
                    }
                )
                
                logger.info(f"创建任务响应状态码: {response.status_code}")
                logger.info(f"创建任务响应内容: {response.text[:500]}")
                
                if response.status_code != 200:
                    raise RuntimeError(f"百炼图片 API 创建任务失败 HTTP {response.status_code}: {response.text[:500]}")
                
                result = response.json()
                task_id = result.get("output", {}).get("task_id", "")
                
                if not task_id:
                    raise ValueError(f"百炼 API 返回成功但没有 task_id。完整响应: {response.text[:1000]}")
                
                logger.info(f"任务创建成功，task_id: {task_id}")
            
            # 步骤2: 轮询等待任务完成
            image_url = await self._wait_for_task_completion(task_id)
            
            if not image_url:
                raise ValueError("任务完成但没有获取到图片 URL")
            
            # 步骤3: 下载并保存图片到本地
            local_path = ""
            if save_local and image_url:
                local_path = await self._download_and_save_image(image_url, character_name)
            
            return {
                "url": image_url,
                "path": local_path,
                "status": "success"
            }
                    
        except httpx.HTTPError as e:
            logger.error(f"图片生成 HTTP 错误: {type(e).__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"图片生成异常: {type(e).__name__}: {e}")
            raise
    
    async def _wait_for_task_completion(self, task_id: str, max_wait: int = 300) -> str:
        """轮询等待任务完成，返回图片 URL"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(max_wait // 5):
                await asyncio.sleep(5)
                
                response = await client.get(
                    f"{self.task_query_url}/{task_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"查询任务失败 HTTP {response.status_code}")
                    continue
                
                result = response.json()
                task_status = result.get("output", {}).get("task_status", "")
                
                logger.info(f"任务状态: {task_status} (轮询第 {i+1} 次)")
                
                if task_status == "SUCCEEDED":
                    # 获取图片 URL
                    choices = result.get("output", {}).get("choices", [])
                    if choices and len(choices) > 0:
                        content = choices[0].get("message", {}).get("content", [])
                        if content and len(content) > 0:
                            image_url = content[0].get("image", "")
                            if image_url:
                                logger.info(f"图片生成成功: {image_url[:100]}...")
                                return image_url
                    raise ValueError(f"任务成功但无法解析图片 URL。响应: {response.text[:500]}")
                
                elif task_status == "FAILED":
                    error_msg = result.get("output", {}).get("message", "未知错误")
                    raise RuntimeError(f"图片生成任务失败: {error_msg}")
                
                elif task_status in ["PENDING", "RUNNING"]:
                    continue
                
                else:
                    logger.warning(f"未知任务状态: {task_status}")
        
        raise RuntimeError(f"任务超时，等待了 {max_wait} 秒仍未完成")
    
    async def _download_and_save_image(self, url: str, character_name: str) -> str:
        """下载并保存图片到本地 storage"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    filename = f"{character_name or 'image'}_{uuid.uuid4().hex[:8]}.png"
                    filepath = IMAGES_STORAGE_PATH / filename
                    filepath.write_bytes(response.content)
                    logger.info(f"图片已保存到: {filepath}")
                    return str(filepath)
                else:
                    raise RuntimeError(f"下载图片失败 HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            raise
    
    def generate_sync(self, prompt: str, character_name: str = "", save_local: bool = True) -> Dict[str, Any]:
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.generate(prompt, character_name, save_local)
                )
                return future.result()
        except RuntimeError:
            return asyncio.run(self.generate(prompt, character_name, save_local))
        except Exception as e:
            logger.error(f"generate_sync 异常: {type(e).__name__}: {e}")
            raise
