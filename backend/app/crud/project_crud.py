import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.models import ProjectModel, WorkflowModel
from ..models.schemas import ProjectCreate, ProjectUpdate, ProjectSettings

def create_project(db: Session, project: ProjectCreate) -> ProjectModel:
    """创建项目"""
    project_id = str(uuid.uuid4())
    
    db_project = ProjectModel(
        project_id=project_id,
        user_id=project.user_id,
        name=project.name,
        description=project.description or "",
        document_id=project.document_id,
        settings=project.settings.model_dump() if project.settings else None,
        status="pending",
        progress=0.0,
        current_stage="created"
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: str) -> Optional[ProjectModel]:
    """获取项目"""
    return db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()

def get_projects(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> List[ProjectModel]:
    """获取项目列表"""
    return db.query(ProjectModel).filter(
        ProjectModel.user_id == user_id
    ).order_by(ProjectModel.created_at.desc()).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: str, updates: ProjectUpdate) -> Optional[ProjectModel]:
    """更新项目"""
    project = db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()
    
    if not project:
        return None
    
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(project, field, value)
    
    project.updated_at = datetime.now()
    db.commit()
    db.refresh(project)
    return project

def update_project_status(db: Session, project_id: str, status: str, progress: float = None, current_stage: str = None) -> Optional[ProjectModel]:
    """更新项目状态"""
    project = db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()
    
    if not project:
        return None
    
    project.status = status
    if progress is not None:
        project.progress = progress
    if current_stage is not None:
        project.current_stage = current_stage
    project.updated_at = datetime.now()
    
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: str) -> bool:
    """删除项目"""
    project = db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()
    
    if not project:
        return False
    
    db.delete(project)
    db.commit()
    return True

def count_projects(db: Session, user_id: str) -> int:
    """统计项目数量"""
    return db.query(ProjectModel).filter(ProjectModel.user_id == user_id).count()