from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class VideoSegment(BaseModel):
    segment_id: str
    scene_id: str
    file_path: str
    url: str
    duration: float
    start_time: float
    end_time: float
    status: str = "pending"

class Video(BaseModel):
    video_id: str
    project_id: str
    segments: List[VideoSegment] = []
    final_path: Optional[str] = None
    final_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: float = 0.0
    resolution: str = "1920x1080"
    file_size: int = 0
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
