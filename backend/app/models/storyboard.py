from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CameraMovement(str, Enum):
    FIXED = "固定"
    PAN_LEFT = "左摇"
    PAN_RIGHT = "右摇"
    TILT_UP = "上摇"
    TILT_DOWN = "下摇"
    DOLLY_IN = "推进"
    DOLLY_OUT = "拉出"
    TRACKING = "跟拍"
    CRANE_UP = "升格"
    CRANE_DOWN = "降格"

class ShotType(str, Enum):
    EXTREME_WIDE = "极远景"
    WIDE = "远景"
    FULL = "全景"
    MEDIUM_WIDE = "中远景"
    MEDIUM = "中景"
    MEDIUM_CLOSE = "中近景"
    CLOSE_UP = "近景"
    EXTREME_CLOSE_UP = "特写"
    TWO_SHOT = "双镜头"
    OVER_SHOULDER = "过肩"

class Scene(BaseModel):
    scene_id: str
    sequence: int
    description: str
    characters: List[str] = []
    dialogue: Optional[str] = None
    narration: Optional[str] = None
    camera_movement: CameraMovement = CameraMovement.FIXED
    shot_type: ShotType = ShotType.MEDIUM
    duration: float = 5.0
    image_prompt: str
    video_prompt: str
    status: str = "pending"
    generated_image_url: Optional[str] = None
    generated_video_url: Optional[str] = None

class Storyboard(BaseModel):
    storyboard_id: str
    project_id: str
    version: int = 1
    scenes: List[Scene] = []
    total_duration: float = 0.0
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
