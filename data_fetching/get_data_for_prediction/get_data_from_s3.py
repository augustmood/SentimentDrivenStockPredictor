import boto3
import os

def download_s3_bucket(bucket_name, local_directory):
    """
    Download the contents of an entire S3 bucket to a local directory.
    
    :param bucket_name: The name of the S3 bucket.
    :param local_directory: The local directory to which the bucket's contents will be downloaded.
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name):
        if "Contents" in result:
            for obj in result['Contents']:
                # Define the local file path where the file will be saved
                local_file_path = os.path.join(local_directory, obj['Key'])
                # Ensure the local directory structure exists
                local_file_directory = os.path.dirname(local_file_path)
                if not os.path.exists(local_file_directory):
                    os.makedirs(local_file_directory)
                # Download the file from S3 to the specified local path
                s3.download_file(bucket_name, obj['Key'], local_file_path)
                print(f"Downloaded {obj['Key']} to {local_file_path}")

# Example usage
bucket_name = '733-project-new-data'
local_directory = './input_data/'
download_s3_bucket(bucket_name, local_directory)