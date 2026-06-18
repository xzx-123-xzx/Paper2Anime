import uuid
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.models import ProjectModel
from backend.app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.crud import project_crud, workflow_crud
from backend.app.core.exceptions import ProjectNotFoundError
from backend.app.api.v1.deps import get_current_user
from common.logger import my_logger as logger

router = APIRouter()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


@router.post("/", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建项目"""
    db_project = project_crud.create_project(db, request)
    logger.info(f"项目创建成功: {db_project.project_id}")

    return db_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    projects = project_crud.get_projects(db, user_id, skip, limit)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = project_crud.get_project(db, project_id)

    if not project:
        raise ProjectNotFoundError()

    if project.user_id != user_id:
        raise ProjectNotFoundError()

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新项目"""
    project = project_crud.get_project(db, project_id)

    if not project:
        raise ProjectNotFoundError()

    if project.user_id != user_id:
        raise ProjectNotFoundError()

    updated = project_crud.update_project(db, project_id, updates)
    return updated


@router.get("/{project_id}/video")
async def get_project_video(
    project_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """下载/预览项目生成的视频文件"""
    project = project_crud.get_project(db, project_id)
    if not project:
        raise ProjectNotFoundError()
    if project.user_id != user_id:
        raise ProjectNotFoundError()

    local_path = getattr(project, "final_video_url", None)
    if not local_path:
        raise HTTPException(status_code=404, detail="项目尚未生成视频")

    # 如果是 URL（比如外网资源），直接 307 跳转
    if local_path.startswith("http://") or local_path.startswith("https://"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=local_path, status_code=307)

    # 本地文件
    if not Path(local_path).exists():
        # 尝试拼接一个常见位置
        candidate = PROJECT_ROOT / "storage" / "videos" / f"{project_id}_final.mp4"
        if candidate.exists():
            local_path = str(candidate)
        else:
            raise HTTPException(status_code=404, detail=f"文件不存在: {local_path}")

    filename = Path(local_path).name
    return FileResponse(
        path=local_path,
        filename=filename,
        media_type="video/mp4",
    )


def _cleanup_project_files(project_id: str) -> int:
    """清理项目相关的本地文件，返回清理的文件数"""
    cleaned = 0
    storage_root = PROJECT_ROOT / "storage"

    # 待清理的子目录
    sub_dirs = ["images", "videos", "scripts", "storyboards"]
    for sub in sub_dirs:
        target = storage_root / sub / project_id
        if target.exists() and target.is_dir():
            try:
                shutil.rmtree(target)
                cleaned += 1
                logger.info(f"已清理目录: {target}")
            except Exception as e:
                logger.warning(f"清理目录失败 {target}: {e}")

    # 清理可能存在的项目最终视频文件
    final_video = storage_root / "videos" / f"{project_id}_final.mp4"
    if final_video.exists():
        try:
            final_video.unlink()
            cleaned += 1
            logger.info(f"已清理文件: {final_video}")
        except Exception as e:
            logger.warning(f"清理文件失败 {final_video}: {e}")

    return cleaned


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除项目"""
    project = project_crud.get_project(db, project_id)

    if not project:
        raise ProjectNotFoundError()

    if project.user_id != user_id:
        raise ProjectNotFoundError()

    # 清理工作流记录
    workflow_crud.delete_workflows_by_project(db, project_id)

    # 清理本地文件
    cleaned_files = _cleanup_project_files(project_id)

    # 删除项目记录
    success = project_crud.delete_project(db, project_id)

    return {
        "success": success,
        "project_id": project_id,
        "cleaned_files": cleaned_files
    }
