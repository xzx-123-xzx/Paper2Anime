import os
from celery import Task
from common.logger import my_logger as logger
from .celery_app import celery_app
from ..services.ffmpeg_service import FFmpegService

ffmpeg_service = FFmpegService()

@celery_app.task(bind=True, name="tasks.merge_videos")
def merge_videos_task(self: Task, project_id: str, video_paths: list, settings: dict = None) -> dict:
    logger.info(f"开始合并视频: project_id={project_id}")
    
    settings = settings or {}
    output_dir = settings.get("output_dir", "./storage/videos")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{project_id}_final.mp4")
    
    try:
        result = ffmpeg_service.merge_videos(
            video_paths=video_paths,
            output_path=output_path,
            add_transitions=settings.get("add_transitions", True),
            add_subtitles=settings.get("add_subtitles", False)
        )
        
        return {
            "status": "completed",
            "project_id": project_id,
            "final_video_path": result.get("output_path"),
            "thumbnail_path": result.get("thumbnail_path")
        }
    except Exception as e:
        logger.error(f"视频合并失败: {e}")
        return {
            "status": "failed",
            "project_id": project_id,
            "error": str(e)
        }

@celery_app.task(bind=True, name="tasks.add_subtitles")
def add_subtitles_task(self: Task, video_path: str, subtitle_path: str, output_path: str = None) -> dict:
    logger.info(f"为视频添加字幕: {video_path}")
    
    try:
        if not output_path:
            output_path = video_path.replace(".mp4", "_subtitled.mp4")
        
        result = ffmpeg_service.add_subtitles(video_path, subtitle_path, output_path)
        
        return {
            "status": "completed" if result.get("status") == "success" else "failed",
            "output_path": result.get("output_path")
        }
    except Exception as e:
        logger.error(f"添加字幕失败: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }
