# In app/services/s3_export.py
import os
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional

def export_to_s3(file_path: str, bucket_name: str, key: str = "", 
                 create_bucket: bool = True, access_key: str = None, 
                 secret_key: str = None, region: str = None) -> Dict[str, str]:
    """
    Export a dataset to AWS S3
    
    Args:
        file_path: Path to the JSON file to export
        bucket_name: Name of the S3 bucket
        key: Optional key name for the file in S3 (path/to/file.json)
        create_bucket: Whether to create the bucket if it doesn't exist
        access_key: AWS access key (defaults to environment variable)
        secret_key: AWS secret key (defaults to environment variable)
        region: AWS region (defaults to environment variable)
        
    Returns:
        Dictionary with the S3 path of the exported file
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Use provided credentials or environment variables
        access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        region = region or os.environ.get('AWS_DEFAULT_REGION')
        
        if not access_key or not secret_key:
            raise ValueError("AWS credentials not provided and not found in environment variables")
        
        # Set up S3 client
        s3_args = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key
        }
        
        if region:
            s3_args['region_name'] = region
            
        s3_client = boto3.client('s3', **s3_args)
        
        # Create key name if not provided
        if not key:
            key = os.path.basename(file_path)
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404' and create_bucket:
                # If bucket doesn't exist and create_bucket is True, create it
                try:
                    if region and region != 'us-east-1':
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    else:
                        s3_client.create_bucket(Bucket=bucket_name)
                    print(f"Bucket {bucket_name} created successfully")
                except ClientError as create_error:
                    raise ValueError(f"Failed to create bucket: {str(create_error)}")
            else:
                # If there's another error or create_bucket is False
                if error_code == '404':
                    raise ValueError(f"Bucket {bucket_name} does not exist and create_bucket is False")
                else:
                    raise ValueError(f"Error accessing bucket: {str(e)}")
        
        # Upload file to S3 using upload_file method
        try:
            s3_client.upload_file(
                file_path, 
                bucket_name, 
                key,
                ExtraArgs={'ContentType': 'application/json'}
            )
        except ClientError as e:
            raise ValueError(f"Error uploading file to S3: {str(e)}")
        
        s3_path = f"s3://{bucket_name}/{key}"
        print(f"File successfully uploaded to {s3_path}")
        
        return {'s3': s3_path}
    
    except Exception as e:
        error_msg = f"Error exporting to S3: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)