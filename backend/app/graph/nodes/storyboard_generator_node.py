import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List
from common.logger import my_logger as logger
from common.llm import my_llm

STORYBOARD_GENERATION_PROMPT = """你是一个专业的分镜头脚本创作AI。请根据以下剧本，生成分镜头脚本。

要求：
1. 每个镜头控制在3-8秒
2. 包含：场景描述、角色动作、对话（如果有）、镜头时长
3. 生成适合AI视频生成的画面描述（image_prompt）和视频描述（video_prompt）
4. 指定镜头类型和运镜方式

剧本内容：
{script}

请生成分镜头脚本（JSON数组格式）：
[{{
  "scene_id": "scene_001",
  "sequence": 1,
  "description": "场景描述",
  "characters": ["角色名"],
  "dialogue": "对话内容",
  "camera_movement": "固定/推进/拉出等",
  "shot_type": "中景/近景等",
  "duration": 5.0,
  "image_prompt": "文生图提示词",
  "video_prompt": "文生视频提示词"
}}]"""

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def storyboard_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行分镜生成节点")
    
    script = state.get("script", "")
    project_id = state.get("project_id", "unknown")
    
    if not script:
        logger.warning("没有剧本可生成分镜")
        state["error_message"] = "缺少剧本"
        return state
    
    # 创建项目专用的存储目录
    project_dir = PROJECT_ROOT / "storage" / "storyboards" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        prompt = STORYBOARD_GENERATION_PROMPT.format(script=script[:6000])
        response = my_llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        import re
        
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            storyboard = json.loads(json_match.group())
        else:
            storyboard = []
        
        for scene in storyboard:
            if "scene_id" not in scene:
                scene["scene_id"] = f"scene_{uuid.uuid4().hex[:8]}"
        
        # 保存分镜到 JSON 文件
        storyboard_path = project_dir / "storyboard.json"
        storyboard_path.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding='utf-8')
        
        state["storyboard"] = storyboard
        state["storyboard_path"] = str(storyboard_path)
        state["storyboard_version"] = state.get("storyboard_version", 0) + 1
        state["node_statuses"]["storyboard_generator"] = "completed"
        state["progress"] = 30.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"分镜生成完成，共 {len(storyboard)} 个镜头，已保存到: {storyboard_path}")
    except Exception as e:
        logger.error(f"分镜生成失败: {type(e).__name__}: {e}")
        state["node_statuses"]["storyboard_generator"] = "failed"
        state["error_message"] = str(e)
    
    return state
