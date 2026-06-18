import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

from common.logger import my_logger as logger

from .state import WorkflowState, TaskStatus, get_initial_state
from .workflow import compile_workflow
from ..models.database import SessionLocal, get_db
from ..crud import project_crud, workflow_crud, document_crud

_active_workflows: Dict[str, threading.Thread] = {}


def _run_workflow_in_thread(
    project_id: str,
    user_id: str,
    document_id: str,
    document_path: str,
    workflow_id: str,
    settings: Dict[str, Any] = None,
) -> None:
    """在独立线程中运行工作流，持续更新数据库状态"""
    db = SessionLocal()
    try:
        logger.info(f"[工作流 {workflow_id}] 开始执行，项目: {project_id}")

        workflow_crud.update_workflow_status(
            db, workflow_id,
            status="running",
            current_node="document_parser",
            progress=0.0,
        )
        project_crud.update_project_status(
            db, project_id,
            status="parsing",
            progress=0.0,
            current_stage="document_parser",
        )

        initial_state = get_initial_state(
            project_id=project_id,
            user_id=user_id,
            document_id=document_id,
            document_path=document_path,
            settings=settings or {},
        )

        app = compile_workflow()
        final_state: Optional[Dict[str, Any]] = None

        total_nodes = 8.0
        node_progress_map = {
            "document_parser": 0,
            "script_generator": 1,
            "storyboard_generator": 2,
            "character_designer": 3,
            "image_generator": 4,
            "video_generator": 5,
            "video_editor": 6,
            "quality_check": 7,
        }

        try:
            current_state = dict(initial_state) if isinstance(initial_state, dict) else {}

            for output in app.stream(initial_state):
                for node_name, node_state in output.items():
                    if isinstance(node_state, dict):
                        current_state.update(node_state)
                    current_state["current_node"] = node_name
                    final_state = current_state

                    progress = current_state.get("progress", 0.0) or 0.0
                    node_statuses = current_state.get("node_statuses", {})

                    if node_name in node_progress_map:
                        display_progress = ((node_progress_map[node_name] + 1) / total_nodes) * 100
                    else:
                        display_progress = float(progress)

                    logger.info(f"[工作流 {workflow_id}] {node_name} - {display_progress:.0f}%")

                    workflow_crud.update_workflow_status(
                        db, workflow_id,
                        status="running",
                        current_node=node_name,
                        node_statuses=node_statuses,
                        progress=float(display_progress),
                    )
                    project_crud.update_project_status(
                        db, project_id,
                        status=node_name,
                        progress=float(display_progress),
                        current_stage=node_name,
                    )

                    script = current_state.get("script")
                    if script:
                        from ..models.schemas import ProjectUpdate
                        project_crud.update_project(db, project_id, ProjectUpdate(script=str(script)))

                    storyboard = current_state.get("storyboard")
                    if storyboard:
                        from ..models.schemas import ProjectUpdate
                        project_crud.update_project(db, project_id, ProjectUpdate(storyboard=storyboard))

                    characters = current_state.get("characters")
                    if characters:
                        from ..models.schemas import ProjectUpdate
                        project_crud.update_project(db, project_id, ProjectUpdate(characters=characters))

                    final_video_path = current_state.get("final_video_path")
                    if final_video_path:
                        from ..models.schemas import ProjectUpdate
                        project_crud.update_project(
                            db, project_id,
                            ProjectUpdate(final_video_url=final_video_path),
                        )

                    thumbnail_path = current_state.get("thumbnail_path")
                    if thumbnail_path:
                        from ..models.schemas import ProjectUpdate
                        project_crud.update_project(
                            db, project_id,
                            ProjectUpdate(thumbnail_url=thumbnail_path),
                        )

            workflow_crud.update_workflow_status(
                db, workflow_id,
                status="completed",
                current_node="done",
                progress=100.0,
            )
            project_crud.update_project_status(
                db, project_id,
                status="completed",
                progress=100.0,
                current_stage="done",
            )
            logger.info(f"[工作流 {workflow_id}] 完成")

        except Exception as e:
            logger.error(f"[工作流 {workflow_id}] 执行失败: {e}", exc_info=True)
            current_progress = float(final_state.get("progress", 0)) if final_state else 0.0
            workflow_crud.update_workflow_status(
                db, workflow_id,
                status="failed",
                progress=current_progress,
                error_message=str(e),
            )
            project_crud.update_project_status(
                db, project_id,
                status="failed",
                error_message=str(e),
            )
    finally:
        db.close()
        _active_workflows.pop(project_id, None)


def start_workflow_async(
    project_id: str,
    user_id: str,
    document_id: str,
    document_path: str,
    workflow_id: str,
    settings: Dict[str, Any] = None,
) -> None:
    """异步启动工作流（线程池）"""
    if project_id in _active_workflows:
        logger.warning(f"项目 {project_id} 已有工作流在运行，跳过")
        return

    thread = threading.Thread(
        target=_run_workflow_in_thread,
        args=(project_id, user_id, document_id, document_path, workflow_id, settings),
        daemon=True,
        name=f"workflow-{workflow_id}",
    )
    thread.start()
    _active_workflows[project_id] = thread
    logger.info(f"工作流线程启动: {workflow_id}")


def is_workflow_running(project_id: str) -> bool:
    return project_id in _active_workflows and _active_workflows[project_id].is_alive()
