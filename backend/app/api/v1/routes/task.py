from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.models import TaskModel, WorkflowModel, ProjectModel, DocumentModel
from backend.app.models.schemas import WorkflowStartRequest
from backend.app.crud import project_crud, workflow_crud
from backend.app.graph.runner import start_workflow_async
from common.logger import my_logger as logger

router = APIRouter()


@router.post("/workflows/start")
async def start_workflow(
    request: WorkflowStartRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db),
):
    """启动工作流 - 使用线程池异步执行，不依赖 Celery/Redis"""
    logger.info(f"启动工作流: project_id={request.project_id}")

    project = project_crud.get_project(db, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    document = db.query(DocumentModel).filter(
        DocumentModel.document_id == project.document_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    workflow = workflow_crud.create_workflow(db, request.project_id)
    logger.info(f"工作流已创建: workflow_id={workflow.workflow_id}")

    settings = project.settings if project.settings else {}

    start_workflow_async(
        project_id=request.project_id,
        user_id=user_id,
        document_id=project.document_id,
        document_path=document.file_path,
        workflow_id=workflow.workflow_id,
        settings=settings,
    )

    return {
        "workflow_id": workflow.workflow_id,
        "project_id": request.project_id,
        "status": "started",
    }


@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """获取工作流状态"""
    workflow = workflow_crud.get_workflow(db, workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    return {
        "workflow_id": workflow.workflow_id,
        "project_id": workflow.project_id,
        "status": workflow.status,
        "current_node": workflow.current_node,
        "node_statuses": workflow.node_statuses,
        "progress": workflow.progress,
        "error_message": workflow.error_message,
    }


@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """取消工作流"""
    workflow = workflow_crud.get_workflow(db, workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow_crud.update_workflow_status(
        db, workflow_id,
        status="cancelled",
    )
    project_crud.update_project_status(
        db, workflow.project_id,
        status="failed",
        current_stage="cancelled",
    )

    return {"status": "cancelled", "workflow_id": workflow_id}


@router.get("/workflows/{workflow_id}/result")
async def get_workflow_result(
    workflow_id: str,
    db: Session = Depends(get_db),
):
    """获取工作流结果"""
    workflow = workflow_crud.get_workflow(db, workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    project = project_crud.get_project(db, workflow.project_id)

    return {
        "workflow_id": workflow.workflow_id,
        "status": workflow.status,
        "project": {
            "project_id": project.project_id if project else None,
            "final_video_url": project.final_video_url if project else None,
            "thumbnail_url": project.thumbnail_url if project else None,
            "script": project.script if project else None,
            "storyboard": project.storyboard if project else None,
            "characters": project.characters if project else None,
        },
    }


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
):
    """获取任务状态"""
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "result": task.result,
        "error_message": task.error_message,
    }


@router.get("/{task_id}/logs")
async def get_task_logs(task_id: str):
    """获取任务日志"""
    return {"task_id": task_id, "logs": []}
