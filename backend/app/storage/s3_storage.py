import os
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

from common.logger import my_logger as logger
from common.config import Config

conf = Config()

class S3Storage:
    """S3/MinIO 对象存储"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("S3_ENDPOINT"),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "us-east-1")
        )
        self.bucket = os.getenv("S3_BUCKET", "paper2anime")
    
    def save(self, file_content: bytes, relative_path: str) -> str:
        """保存文件到 S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=relative_path,
                Body=file_content
            )
            logger.info(f"文件上传到 S3: {relative_path}")
            return f"s3://{self.bucket}/{relative_path}"
        except ClientError as e:
            logger.error(f"S3 上传失败: {e}")
            raise
    
    def get(self, relative_path: str) -> Optional[bytes]:
        """从 S3 读取文件"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=relative_path)
            return response["Body"].read()
        except ClientError:
            return None
    
    def delete(self, relative_path: str) -> bool:
        """从 S3 删除文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=relative_path)
            logger.info(f"从 S3 删除: {relative_path}")
            return True
        except ClientError:
            return False
    
    def get_url(self, relative_path: str) -> str:
        """获取文件 URL"""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": relative_path},
                ExpiresIn=3600
            )
            return url
        except ClientError:
            return f"https://{self.bucket}.s3.amazonaws.com/{relative_path}"
    
    def exists(self, relative_path: str) -> bool:
        """检查文件是否存在"""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=relative_path)
            return True
        except ClientError:
            return False
    
    def list(self, prefix: str = "") -> list:
        """列出 S3 下的文件"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError:
            return []