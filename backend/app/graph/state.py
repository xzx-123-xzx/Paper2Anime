from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class WorkflowState(TypedDict):
    project_id: str
    user_id: str
    document_id: str
    document_path: str
    raw_document: str
    parsed_document: Dict[str, Any]
    document_metadata: Dict[str, Any]
    script: Optional[str]
    script_version: int
    storyboard: Optional[List[Dict[str, Any]]]
    storyboard_version: int
    characters: Optional[List[Dict[str, Any]]]
    character_images: Optional[Dict[str, Dict[str, str]]]
    generated_images: Optional[List[Dict[str, Any]]]
    generated_videos: Optional[List[Dict[str, Any]]]
    final_video_path: Optional[str]
    thumbnail_path: Optional[str]
    current_node: str
    status: TaskStatus
    node_statuses: Dict[str, TaskStatus]
    progress: float
    error_message: Optional[str]
    quality_score: Optional[float]
    retry_count: int
    max_retries: int
    cost_estimate: float
    cost_actual: float
    created_at: str
    updated_at: str
    settings: Dict[str, Any]

def get_initial_state(project_id: str, user_id: str, document_id: str, document_path: str, settings: Dict[str, Any] = None) -> WorkflowState:
    """初始化工作流状态"""
    from datetime import datetime
    return WorkflowState(
        project_id=project_id,
        user_id=user_id,
        document_id=document_id,
        document_path=document_path,
        raw_document="",
        parsed_document={},
        document_metadata={},
        script=None,
        script_version=0,
        storyboard=None,
        storyboard_version=0,
        characters=None,
        character_images=None,
        generated_images=None,
        generated_videos=None,
        final_video_path=None,
        thumbnail_path=None,
        current_node="document_parser",
        status=TaskStatus.PENDING,
        node_statuses={},
        progress=0.0,
        error_message=None,
        quality_score=None,
        retry_count=0,
        max_retries=3,
        cost_estimate=0.0,
        cost_actual=0.0,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        settings=settings or {}
    )