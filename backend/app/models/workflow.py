from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class WorkflowStatus(BaseModel):
    workflow_id: str
    project_id: str
    status: TaskStatus
    current_node: str
    progress: float
    node_statuses: Dict[str, TaskStatus] = {}
    estimated_time_remaining: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WorkflowStartRequest(BaseModel):
    project_id: str
    options: Optional[Dict] = None
