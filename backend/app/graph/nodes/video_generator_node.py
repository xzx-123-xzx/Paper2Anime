import os
from pathlib import Path
from typing import Dict, Any, List
from common.logger import my_logger as logger
from ...services.video_service import VideoGenerationService

video_service = VideoGenerationService()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def video_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行视频生成节点")
    
    storyboard = state.get("storyboard", [])
    character_images = state.get("character_images", {})
    project_id = state.get("project_id", "unknown")
    
    if not storyboard:
        logger.warning("没有分镜可生成视频")
        state["error_message"] = "缺少分镜"
        return state
    
    # 创建项目专用的视频存储目录
    project_videos_dir = PROJECT_ROOT / "storage" / "videos" / project_id
    project_videos_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        generated_videos = []
        total_scenes = len(storyboard)
        
        for i, scene in enumerate(storyboard):
            scene_id = scene.get("scene_id", f"scene_{i}")
            video_prompt = scene.get("video_prompt", scene.get("description", ""))
            characters_in_scene = scene.get("characters", [])
            
            logger.info(f"生成镜头 {i+1}/{total_scenes}: {scene_id}")
            
            scene_char_images = {}
            for char_name in characters_in_scene:
                for char_id, images in character_images.items():
                    if char_name.lower() in str(char_id).lower():
                        scene_char_images[char_name] = images
                        break
            
            try:
                result = video_service.generate_sync(
                    prompt=video_prompt,
                    scene_id=scene_id,
                    reference_images=scene_char_images,
                    duration=scene.get("duration", 5.0)
                )
                video_url = result.get("url", "")
                video_path = result.get("path", "")
                
                # 如果有 URL 但没有本地路径，记录 URL
                generated_videos.append({
                    "scene_id": scene_id,
                    "video_url": video_url,
                    "video_path": video_path,
                    "duration": scene.get("duration", 5.0),
                    "status": result.get("status", "unknown")
                })
                
                if video_path:
                    logger.info(f"视频已保存: {video_path}")
                    
            except Exception as e:
                logger.warning(f"生成视频片段 {scene_id} 失败: {type(e).__name__}: {e}")
                generated_videos.append({
                    "scene_id": scene_id,
                    "video_url": "",
                    "video_path": "",
                    "duration": scene.get("duration", 5.0),
                    "error": str(e)
                })
        
        state["generated_videos"] = generated_videos
        state["node_statuses"]["video_generator"] = "completed"
        state["progress"] = 85.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"视频片段生成完成，共 {len(generated_videos)} 个，保存目录: {project_videos_dir}")
    except Exception as e:
        logger.error(f"视频生成失败: {type(e).__name__}: {e}")
        state["node_statuses"]["video_generator"] = "failed"
        state["error_message"] = str(e)
    
    return state
