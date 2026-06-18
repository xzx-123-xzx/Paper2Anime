from celery import Task
from common.logger import my_logger as logger
from .celery_app import celery_app
from ..graph.workflow import run_workflow_sync

@celery_app.task(bind=True, name="tasks.run_workflow")
def run_workflow_task(self: Task, project_id: str, user_id: str, document_id: str, document_path: str, settings: dict = None) -> dict:
    logger.info(f"开始执行工作流: project_id={project_id}")
    
    try:
        result = run_workflow_sync(
            project_id=project_id,
            user_id=user_id,
            document_id=document_id,
            document_path=document_path,
            settings=settings or {}
        )
        
        return {
            "status": "completed",
            "project_id": project_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        return {
            "status": "failed",
            "project_id": project_id,
            "error": str(e)
        }

@celery_app.task(bind=True, name="tasks.generate_images")
def generate_images_task(self: Task, project_id: str, characters: list, storyboard: list = None) -> dict:
    logger.info(f"开始生成角色图片: project_id={project_id}")
    
    from backend.app.services.image_service import ImageGenerationService
    image_service = ImageGenerationService()
    
    results = {}
    for char in characters:
        char_id = char.get("character_id", "unknown")
        name = char.get("name", "character")
        appearance = char.get("appearance", {})
        
        prompts = {
            "front": f"{name}, front view, full body, {appearance.get('clothing_style', 'casual')}",
            "side": f"{name}, side view, full body, walking pose",
            "back": f"{name}, back view, full body",
            "expression": f"{name}, close-up face, detailed expression"
        }
        
        char_images = {}
        for view_type, prompt in prompts.items():
            try:
                result = image_service.generate_sync(prompt, name)
                char_images[view_type] = result.get("url", "")
            except Exception as e:
                logger.warning(f"生成 {name}.{view_type} 失败: {e}")
                char_images[view_type] = ""
        
        results[char_id] = char_images
    
    return {
        "status": "completed",
        "project_id": project_id,
        "character_images": results
    }

@celery_app.task(bind=True, name="tasks.generate_videos")
def generate_videos_task(self: Task, project_id: str, storyboard: list, character_images: dict = None) -> dict:
    logger.info(f"开始生成视频片段: project_id={project_id}")
    
    from ..services.video_service import VideoGenerationService
    video_service = VideoGenerationService()
    
    results = []
    for i, scene in enumerate(storyboard):
        scene_id = scene.get("scene_id", f"scene_{i}")
        video_prompt = scene.get("video_prompt", scene.get("description", ""))
        
        try:
            result = video_service.generate_sync(
                prompt=video_prompt,
                scene_id=scene_id,
                reference_images=character_images,
                duration=scene.get("duration", 5.0)
            )
            results.append({
                "scene_id": scene_id,
                "video_url": result.get("url", ""),
                "video_path": result.get("path", ""),
                "duration": scene.get("duration", 5.0),
                "status": "success"
            })
        except Exception as e:
            logger.warning(f"生成视频 {scene_id} 失败: {e}")
            results.append({
                "scene_id": scene_id,
                "video_url": "",
                "video_path": "",
                "duration": scene.get("duration", 5.0),
                "status": "error",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "project_id": project_id,
        "videos": results
    }
