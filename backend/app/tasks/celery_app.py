import os
from celery import Celery
from common.config import Config

conf = Config()

celery_app = Celery(
    "paper2anime",
    broker=os.getenv("CELERY_BROKER_URL", f"redis://{conf.REDIS_HOST}:{conf.REDIS_PORT}/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", f"redis://{conf.REDIS_HOST}:{conf.REDIS_PORT}/2"),
    include=[
        "backend.app.tasks.document_tasks",
        "backend.app.tasks.generation_tasks",
        "backend.app.tasks.video_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 2,
    task_soft_time_limit=3600 * 1.5,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

celery_app.autodiscover_tasks(["backend.app.tasks"])
