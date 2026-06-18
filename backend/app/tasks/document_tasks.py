from celery import Task
from common.logger import my_logger as logger
from .celery_app import celery_app
from ..services.document_parser import DocumentParser

document_parser = DocumentParser()

@celery_app.task(bind=True, name="tasks.parse_document")
def parse_document_task(self: Task, document_id: str, file_path: str) -> dict:
    logger.info(f"开始解析文档: {document_id}")
    
    try:
        result = document_parser.parse(file_path)
        
        return {
            "status": "completed",
            "document_id": document_id,
            "parsed_content": result.get("content", {}),
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        logger.error(f"文档解析失败: {e}")
        return {
            "status": "failed",
            "document_id": document_id,
            "error": str(e)
        }
