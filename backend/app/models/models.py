from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, BigInteger
from datetime import datetime
from .database import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    project_id = Column(String(36), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_id = Column(String(36), nullable=True)
    settings = Column(JSON, nullable=True)
    status = Column(String(50), default="pending", index=True)
    progress = Column(Float, default=0.0)
    current_stage = Column(String(100), nullable=True)
    script = Column(Text, nullable=True)
    storyboard = Column(JSON, nullable=True)
    characters = Column(JSON, nullable=True)
    final_video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    cost_estimate = Column(Float, default=0.0)
    cost_actual = Column(Float, default=0.0)
    workflow_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id = Column(String(36), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(20), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    parsed_content = Column(JSON, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class WorkflowModel(Base):
    __tablename__ = "workflows"

    workflow_id = Column(String(36), primary_key=True)
    project_id = Column(String(36), nullable=False, index=True)
    status = Column(String(50), default="pending")
    current_node = Column(String(100), nullable=True)
    node_statuses = Column(JSON, nullable=True)
    progress = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TaskModel(Base):
    __tablename__ = "tasks"

    task_id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), nullable=True, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    task_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(Float, default=0.0)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CharacterModel(Base):
    __tablename__ = "characters"

    character_id = Column(String(36), primary_key=True)
    project_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    appearance = Column(JSON, nullable=True)
    personality = Column(JSON, nullable=True)
    image_urls = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class VideoSegmentModel(Base):
    __tablename__ = "video_segments"

    segment_id = Column(String(36), primary_key=True)
    project_id = Column(String(36), nullable=False, index=True)
    scene_id = Column(String(36), nullable=False)
    file_path = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    duration = Column(Float, default=0.0)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
