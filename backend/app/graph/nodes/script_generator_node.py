import os
import json
from pathlib import Path
from typing import Dict, Any
from common.logger import my_logger as logger
from common.llm import my_llm

SCRIPT_GENERATION_PROMPT = """你是一个专业的剧本创作AI。请根据以下文档内容，创作一个适合制作动画视频的剧本。

要求：
1. 采用经典的三幕式结构（建置、对抗、解决）
2. 角色对话生动，符合角色性格
3. 适当加入场景描述和动作指导
4. 控制总时长在2-5分钟左右

文档内容：
{content}

请生成剧本："""

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def script_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行剧本生成节点")
    
    raw_document = state.get("raw_document", "")
    project_id = state.get("project_id", "unknown")
    
    if not raw_document:
        logger.warning("没有文档内容可生成剧本")
        state["error_message"] = "缺少文档内容"
        return state
    
    # 创建项目专用的存储目录
    project_dir = PROJECT_ROOT / "storage" / "scripts" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        prompt = SCRIPT_GENERATION_PROMPT.format(content=raw_document[:8000])
        response = my_llm.invoke(prompt)
        script = response.content if hasattr(response, 'content') else str(response)
        
        # 保存剧本到文件
        script_path = project_dir / "script.txt"
        script_path.write_text(script, encoding='utf-8')
        
        state["script"] = script
        state["script_path"] = str(script_path)
        state["script_version"] = state.get("script_version", 0) + 1
        state["node_statuses"]["script_generator"] = "completed"
        state["progress"] = 15.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"剧本生成完成，已保存到: {script_path}")
    except Exception as e:
        logger.error(f"剧本生成失败: {type(e).__name__}: {e}")
        state["node_statuses"]["script_generator"] = "failed"
        state["error_message"] = str(e)
    
    return state
