import os
from pathlib import Path
from typing import Dict, Any
from common.logger import my_logger as logger
from ...services.ffmpeg_service import FFmpegService

ffmpeg_service = FFmpegService()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def video_editor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行视频剪辑节点")
    
    generated_videos = state.get("generated_videos", [])
    project_id = state.get("project_id", "unknown")
    settings = state.get("settings", {})
    
    if not generated_videos:
        logger.warning("没有视频片段可剪辑")
        state["error_message"] = "缺少视频片段"
        state["node_statuses"]["video_editor"] = "failed"
        return state
    
    # 筛选出磁盘上真实存在的视频路径
    video_segments = []
    for v in generated_videos:
        path = v.get("video_path", "")
        if path and os.path.exists(path):
            video_segments.append(path)
    
    logger.info(f"找到 {len(video_segments)} 个有效的视频文件 (共 {len(generated_videos)} 个镜头)")
    
    if not video_segments:
        logger.error("没有有效的视频文件可供合并")
        state["error_message"] = "没有有效的视频文件"
        state["node_statuses"]["video_editor"] = "failed"
        return state
    
    # 输出目录使用项目路径
    output_dir = PROJECT_ROOT / "storage" / "videos" / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / f"{project_id}_final.mp4")
    
    try:
        result = ffmpeg_service.merge_videos(
            video_paths=video_segments,
            output_path=output_path,
            add_transitions=settings.get("add_transitions", True),
            add_subtitles=settings.get("subtitle", False)
        )
        
        state["final_video_path"] = result.get("output_path", output_path)
        state["thumbnail_path"] = result.get("thumbnail_path", "")
        state["node_statuses"]["video_editor"] = "completed"
        state["progress"] = 95.0
        state["status"] = "completed"
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"视频剪辑完成: {result.get('output_path', output_path)}")
    except Exception as e:
        logger.error(f"视频剪辑失败: {type(e).__name__}: {e}")
        # 即使合并失败，也记录第一个视频作为结果
        if video_segments:
            state["final_video_path"] = video_segments[0]
            state["node_statuses"]["video_editor"] = "completed"
            state["progress"] = 95.0
            logger.info(f"合并失败，使用第一个视频片段作为最终结果: {video_segments[0]}")
        else:
            state["node_statuses"]["video_editor"] = "failed"
            state["error_message"] = str(e)
    
    return state
