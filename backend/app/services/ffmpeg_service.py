import os
import shutil
import subprocess
import tempfile
from typing import List, Dict, Any, Optional

from common.logger import my_logger as logger

# 从环境变量读取 ffmpeg 路径，默认使用系统 PATH 中的 ffmpeg
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")


def _find_ffmpeg():
    """查找 ffmpeg 可执行文件路径"""
    # 如果配置的是目录，尝试在该目录下找 bin/ffmpeg.exe
    if os.path.isdir(FFMPEG_PATH):
        possible_paths = [
            os.path.join(FFMPEG_PATH, "bin", "ffmpeg.exe"),
            os.path.join(FFMPEG_PATH, "ffmpeg.exe"),
            os.path.join(FFMPEG_PATH, "bin", "ffmpeg"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p
        return FFMPEG_PATH

    # 如果配置的是文件但不存在，尝试在 PATH 中查找
    if not os.path.exists(FFMPEG_PATH):
        # 尝试常见位置
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            os.path.join(os.path.dirname(FFMPEG_PATH), "bin", "ffmpeg.exe"),
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
        # 返回原始值，让 subprocess 查找
        return "ffmpeg"

    return FFMPEG_PATH


def _run_ffmpeg(cmd: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """执行 ffmpeg 命令，处理 Windows 路径问题"""
    # 找到正确的 ffmpeg 路径
    ffmpeg_exe = _find_ffmpeg()

    # 如果路径包含空格或特殊字符，在 Windows 上需要处理
    if os.name == 'nt' and ' ' in ffmpeg_exe:
        # Windows 上包含空格的路径需要用双引号包裹
        # 但 subprocess.list2cmdline 已经处理了大部分情况
        # 这里主要是确保 ffmpeg_exe 是正确的
        pass

    # 替换命令中的 ffmpeg 为完整路径
    cmd[0] = ffmpeg_exe

    logger.info(f"执行命令: {os.path.basename(ffmpeg_exe)} ...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            # Windows 上需要 creationflags 来避免弹出窗口
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result
    except subprocess.TimeoutExpired as e:
        logger.error(f"ffmpeg 执行超时: {timeout}秒")
        raise
    except FileNotFoundError:
        logger.error(f"ffmpeg 命令找不到: {ffmpeg_exe}")
        raise
    except Exception as e:
        logger.error(f"执行 ffmpeg 失败: {e}")
        raise


class FFmpegService:
    def merge_videos(
        self,
        video_paths: List[str],
        output_path: str,
        add_transitions: bool = True,
        add_subtitles: bool = False
    ) -> Dict[str, Any]:
        logger.info(f"合并 {len(video_paths)} 个视频片段: {output_path}")
        logger.info(f"使用 ffmpeg 路径: {FFMPEG_PATH}")

        # 检查 ffmpeg 是否可用
        try:
            result = _run_ffmpeg([FFMPEG_PATH, "-version"], timeout=5)
            if result.returncode != 0:
                logger.warning(f"ffmpeg 不可用: {result.stderr.decode()[:200]}")
        except FileNotFoundError:
            logger.warning(f"ffmpeg 命令找不到: {FFMPEG_PATH}，请安装 ffmpeg 或在 .env 中配置 FFMPEG_PATH")
        except Exception as e:
            logger.warning(f"检查 ffmpeg 失败: {e}")

        # 检查文件是否存在且有一定大小
        valid_paths = [p for p in video_paths if p and os.path.exists(p) and os.path.getsize(p) > 0]

        if not valid_paths:
            raise ValueError("没有有效的视频文件")

        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            if len(valid_paths) == 1:
                shutil.copy(valid_paths[0], output_path)
                logger.info(f"只有一个视频片段，直接复制: {output_path}")
            else:
                # 使用 concat demuxer 方式（最稳定）
                self._merge_with_concat_demuxer(valid_paths, output_path)

            thumbnail_path = self._generate_thumbnail(output_path)

            return {
                "output_path": output_path,
                "thumbnail_path": thumbnail_path,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"视频合并失败: {type(e).__name__}: {e}")
            # 失败降级：复制第一个视频作为结果
            if valid_paths:
                try:
                    shutil.copy(valid_paths[0], output_path)
                    logger.info(f"降级：使用第一个视频片段作为最终结果")
                    return {
                        "output_path": output_path,
                        "thumbnail_path": self._generate_thumbnail(output_path),
                        "status": "partial"
                    }
                except Exception:
                    pass
            raise

    def _merge_with_concat_demuxer(self, video_paths: List[str], output_path: str) -> bool:
        """使用 concat demuxer 合并视频"""
        temp_dir = tempfile.gettempdir()
        concat_file = os.path.join(temp_dir, f"ffmpeg_concat_{abs(hash(output_path))}.txt")

        try:
            # 创建 concat 文件列表
            with open(concat_file, 'w', encoding='utf-8') as f:
                for p in video_paths:
                    # Windows 路径需要特殊处理
                    # 使用绝对路径，转义特殊字符
                    safe_path = os.path.abspath(p)
                    # 在 concat 文件中，路径需要转义单引号
                    safe_path = safe_path.replace("'", "'\\''")
                    # Windows 跃径中的反斜杠在 concat 文件中需要保持
                    f.write(f"file '{safe_path}'\n")

            logger.info(f"创建 concat 文件: {concat_file}")

            # 方法1: 使用 concat demuxer + stream copy（最快，无需重新编码）
            cmd = [
                FFMPEG_PATH, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-loglevel", "warning",
                output_path
            ]

            result = _run_ffmpeg(cmd, timeout=120)

            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"concat demuxer + copy 成功合并 {len(video_paths)} 个视频")
                return True

            # 方法2: 如果 copy 失败（可能编码不兼容），使用重新编码
            logger.warning(f"concat copy 失败 (返回码 {result.returncode})，尝试重新编码")
            logger.debug(f"stderr: {result.stderr.decode()[:500]}")

            cmd = [
                FFMPEG_PATH, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-loglevel", "warning",
                output_path
            ]

            result = _run_ffmpeg(cmd, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"concat demuxer + re-encode 成功合并 {len(video_paths)} 个视频")
                return True

            # 方法3: 使用 filter_complex concat（最可靠但最慢）
            logger.warning("concat demuxer 失败，尝试 filter_complex 方式")

            inputs = []
            filter_parts = []
            for i, p in enumerate(video_paths):
                inputs.extend(["-i", p])

            # 构建 filter_complex 表达式
            # concat=n=v:a=1 格式，n 是视频数量，v=1 表示每个输入有1个视频流，a=1 表示每个输入有1个音频流
            filter_complex = f"concat=n={len(video_paths)}:v=1:a=1[outv][outa]"

            cmd = [FFMPEG_PATH, "-y"] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-loglevel", "warning",
                output_path
            ]

            result = _run_ffmpeg(cmd, timeout=600)

            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"filter_complex 成功合并 {len(video_paths)} 个视频")
                return True

            raise RuntimeError(f"所有合并方法都失败了。最后错误: {result.stderr.decode()[:500]}")

        finally:
            # 清理临时文件
            if os.path.exists(concat_file):
                try:
                    os.remove(concat_file)
                except Exception:
                    pass

    def _generate_thumbnail(self, video_path: str) -> Optional[str]:
        try:
            if not video_path or not os.path.exists(video_path):
                return None

            thumbnail_dir = os.path.join(os.path.dirname(video_path), "thumbnails")
            os.makedirs(thumbnail_dir, exist_ok=True)

            thumbnail_path = os.path.join(
                thumbnail_dir,
                f"{os.path.splitext(os.path.basename(video_path))[0]}.jpg"
            )

            cmd = [
                FFMPEG_PATH, "-y",
                "-ss", "1",
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                "-loglevel", "warning",
                thumbnail_path
            ]

            result = _run_ffmpeg(cmd, timeout=15)

            if result.returncode == 0 and os.path.exists(thumbnail_path):
                logger.info(f"缩略图生成成功: {thumbnail_path}")
                return thumbnail_path

            logger.warning(f"缩略图生成失败: {result.stderr.decode()[:200]}")

        except FileNotFoundError:
            logger.warning(f"ffmpeg 找不到，无法生成缩略图")
        except Exception as e:
            logger.warning(f"缩略图生成失败: {e}")

        return None

    def add_subtitles(self, video_path: str, subtitle_path: str, output_path: str) -> Dict[str, Any]:
        try:
            cmd = [
                FFMPEG_PATH, "-y",
                "-i", video_path,
                "-vf", f"subtitles={subtitle_path}",
                "-c:a", "copy",
                "-loglevel", "warning",
                output_path
            ]

            result = _run_ffmpeg(cmd, timeout=120)

            if result.returncode == 0:
                return {"output_path": output_path, "status": "success"}

            return {"output_path": video_path, "status": "error"}

        except Exception as e:
            logger.error(f"添加字幕失败: {e}")
            return {"output_path": video_path, "status": "error"}
