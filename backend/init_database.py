"""
数据库初始化脚本
创建所有需要的数据库表
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, Boolean, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from common.config import Config

Base = declarative_base()


class FileTypeEnum(enum.Enum):
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"


class ProjectStatusEnum(enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_STORYBOARD = "generating_storyboard"
    GENERATING_CHARACTERS = "generating_characters"
    GENERATING_IMAGES = "generating_images"
    GENERATING_VIDEOS = "generating_videos"
    EDITING = "editing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatusEnum(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class CharacterRoleEnum(enum.Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


class CameraMovementEnum(enum.Enum):
    FIXED = "固定"
    PAN_LEFT = "左摇"
    PAN_RIGHT = "右摇"
    TILT_UP = "上摇"
    TILT_DOWN = "下摇"
    DOLLY_IN = "推进"
    DOLLY_OUT = "拉出"
    TRACKING = "跟拍"
    CRANE_UP = "升格"
    CRANE_DOWN = "降格"


class ShotTypeEnum(enum.Enum):
    EXTREME_WIDE = "极远景"
    WIDE = "远景"
    FULL = "全景"
    MEDIUM_WIDE = "中远景"
    MEDIUM = "中景"
    MEDIUM_CLOSE = "中近景"
    CLOSE_UP = "近景"
    EXTREME_CLOSE_UP = "特写"
    TWO_SHOT = "双镜头"
    OVER_SHOULDER = "过肩"


# ==================== 用户表 ====================
class User(Base):
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(256))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ==================== 文档表 ====================
class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.user_id"), index=True, nullable=False)
    file_name = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(SQLEnum(FileTypeEnum), nullable=False)
    file_size = Column(Integer, default=0)
    title = Column(String(512))
    chapter_count = Column(Integer, default=0)
    parsed_content = Column(JSON)
    raw_text = Column(Text)
    status = Column(String(32), default="uploaded")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", backref="documents")
    projects = relationship("Project", back_populates="document")


# ==================== 项目表 ====================
class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.user_id"), index=True, nullable=False)
    document_id = Column(String(64), ForeignKey("documents.document_id"), index=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text)
    quality_preset = Column(String(32), default="standard")
    voiceover = Column(Boolean, default=False)
    subtitle = Column(Boolean, default=True)
    aspect_ratio = Column(String(16), default="16:9")
    resolution = Column(String(16), default="1920x1080")
    status = Column(SQLEnum(ProjectStatusEnum), default=ProjectStatusEnum.PENDING)
    progress = Column(Float, default=0.0)
    current_stage = Column(String(64))
    script = Column(Text)
    final_video_url = Column(String(1024))
    thumbnail_url = Column(String(1024))
    error_message = Column(Text)
    cost_estimate = Column(Float, default=0.0)
    cost_actual = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", backref="projects")
    document = relationship("Document", back_populates="projects")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    storyboards = relationship("Storyboard", back_populates="project", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="project", cascade="all, delete-orphan")


# ==================== 工作流表 ====================
class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.project_id"), index=True, nullable=False)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    current_node = Column(String(64))
    progress = Column(Float, default=0.0)
    node_statuses = Column(JSON, default={})
    estimated_time_remaining = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project", back_populates="workflows")
    tasks = relationship("WorkflowTask", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    task_id = Column(String(64), primary_key=True, index=True)
    workflow_id = Column(String(64), ForeignKey("workflows.workflow_id"), index=True, nullable=False)
    node_name = Column(String(64), nullable=False)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    workflow = relationship("Workflow", back_populates="tasks")


# ==================== 角色表 ====================
class Character(Base):
    __tablename__ = "characters"

    character_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.project_id"), index=True, nullable=False)
    name = Column(String(128), nullable=False)
    role = Column(SQLEnum(CharacterRoleEnum), default=CharacterRoleEnum.SUPPORTING)
    description = Column(Text)
    age_estimate = Column(String(32))
    gender = Column(String(16))
    height = Column(String(16))
    build = Column(String(32))
    hair_style = Column(String(64))
    hair_color = Column(String(32))
    eye_color = Column(String(32))
    skin_tone = Column(String(32))
    clothing_style = Column(String(128))
    distinguishing_features = Column(JSON, default=[])
    temperament = Column(String(64))
    speaking_style = Column(String(128))
    mannerisms = Column(JSON, default=[])
    image_urls = Column(JSON, default={})
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project", back_populates="characters")


# ==================== 分镜表 ====================
class Storyboard(Base):
    __tablename__ = "storyboards"

    storyboard_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.project_id"), index=True, nullable=False)
    version = Column(Integer, default=1)
    total_duration = Column(Float, default=0.0)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project", back_populates="storyboards")
    scenes = relationship("Scene", back_populates="storyboard", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"

    scene_id = Column(String(64), primary_key=True, index=True)
    storyboard_id = Column(String(64), ForeignKey("storyboards.storyboard_id"), index=True, nullable=False)
    sequence = Column(Integer, nullable=False)
    description = Column(Text)
    characters = Column(JSON, default=[])
    dialogue = Column(Text)
    narration = Column(Text)
    camera_movement = Column(SQLEnum(CameraMovementEnum), default=CameraMovementEnum.FIXED)
    shot_type = Column(SQLEnum(ShotTypeEnum), default=ShotTypeEnum.MEDIUM)
    duration = Column(Float, default=5.0)
    image_prompt = Column(Text)
    video_prompt = Column(Text)
    generated_image_url = Column(String(1024))
    generated_video_url = Column(String(1024))
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    storyboard = relationship("Storyboard", back_populates="scenes")


# ==================== 视频表 ====================
class Video(Base):
    __tablename__ = "videos"

    video_id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.project_id"), index=True, nullable=False)
    final_path = Column(String(1024))
    final_url = Column(String(1024))
    thumbnail_path = Column(String(1024))
    thumbnail_url = Column(String(1024))
    duration = Column(Float, default=0.0)
    resolution = Column(String(16), default="1920x1080")
    file_size = Column(Integer, default=0)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project", back_populates="videos")
    segments = relationship("VideoSegment", back_populates="video", cascade="all, delete-orphan")


class VideoSegment(Base):
    __tablename__ = "video_segments"

    segment_id = Column(String(64), primary_key=True, index=True)
    video_id = Column(String(64), ForeignKey("videos.video_id"), index=True, nullable=False)
    scene_id = Column(String(64), ForeignKey("scenes.scene_id"), index=True)
    file_path = Column(String(1024))
    url = Column(String(1024))
    duration = Column(Float, default=0.0)
    start_time = Column(Float, default=0.0)
    end_time = Column(Float, default=0.0)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    video = relationship("Video", back_populates="segments")


def get_database_url():
    """构建数据库连接 URL"""
    conf = Config()

    if conf.MYSQL_USER and conf.MYSQL_PASSWORD and conf.MYSQL_DATABASE:
        host = conf.MYSQL_HOST or "localhost"
        return f"mysql+pymysql://{conf.MYSQL_USER}:{conf.MYSQL_PASSWORD}@{host}/{conf.MYSQL_DATABASE}?charset=utf8mb4"
    else:
        # 默认使用 SQLite 作为演示
        db_path = os.path.join(os.path.dirname(__file__), "data", "paper2anime.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"


def create_tables(drop_existing=False):
    """创建所有数据库表"""
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)

    database_url = get_database_url()
    print(f"\n数据库地址: {database_url}")

    engine = create_engine(
        database_url,
        echo=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    if drop_existing:
        print("\n[警告] 将删除所有现有表...")
        Base.metadata.drop_all(engine)

    print("\n创建所有表...")
    Base.metadata.create_all(engine)
    print("表创建完成！")

    # 打印所有创建的表
    print("\n创建的表列表:")
    print("-" * 30)
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    print("-" * 30)

    print("\n数据库初始化完成！")
    return engine


def init_database():
    """初始化数据库"""
    create_tables(drop_existing=False)


def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    create_tables(drop_existing=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有现有表）")
    args = parser.parse_args()

    if args.reset:
        reset_database()
    else:
        init_database()
