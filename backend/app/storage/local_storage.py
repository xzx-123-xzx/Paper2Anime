import os
import shutil
from typing import Optional, Dict, Any

from common.logger import my_logger as logger
from common.config import Config

class LocalStorage:
    """本地存储"""
    
    def __init__(self, base_path: str = None):
        conf = Config()
        self.base_path = base_path or conf.LOCAL_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)
    
    def save(self, file_content: bytes, relative_path: str) -> str:
        """保存文件"""
        full_path = os.path.join(self.base_path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"文件保存: {full_path}")
        return full_path
    
    def get(self, relative_path: str) -> Optional[bytes]:
        """读取文件"""
        full_path = os.path.join(self.base_path, relative_path)
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                return f.read()
        return None
    
    def delete(self, relative_path: str) -> bool:
        """删除文件"""
        full_path = os.path.join(self.base_path, relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"文件删除: {full_path}")
            return True
        return False
    
    def get_url(self, relative_path: str) -> str:
        """获取文件 URL"""
        return f"/files/{relative_path}"
    
    def exists(self, relative_path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(os.path.join(self.base_path, relative_path))
    
    def list(self, relative_path: str = "") -> list:
        """列出目录下的文件"""
        full_path = os.path.join(self.base_path, relative_path)
        if os.path.exists(full_path):
            return os.listdir(full_path)
        return []
    
    def copy(self, src: str, dst: str) -> str:
        """复制文件"""
        src_path = os.path.join(self.base_path, src)
        dst_path = os.path.join(self.base_path, dst)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        return dst_path