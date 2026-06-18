from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_STORYBOARD = "generating_storyboard"
    GENERATING_CHARACTERS = "generating_characters"
    GENERATING_IMAGES = "generating_images"
    GENERATING_VIDEOS = "generating_videos"
    EDITING = "editing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectSettings(BaseModel):
    quality_preset: str = "standard"
    voiceover: bool = False
    subtitle: bool = True
    aspect_ratio: str = "16:9"
    resolution: str = "1920x1080"

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""
    document_id: str
    settings: Optional[ProjectSettings] = None

class ProjectCreate(ProjectBase):
    user_id: str = "default_user"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[ProjectSettings] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    current_stage: Optional[str] = None
    script: Optional[str] = None
    storyboard: Optional[List[Dict[str, Any]]] = None
    characters: Optional[List[Dict[str, Any]]] = None
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: str
    user_id: str
    name: str
    description: Optional[str]
    document_id: Optional[str]
    settings: Optional[Dict[str, Any]]
    status: str
    progress: float
    current_stage: Optional[str]
    script: Optional[str]
    storyboard: Optional[List[Dict[str, Any]]]
    characters: Optional[List[Dict[str, Any]]]
    final_video_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    document_id: str
    user_id: str
    file_path: str
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    workflow_id: str
    project_id: str
    status: str
    current_node: Optional[str]
    node_statuses: Optional[Dict[str, str]]
    progress: float
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    task_id: str
    workflow_id: Optional[str]
    project_id: str
    task_type: str
    status: str
    progress: float
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowStartRequest(BaseModel):
    project_id: str
    options: Optional[Dict[str, Any]] = None