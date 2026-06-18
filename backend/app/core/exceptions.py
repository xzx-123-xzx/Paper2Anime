from fastapi import HTTPException, status

class DocumentUploadError(HTTPException):
    def __init__(self, detail: str = "文档上传失败"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnsupportedFileTypeError(HTTPException):
    def __init__(self, detail: str = "不支持的文件格式"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class FileTooLargeError(HTTPException):
    def __init__(self, detail: str = "文件大小超限"):
        super().__init__(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=detail)

class ProjectNotFoundError(HTTPException):
    def __init__(self, detail: str = "项目不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class WorkflowError(HTTPException):
    def __init__(self, detail: str = "工作流执行失败"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class LLMCallError(HTTPException):
    def __init__(self, detail: str = "LLM 调用失败"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class MediaGenerationError(HTTPException):
    def __init__(self, detail: str = "媒体生成失败"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class VideoMergeError(HTTPException):
    def __init__(self, detail: str = "视频合成失败"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
