import oss2
from ..config.config import config

class OSSHelper:
    def __init__(self):
        self.config = config['default']
        self.auth = oss2.Auth(
            self.config.OSS_ACCESS_KEY_ID,
            self.config.OSS_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth,
            self.config.OSS_ENDPOINT,
            self.config.OSS_BUCKET_NAME
        )
        
    def upload_file(self, local_file, remote_file):
        """上传文件到OSS"""
        try:
            self.bucket.put_object_from_file(remote_file, local_file)
            return True
        except Exception as e:
            print(f"Upload to OSS failed: {str(e)}")
            return False
            
    def download_file(self, remote_file, local_file):
        """从OSS下载文件"""
        try:
            self.bucket.get_object_to_file(remote_file, local_file)
            return True
        except Exception as e:
            print(f"Download from OSS failed: {str(e)}")
            return False
            
    def delete_file(self, remote_file):
        """删除OSS中的文件"""
        try:
            self.bucket.delete_object(remote_file)
            return True
        except Exception as e:
            print(f"Delete from OSS failed: {str(e)}")
            return False 