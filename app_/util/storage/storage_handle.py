import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
import os
from typing import Optional, List, Dict
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class R2Storage:
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None
    ):
        """
        Initialize R2 Storage Client
        
        Args:
            endpoint_url: R2 endpoint URL (e.g., https://<ACCOUNT_ID>.r2.cloudflarestorage.com)
            access_key_id: R2 Access Key ID
            secret_access_key: R2 Secret Access Key
            bucket_name: Default bucket name to use
        """
        self.endpoint_url = endpoint_url or os.getenv('R2_ENDPOINT_URL')
        self.access_key_id = access_key_id or os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = secret_access_key or os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = bucket_name or os.getenv('R2_BUCKET_NAME', 'my-bucket')
        
        self._validate_credentials()
        self.client = self._create_client()
        logger.info("R2 Storage client initialized successfully")
    
    def _validate_credentials(self):
        """Validate that all required credentials are present"""
        missing = []
        if not self.endpoint_url:
            missing.append('R2_ENDPOINT_URL')
        if not self.access_key_id:
            missing.append('R2_ACCESS_KEY_ID')
        if not self.secret_access_key:
            missing.append('R2_SECRET_ACCESS_KEY')
        
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
    
    def _create_client(self):
        """Create and return the R2 S3 client"""
        return boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
    
    def upload_file(
        self, 
        file_path: str, 
        object_name: str, 
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Upload a file to R2
        
        Args:
            file_path: Local file path
            object_name: Name to store the file as in R2
            bucket_name: Bucket name (uses default if not provided)
        
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.upload_file(file_path, bucket, object_name)
            logger.info(f"Uploaded {file_path} to {bucket}/{object_name}")
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            return False
        except NoCredentialsError:
            logger.error("Invalid credentials")
            return False
    
    def download_file(
        self, 
        object_name: str, 
        file_path: str, 
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Download a file from R2
        
        Args:
            object_name: Name of the file in R2
            file_path: Local path to save the file
            bucket_name: Bucket name (uses default if not provided)
        
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.download_file(bucket, object_name, file_path)
            logger.info(f"Downloaded {bucket}/{object_name} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def list_objects(
        self, 
        bucket_name: Optional[str] = None, 
        prefix: Optional[str] = None
    ) -> List[Dict]:
        """
        List objects in a bucket
        
        Args:
            bucket_name: Bucket name (uses default if not provided)
            prefix: Optional prefix to filter objects
        
        Returns:
            List of object dictionaries
        """
        bucket = bucket_name or self.bucket_name
        try:
            params = {'Bucket': bucket}
            if prefix:
                params['Prefix'] = prefix
            
            response = self.client.list_objects_v2(**params)
            objects = response.get('Contents', [])
            logger.info(f"Found {len(objects)} objects in {bucket}")
            return objects
        except ClientError as e:
            logger.error(f"List objects failed: {e}")
            return []
    
    def delete_object(
        self, 
        object_name: str, 
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Delete an object from R2
        
        Args:
            object_name: Name of the file in R2
            bucket_name: Bucket name (uses default if not provided)
        
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.delete_object(Bucket=bucket, Key=object_name)
            logger.info(f"Deleted {bucket}/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def get_object(
        self, 
        object_name: str, 
        bucket_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Get object content as bytes
        
        Args:
            object_name: Name of the file in R2
            bucket_name: Bucket name (uses default if not provided)
        
        Returns:
            bytes: File content or None if failed
        """
        bucket = bucket_name or self.bucket_name
        try:
            response = self.client.get_object(Bucket=bucket, Key=object_name)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Get object failed: {e}")
            return None
    
    def put_object(
        self, 
        data: bytes, 
        object_name: str, 
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Upload bytes directly to R2 (without saving to disk first)
        
        Args:
            data: Bytes to upload
            object_name: Name to store the file as in R2
            bucket_name: Bucket name (uses default if not provided)
            content_type: MIME type of the content
        
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        try:
            params = {
                'Bucket': bucket,
                'Key': object_name,
                'Body': data
            }
            if content_type:
                params['ContentType'] = content_type
            
            self.client.put_object(**params)
            logger.info(f"Uploaded {object_name} to {bucket}")
            return True
        except ClientError as e:
            logger.error(f"Put object failed: {e}")
            return False
    
    def object_exists(
        self, 
        object_name: str, 
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Check if an object exists in the bucket
        
        Args:
            object_name: Name of the file in R2
            bucket_name: Bucket name (uses default if not provided)
        
        Returns:
            bool: True if exists, False otherwise
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.head_object(Bucket=bucket, Key=object_name)
            return True
        except ClientError:
            return False