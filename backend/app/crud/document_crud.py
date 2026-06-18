import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.models import DocumentModel

def create_document(db: Session, user_id: str, file_path: str, file_name: str, file_type: str, file_size: int) -> DocumentModel:
    """创建文档记录"""
    document_id = str(uuid.uuid4())
    
    db_document = DocumentModel(
        document_id=document_id,
        user_id=user_id,
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: str) -> Optional[DocumentModel]:
    """获取文档"""
    return db.query(DocumentModel).filter(DocumentModel.document_id == document_id).first()

def get_documents(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> List[DocumentModel]:
    """获取文档列表"""
    return db.query(DocumentModel).filter(
        DocumentModel.user_id == user_id
    ).order_by(DocumentModel.created_at.desc()).offset(skip).limit(limit).all()

def update_document_content(db: Session, document_id: str, parsed_content: dict, metadata: dict) -> Optional[DocumentModel]:
    """更新文档解析内容"""
    document = db.query(DocumentModel).filter(DocumentModel.document_id == document_id).first()
    
    if not document:
        return None
    
    document.parsed_content = parsed_content
    document.document_metadata = metadata
    document.updated_at = datetime.now()
    
    db.commit()
    db.refresh(document)
    return document