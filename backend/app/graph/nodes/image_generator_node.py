import os
from pathlib import Path
from typing import Dict, Any, List
from common.logger import my_logger as logger
from ...services.image_service import ImageGenerationService

image_service = ImageGenerationService()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def image_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行图片生成节点")
    
    characters = state.get("characters", [])
    project_id = state.get("project_id", "unknown")
    
    if not characters:
        logger.warning("没有角色可生成图片")
        state["error_message"] = "缺少角色"
        return state
    
    # 创建项目专用的图片存储目录
    project_images_dir = PROJECT_ROOT / "storage" / "images" / project_id
    project_images_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        character_images = {}
        character_paths = {}
        
        for char in characters:
            char_id = char.get("character_id", "unknown")
            char_name = char.get("name", "character")
            logger.info(f"为角色 {char_name} 生成四视图")
            
            appearance_desc = char.get("appearance", {})
            name = char.get("name", "character")
            
            prompts = {
                "front": f"{name}, front view, full body, {appearance_desc.get('clothing_style', 'casual clothing')}, neutral expression, standing pose",
                "side": f"{name}, side view, full body, {appearance_desc.get('clothing_style', 'casual clothing')}, walking pose",
                "back": f"{name}, back view, full body, {appearance_desc.get('clothing_style', 'casual clothing')}",
                "expression": f"{name}, close-up face, detailed facial expression, {appearance_desc.get('eye_color', 'brown')} eyes"
            }
            
            image_urls = {}
            image_local_paths = {}
            
            for view_type, prompt in prompts.items():
                try:
                    result = image_service.generate_sync(prompt, character_name=name)
                    image_url = result.get("url", "")
                    image_path = result.get("path", "")
                    
                    # 如果生成了图片但没有本地路径，手动保存
                    if image_url and not image_path:
                        import uuid
                        filename = f"{char_name}_{view_type}_{uuid.uuid4().hex[:8]}.png"
                        image_path = str(project_images_dir / filename)
                    
                    image_urls[view_type] = image_url
                    image_local_paths[view_type] = image_path
                    
                    if image_path and os.path.exists(image_path):
                        logger.info(f"{view_type} 视图已保存: {image_path}")
                    elif image_path:
                        logger.warning(f"{view_type} 视图路径不存在: {image_path}")
                        
                except Exception as e:
                    logger.warning(f"生成 {view_type} 视图失败: {type(e).__name__}: {e}")
                    image_urls[view_type] = ""
                    image_local_paths[view_type] = ""
            
            character_images[char_id] = image_urls
            character_paths[char_id] = image_local_paths
        
        state["character_images"] = character_images
        state["character_image_paths"] = character_paths  # 保存本地路径
        state["node_statuses"]["image_generator"] = "completed"
        state["progress"] = 60.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"角色四视图生成完成，共 {len(character_images)} 个角色，保存目录: {project_images_dir}")
    except Exception as e:
        logger.error(f"图片生成失败: {type(e).__name__}: {e}")
        state["node_statuses"]["image_generator"] = "failed"
        state["error_message"] = str(e)
    
    return state
