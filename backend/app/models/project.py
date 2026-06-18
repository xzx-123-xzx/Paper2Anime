from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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

class Project(BaseModel):
    project_id: str = Field(..., description="项目唯一标识")
    user_id: str = Field(..., description="用户ID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = ""
    document_id: str
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    status: ProjectStatus = ProjectStatus.PENDING
    progress: float = 0.0
    current_stage: str = ""
    script: Optional[str] = None
    storyboard: Optional[List[Dict[str, Any]]] = None
    characters: Optional[List[Dict[str, Any]]] = None
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    cost_estimate: float = 0.0
    cost_actual: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    document_id: str
    settings: Optional[ProjectSettings] = None

class ProjectResponse(BaseModel):
    project_id: str
    name: str
    status: ProjectStatus
    progress: float
    current_stage: str
    created_at: datetime
    updated_at: datetime
