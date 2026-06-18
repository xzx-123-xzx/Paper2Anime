from typing import Dict, Any, List
import uuid
from common.logger import my_logger as logger
from common.llm import my_llm

CHARACTER_EXTRACTION_PROMPT = """你是一个角色设计AI。请从以下分镜脚本中提取所有出现的角色，并生成每个角色的详细外观描述。

分镜内容：
{storyboard}

请为每个角色生成：
- name: 角色名称
- role: 角色定位（protagonist/antagonist/supporting/minor）
- description: 角色简介
- appearance: 外观特征（年龄、性别、身高、体型、发型、发色、眼睛、服装等）

输出格式（JSON数组）：
[{{
  "character_id": "char_001",
  "name": "角色名",
  "role": "protagonist",
  "description": "角色简介",
  "appearance": {{
    "age_estimate": "25-30岁",
    "gender": "男",
    "height": "175cm",
    "build": "中等",
    "hair_style": "短发",
    "hair_color": "黑色",
    "eye_color": "棕色",
    "skin_tone": "健康",
    "clothing_style": "休闲西装",
    "distinguishing_features": ["特征1", "特征2"]
  }}
}}]"""

def character_designer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行角色设计节点")
    
    storyboard = state.get("storyboard", [])
    
    if not storyboard:
        logger.warning("没有分镜可提取角色")
        state["error_message"] = "缺少分镜"
        return state
    
    try:
        import json
        import re
        
        storyboard_text = "\n".join([
            f"镜头{i+1}: {s.get('description', '')} 角色: {', '.join(s.get('characters', []))}"
            for i, s in enumerate(storyboard[:20])
        ])
        
        prompt = CHARACTER_EXTRACTION_PROMPT.format(storyboard=storyboard_text)
        response = my_llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            characters = json.loads(json_match.group())
        else:
            characters = []
        
        for char in characters:
            if "character_id" not in char:
                char["character_id"] = f"char_{uuid.uuid4().hex[:8]}"
        
        state["characters"] = characters
        state["node_statuses"]["character_designer"] = "completed"
        state["progress"] = 40.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"角色设计完成，共 {len(characters)} 个角色")
    except Exception as e:
        logger.error(f"角色设计失败: {e}")
        state["node_statuses"]["character_designer"] = "failed"
        state["error_message"] = str(e)
    
    return state
