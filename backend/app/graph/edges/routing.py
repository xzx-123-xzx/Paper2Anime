from typing import Dict, Any, Literal
from backend.app.graph.state import TaskStatus

def should_continue(state: Dict[str, Any]) -> Literal["next_node", "fail_and_notify", "retry_current_node"]:
    status = state.get("status")
    error_message = state.get("error_message")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    
    if error_message and retry_count >= max_retries:
        return "fail_and_notify"
    
    if status == TaskStatus.FAILED:
        return "fail_and_notify"
    
    return "next_node"

def routing_decision(state: Dict[str, Any]) -> str:
    node_order = [
        "document_parser",
        "script_generator",
        "storyboard_generator",
        "character_designer",
        "image_generator",
        "video_generator",
        "video_editor",
        "quality_check"
    ]
    
    current_node = state.get("current_node", "document_parser")
    
    try:
        current_index = node_order.index(current_node)
        if current_index < len(node_order) - 1:
            return node_order[current_index + 1]
        return "end"
    except ValueError:
        return "end"
