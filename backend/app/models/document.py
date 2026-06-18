from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"

class DocumentMetadata(BaseModel):
    file_name: str
    file_type: FileType
    file_size: int
    title: Optional[str] = None
    chapter_count: int = 0

class Document(BaseModel):
    document_id: str = Field(..., description="文档唯一标识")
    user_id: str = Field(..., description="用户ID")
    file_path: str = Field(..., description="文件存储路径")
    metadata: DocumentMetadata
    parsed_content: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DocumentUploadResponse(BaseModel):
    document_id: str
    file_path: str
    status: str = "uploaded"
