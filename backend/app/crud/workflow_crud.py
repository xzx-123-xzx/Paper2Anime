import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.models import WorkflowModel, TaskModel

def create_workflow(db: Session, project_id: str) -> WorkflowModel:
    """创建工作流"""
    workflow_id = f"wf_{str(uuid.uuid4())[:12]}"
    
    db_workflow = WorkflowModel(
        workflow_id=workflow_id,
        project_id=project_id,
        status="pending",
        node_statuses={}
    )
    
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def get_workflow(db: Session, workflow_id: str) -> Optional[WorkflowModel]:
    """获取工作流"""
    return db.query(WorkflowModel).filter(WorkflowModel.workflow_id == workflow_id).first()

def get_workflow_by_project(db: Session, project_id: str) -> Optional[WorkflowModel]:
    """根据项目获取工作流"""
    return db.query(WorkflowModel).filter(WorkflowModel.project_id == project_id).first()

def update_workflow_status(db: Session, workflow_id: str, status: str, current_node: str = None, 
                          node_statuses: dict = None, progress: float = None, error_message: str = None) -> Optional[WorkflowModel]:
    """更新工作流状态"""
    workflow = db.query(WorkflowModel).filter(WorkflowModel.workflow_id == workflow_id).first()
    
    if not workflow:
        return None
    
    if status:
        workflow.status = status
    if current_node is not None:
        workflow.current_node = current_node
    if node_statuses is not None:
        workflow.node_statuses = node_statuses
    if progress is not None:
        workflow.progress = progress
    if error_message is not None:
        workflow.error_message = error_message
    
    workflow.updated_at = datetime.now()
    db.commit()
    db.refresh(workflow)
    return workflow

def create_task(db: Session, project_id: str, task_type: str, workflow_id: str = None) -> TaskModel:
    """创建任务"""
    task_id = f"task_{str(uuid.uuid4())[:12]}"
    
    db_task = TaskModel(
        task_id=task_id,
        project_id=project_id,
        task_type=task_type,
        workflow_id=workflow_id,
        status="pending"
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: str, status: str, progress: float = None,
                       result: dict = None, error_message: str = None) -> Optional[TaskModel]:
    """更新任务状态"""
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

    if not task:
        return None

    task.status = status
    if progress is not None:
        task.progress = progress
    if result is not None:
        task.result = result
    if error_message is not None:
        task.error_message = error_message

    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    return task

def delete_workflows_by_project(db: Session, project_id: str) -> int:
    """删除项目相关的所有工作流和任务记录，返回删除数"""
    deleted = 0

    # 先删除任务
    tasks = db.query(TaskModel).filter(TaskModel.project_id == project_id).all()
    for t in tasks:
        db.delete(t)
        deleted += 1

    # 再删除工作流
    workflows = db.query(WorkflowModel).filter(WorkflowModel.project_id == project_id).all()
    for w in workflows:
        db.delete(w)
        deleted += 1

    db.commit()
    return deleted