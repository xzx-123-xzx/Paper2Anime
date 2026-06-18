import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from common.config import Config

conf = Config()

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 优先使用 SQLite（避免复杂的 MySQL 配置问题）
# 如果用户明确配置了 MySQL 所有必填参数才使用 MySQL
_use_mysql = (
    bool(conf.MYSQL_USER)
    and bool(conf.MYSQL_PASSWORD)
    and bool(conf.MYSQL_DATABASE)
    and bool(getattr(conf, "FORCE_MYSQL", False))
)

if _use_mysql:
    mysql_port = getattr(conf, "MYSQL_PORT", 3306)
    DATABASE_URL = f"mysql+pymysql://{conf.MYSQL_USER}:{conf.MYSQL_PASSWORD}@{conf.MYSQL_HOST}:{mysql_port}/{conf.MYSQL_DATABASE}?charset=utf8mb4"
else:
    # 默认使用 SQLite，开箱即用
    DATABASE_URL = f"sqlite:///{DATA_DIR / 'paper2anime.db'}"

_engine_kwargs = {"echo": False}
if _use_mysql:
    _engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表。对于 SQLite，直接创建所有表即可；对于 MySQL 会删除旧有外键约束的表再重新创建。"""
    from . import models  # noqa: F401

    # SQLite 简单创建
    if "sqlite" in DATABASE_URL:
        Base.metadata.create_all(bind=engine)
        return

    # MySQL: 如果存在旧表（带有外键约束），先 drop 再 create
    try:
        with engine.connect() as conn:
            existing_tables = conn.execute(
                "SHOW TABLES"
            ).fetchall()
            if existing_tables:
                # 关闭外键检查后删除所有表
                conn.execute("SET FOREIGN_KEY_CHECKS = 0")
                for (table_name,) in existing_tables:
                    try:
                        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                    except Exception:
                        pass
                conn.execute("SET FOREIGN_KEY_CHECKS = 1")
                conn.commit()
    except Exception:
        pass

    Base.metadata.create_all(bind=engine)
