import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.models import DocumentModel
from backend.app.crud import document_crud
from backend.app.core.config import settings
from backend.app.core.exceptions import DocumentUploadError, UnsupportedFileTypeError, FileTooLargeError
from backend.app.api.v1.deps import get_current_user
from common.logger import my_logger as logger

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文档"""
    logger.info(f"收到文档上传请求: {file.filename}")
    
    if not file.filename:
        raise DocumentUploadError("文件名为空")
    
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"不支持的文件格式: {ext}")
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise FileTooLargeError(f"文件大小超过 {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB 限制")
    
    document_id = str(uuid.uuid4())
    file_name = file.filename
    relative_path = os.path.join("documents", user_id, document_id, file_name)
    file_path = os.path.join(settings.LOCAL_STORAGE_PATH, relative_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 保存到数据库
    doc = document_crud.create_document(
        db, user_id, file_path, file_name, ext, len(content)
    )
    
    logger.info(f"文档上传成功: {document_id}, 路径: {file_path}")
    
    return {
        "document_id": doc.document_id,
        "file_path": file_path,
        "status": "uploaded"
    }

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档详情"""
    document = document_crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.user_id != user_id:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return {
        "document_id": document.document_id,
        "file_name": document.file_name,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "parsed_content": document.parsed_content,
        "metadata": document.document_metadata,
        "created_at": document.created_at
    }

@router.post("/{document_id}/parse")
async def parse_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解析文档"""
    document = document_crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    from backend.app.services.document_parser import DocumentParser
    parser = DocumentParser()
    
    try:
        result = parser.parse(document.file_path)
        
        document_crud.update_document_content(
            db, document_id,
            result.get("content", {}),
            result.get("metadata", {})
        )
        
        return {
            "status": "completed",
            "document_id": document_id,
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        logger.error(f"文档解析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载文档"""
    document = document_crud.get_document(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.user_id != user_id:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        document.file_path,
        media_type="application/octet-stream",
        filename=document.file_name
    )