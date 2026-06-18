from typing import Dict, Any
from langgraph.graph import StateGraph, END
from common.logger import my_logger as logger

from .state import WorkflowState, TaskStatus, get_initial_state
from .nodes.document_parser_node import document_parser_node
from .nodes.script_generator_node import script_generator_node
from .nodes.storyboard_generator_node import storyboard_generator_node
from .nodes.character_designer_node import character_designer_node
from .nodes.image_generator_node import image_generator_node
from .nodes.video_generator_node import video_generator_node
from .nodes.video_editor_node import video_editor_node
from .nodes.quality_check_node import quality_check_node
from .edges.routing import should_continue, routing_decision

def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("document_parser", document_parser_node)
    workflow.add_node("script_generator", script_generator_node)
    workflow.add_node("storyboard_generator", storyboard_generator_node)
    workflow.add_node("character_designer", character_designer_node)
    workflow.add_node("image_generator", image_generator_node)
    workflow.add_node("video_generator", video_generator_node)
    workflow.add_node("video_editor", video_editor_node)
    workflow.add_node("quality_check", quality_check_node)
    
    workflow.set_entry_point("document_parser")
    
    workflow.add_edge("document_parser", "script_generator")
    workflow.add_edge("script_generator", "storyboard_generator")
    workflow.add_edge("storyboard_generator", "character_designer")
    workflow.add_edge("character_designer", "image_generator")
    workflow.add_edge("image_generator", "video_generator")
    workflow.add_edge("video_generator", "video_editor")
    workflow.add_edge("video_editor", "quality_check")
    workflow.add_edge("quality_check", END)
    
    return workflow

def compile_workflow():
    workflow = create_workflow()
    return workflow.compile()

async def run_workflow(project_id: str, user_id: str, document_id: str, document_path: str, settings: Dict[str, Any] = None):
    logger.info(f"启动工作流: project_id={project_id}")
    
    initial_state = get_initial_state(
        project_id=project_id,
        user_id=user_id,
        document_id=document_id,
        document_path=document_path,
        settings=settings
    )
    
    app = compile_workflow()
    
    final_state = None
    async for state in app.astream(initial_state):
        final_state = state
        current_node = state.get("current_node", "unknown")
        progress = state.get("progress", 0)
        logger.info(f"工作流进度: {current_node} - {progress}%")
    
    logger.info(f"工作流完成: project_id={project_id}")
    return final_state

def run_workflow_sync(project_id: str, user_id: str, document_id: str, document_path: str, settings: Dict[str, Any] = None):
    logger.info(f"启动工作流(同步): project_id={project_id}")
    
    initial_state = get_initial_state(
        project_id=project_id,
        user_id=user_id,
        document_id=document_id,
        document_path=document_path,
        settings=settings
    )
    
    app = compile_workflow()
    final_state = app.invoke(initial_state)
    
    logger.info(f"工作流完成(同步): project_id={project_id}")
    return final_state
