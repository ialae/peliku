# AWS S3 Operations — Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Client Initialization](#client-initialization)
4. [Bucket Existence Check](#bucket-existence-check)
5. [Create Bucket](#create-bucket)
6. [Bucket Permission Configurations](#bucket-permission-configurations)
7. [Upload Files](#upload-files)
8. [Download Files](#download-files)
9. [List Objects](#list-objects)
10. [Delete Objects](#delete-objects)
11. [Delete Bucket](#delete-bucket)
12. [Presigned URLs](#presigned-urls)
13. [Error Handling](#error-handling)
14. [Best Practices](#best-practices)
15. [Quick Reference](#quick-reference)

---

## Overview

Amazon S3 (Simple Storage Service) stores objects (files) inside buckets (containers). Every bucket name is globally unique across all AWS accounts. This guide uses the `boto3` SDK to manage buckets and objects programmatically.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Bucket** | A top-level container for objects. Name must be globally unique, 3-63 characters, lowercase, no underscores. |
| **Object** | A file stored in a bucket, identified by a key (path). |
| **Key** | The unique identifier (path) for an object within a bucket (e.g., `uploads/photo.jpg`). |
| **Region** | The AWS data center location where the bucket is physically stored. |
| **ACL** | Access Control List — legacy per-object/per-bucket permission model. |
| **Bucket Policy** | JSON policy document that defines fine-grained access rules for a bucket. |
| **Block Public Access** | Account/bucket-level safety net that overrides ACLs and policies to prevent public exposure. |

---

## Installation & Setup

### Required Packages

```bash
pip install boto3 python-dotenv
```

### Required Environment Variables

These must be present in your `.env` file before any S3 operation:

```
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_DEFAULT_REGION=<your-aws-region>
```

---

## Client Initialization

Always load credentials from environment variables. Never hardcode them.

```python
import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def create_s3_client() -> boto3.client:
    """Create and return an authenticated S3 client."""
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_DEFAULT_REGION"],
    )


def create_s3_resource() -> boto3.resource:
    """Create and return an authenticated S3 resource (high-level API)."""
    return boto3.resource(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_DEFAULT_REGION"],
    )
```

> Use the **client** for low-level operations and fine-grained control. Use the **resource** for simpler, high-level operations.

---

## Bucket Existence Check

Always check if a bucket exists before attempting to create it.

```python
from botocore.exceptions import ClientError


def bucket_exists(s3_client: boto3.client, bucket_name: str) -> bool:
    """Check if an S3 bucket exists and is accessible.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Name of the bucket to check.

    Returns:
        True if the bucket exists and is accessible, False otherwise.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as error:
        error_code = int(error.response["Error"]["Code"])
        if error_code == 404:
            return False
        if error_code == 403:
            raise PermissionError(
                f"Bucket '{bucket_name}' exists but you do not have access to it."
            ) from error
        raise
```

### Usage

```python
s3_client = create_s3_client()

if bucket_exists(s3_client, "my-app-uploads"):
    print("Bucket already exists.")
else:
    print("Bucket does not exist — creating it now.")
```

---

## Create Bucket

### Private Bucket (Default — Recommended)

This is the most secure configuration. No public access is allowed.

```python
def create_private_bucket(s3_client: boto3.client, bucket_name: str) -> None:
    """Create a private S3 bucket with all public access blocked.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Globally unique name for the new bucket.
    """
    region = os.environ["AWS_DEFAULT_REGION"]

    if bucket_exists(s3_client, bucket_name):
        print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
        return

    create_config = {}
    if region != "us-east-1":
        create_config["CreateBucketConfiguration"] = {
            "LocationConstraint": region,
        }

    s3_client.create_bucket(Bucket=bucket_name, **create_config)

    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    print(f"Private bucket '{bucket_name}' created successfully.")
```

### Public-Read Bucket

Objects can be read by anyone, but only the owner can write.

```python
import json


def create_public_read_bucket(s3_client: boto3.client, bucket_name: str) -> None:
    """Create an S3 bucket where objects are publicly readable.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Globally unique name for the new bucket.
    """
    region = os.environ["AWS_DEFAULT_REGION"]

    if bucket_exists(s3_client, bucket_name):
        print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
        return

    create_config = {}
    if region != "us-east-1":
        create_config["CreateBucketConfiguration"] = {
            "LocationConstraint": region,
        }

    s3_client.create_bucket(Bucket=bucket_name, **create_config)

    # Disable Block Public Access so the bucket policy can grant public read
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )

    # Apply a bucket policy that allows public read on all objects
    public_read_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            }
        ],
    }

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(public_read_policy),
    )

    print(f"Public-read bucket '{bucket_name}' created successfully.")
```

### Public Read/Write Bucket

> **WARNING**: This configuration allows anyone on the internet to read AND write objects. Only use this for explicitly public, non-sensitive data (e.g., a temporary upload target behind your own auth layer). In most cases you should use presigned URLs for anonymous uploads instead.

```python
def create_public_read_write_bucket(
    s3_client: boto3.client, bucket_name: str
) -> None:
    """Create an S3 bucket where objects are publicly readable and writable.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Globally unique name for the new bucket.
    """
    region = os.environ["AWS_DEFAULT_REGION"]

    if bucket_exists(s3_client, bucket_name):
        print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
        return

    create_config = {}
    if region != "us-east-1":
        create_config["CreateBucketConfiguration"] = {
            "LocationConstraint": region,
        }

    s3_client.create_bucket(Bucket=bucket_name, **create_config)

    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )

    public_read_write_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
            {
                "Sid": "PublicWritePutObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(public_read_write_policy),
    )

    print(f"Public read/write bucket '{bucket_name}' created successfully.")
```

---

## Bucket Permission Configurations

### Permission Matrix

| Permission Level | Block Public Access | Bucket Policy Actions | Use Case |
|-----------------|--------------------|-----------------------|----------|
| **Private** (default) | All blocked | None | Internal app data, secrets, backups |
| **Public Read** | All unblocked | `s3:GetObject` to `*` | Static websites, public assets, CDN origin |
| **Public Read/Write** | All unblocked | `s3:GetObject` + `s3:PutObject` to `*` | Open upload targets (use with extreme caution) |

### Change an Existing Bucket to Private

```python
def make_bucket_private(s3_client: boto3.client, bucket_name: str) -> None:
    """Lock down an existing bucket to fully private access.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Name of the bucket to make private.
    """
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    # Remove any existing bucket policy
    try:
        s3_client.delete_bucket_policy(Bucket=bucket_name)
    except ClientError:
        pass  # No policy existed

    print(f"Bucket '{bucket_name}' is now fully private.")
```

### Change an Existing Bucket to Public Read

```python
def make_bucket_public_read(s3_client: boto3.client, bucket_name: str) -> None:
    """Change an existing bucket to allow public read access.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Name of the bucket to make publicly readable.
    """
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )

    public_read_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            }
        ],
    }

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(public_read_policy),
    )

    print(f"Bucket '{bucket_name}' is now publicly readable.")
```

---

## Upload Files

### Upload a File (Private — Default)

```python
from pathlib import Path


def upload_file(
    s3_client: boto3.client,
    bucket_name: str,
    file_path: str,
    object_key: str | None = None,
) -> str:
    """Upload a file to an S3 bucket.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Target bucket name.
        file_path: Local path to the file to upload.
        object_key: S3 object key (path in bucket). Defaults to the file name.

    Returns:
        The S3 object key of the uploaded file.
    """
    if object_key is None:
        object_key = Path(file_path).name

    s3_client.upload_file(file_path, bucket_name, object_key)
    print(f"Uploaded '{file_path}' to s3://{bucket_name}/{object_key}")
    return object_key
```

### Upload Bytes / String Content Directly

```python
def upload_content(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
    content: bytes | str,
    content_type: str = "application/octet-stream",
) -> None:
    """Upload raw bytes or string content to S3.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Target bucket name.
        object_key: S3 object key (path in bucket).
        content: The content to upload (bytes or str).
        content_type: MIME type of the content.
    """
    body = content.encode("utf-8") if isinstance(content, str) else content

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=body,
        ContentType=content_type,
    )

    print(f"Uploaded content to s3://{bucket_name}/{object_key}")
```

### Upload with Public Read Access (Per-Object)

Use this when the bucket itself is private but you want a specific object to be publicly readable.

> This requires the bucket's Block Public Access settings to allow ACLs (`BlockPublicAcls: False`, `IgnorePublicAcls: False`), and the bucket must have `ObjectOwnership` set to `BucketOwnerPreferred` or `ObjectWriter`.

```python
def upload_file_public_read(
    s3_client: boto3.client,
    bucket_name: str,
    file_path: str,
    object_key: str | None = None,
) -> str:
    """Upload a file to S3 with public read access on the object.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Target bucket name.
        file_path: Local path to the file to upload.
        object_key: S3 object key. Defaults to the file name.

    Returns:
        The public URL of the uploaded object.
    """
    if object_key is None:
        object_key = Path(file_path).name

    s3_client.upload_file(
        file_path,
        bucket_name,
        object_key,
        ExtraArgs={"ACL": "public-read"},
    )

    region = os.environ["AWS_DEFAULT_REGION"]
    public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"
    print(f"Uploaded (public) '{file_path}' to {public_url}")
    return public_url
```

---

## Download Files

### Download to a Local File

```python
def download_file(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
    destination_path: str,
) -> None:
    """Download an object from S3 to a local file.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Source bucket name.
        object_key: S3 object key to download.
        destination_path: Local file path to save to.
    """
    s3_client.download_file(bucket_name, object_key, destination_path)
    print(f"Downloaded s3://{bucket_name}/{object_key} to '{destination_path}'")
```

### Download as Bytes (In-Memory)

```python
def download_content(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
) -> bytes:
    """Download an object from S3 and return its content as bytes.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Source bucket name.
        object_key: S3 object key to download.

    Returns:
        The object content as bytes.
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read()
    print(f"Downloaded s3://{bucket_name}/{object_key} ({len(content)} bytes)")
    return content
```

---

## List Objects

### List All Objects in a Bucket

```python
def list_objects(
    s3_client: boto3.client,
    bucket_name: str,
    prefix: str = "",
    max_keys: int = 1000,
) -> list[dict]:
    """List objects in an S3 bucket, optionally filtered by prefix.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Bucket to list objects from.
        prefix: Only return objects whose key starts with this prefix.
        max_keys: Maximum number of keys to return per page.

    Returns:
        List of dicts with 'Key', 'Size', and 'LastModified' for each object.
    """
    objects = []
    paginator = s3_client.get_paginator("list_objects_v2")

    page_config = {"Bucket": bucket_name, "MaxKeys": max_keys}
    if prefix:
        page_config["Prefix"] = prefix

    for page in paginator.paginate(**page_config):
        for obj in page.get("Contents", []):
            objects.append({
                "Key": obj["Key"],
                "Size": obj["Size"],
                "LastModified": obj["LastModified"],
            })

    return objects
```

### Usage

```python
s3_client = create_s3_client()

# List all objects
all_objects = list_objects(s3_client, "my-app-uploads")

# List objects under a folder prefix
images = list_objects(s3_client, "my-app-uploads", prefix="images/")

for obj in images:
    print(f"  {obj['Key']}  ({obj['Size']} bytes)")
```

---

## Delete Objects

### Delete a Single Object

```python
def delete_object(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
) -> None:
    """Delete a single object from an S3 bucket.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Bucket containing the object.
        object_key: Key of the object to delete.
    """
    s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    print(f"Deleted s3://{bucket_name}/{object_key}")
```

### Delete Multiple Objects

```python
def delete_objects(
    s3_client: boto3.client,
    bucket_name: str,
    object_keys: list[str],
) -> None:
    """Delete multiple objects from an S3 bucket in a single request.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Bucket containing the objects.
        object_keys: List of object keys to delete (max 1000 per call).
    """
    if not object_keys:
        return

    delete_payload = {"Objects": [{"Key": key} for key in object_keys]}

    response = s3_client.delete_objects(Bucket=bucket_name, Delete=delete_payload)

    deleted_count = len(response.get("Deleted", []))
    error_count = len(response.get("Errors", []))

    print(f"Deleted {deleted_count} objects. Errors: {error_count}.")

    if error_count > 0:
        for err in response["Errors"]:
            print(f"  Failed to delete {err['Key']}: {err['Message']}")
```

---

## Delete Bucket

A bucket must be empty before it can be deleted.

```python
def delete_bucket(s3_client: boto3.client, bucket_name: str) -> None:
    """Delete an S3 bucket after emptying all its objects.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Name of the bucket to delete.
    """
    # First, delete all objects in the bucket
    all_objects = list_objects(s3_client, bucket_name)
    if all_objects:
        all_keys = [obj["Key"] for obj in all_objects]
        # delete_objects handles max 1000 per call, batch if needed
        for i in range(0, len(all_keys), 1000):
            batch = all_keys[i : i + 1000]
            delete_objects(s3_client, bucket_name, batch)

    s3_client.delete_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' deleted successfully.")
```

---

## Presigned URLs

Presigned URLs let you grant temporary access to a private object without changing bucket permissions.

### Generate a Download URL

```python
def generate_download_url(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
    expiration_seconds: int = 3600,
) -> str:
    """Generate a presigned URL for downloading a private object.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Bucket containing the object.
        object_key: Key of the object.
        expiration_seconds: URL validity duration in seconds (default: 1 hour).

    Returns:
        The presigned URL string.
    """
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_key},
        ExpiresIn=expiration_seconds,
    )

    print(f"Presigned download URL (expires in {expiration_seconds}s): {url}")
    return url
```

### Generate an Upload URL

Use this to let external users upload directly to S3 without exposing your credentials.

```python
def generate_upload_url(
    s3_client: boto3.client,
    bucket_name: str,
    object_key: str,
    expiration_seconds: int = 3600,
    content_type: str = "application/octet-stream",
) -> str:
    """Generate a presigned URL for uploading an object.

    Args:
        s3_client: Authenticated boto3 S3 client.
        bucket_name: Target bucket name.
        object_key: Key the uploaded object will have.
        expiration_seconds: URL validity duration in seconds (default: 1 hour).
        content_type: Expected content type of the upload.

    Returns:
        The presigned URL string.
    """
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket_name,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expiration_seconds,
    )

    print(f"Presigned upload URL (expires in {expiration_seconds}s): {url}")
    return url
```

---

## Error Handling

All S3 operations should handle errors using `botocore.exceptions.ClientError`.

```python
from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError


def safe_s3_operation(operation_name: str):
    """Decorator for consistent S3 error handling.

    Args:
        operation_name: Human-readable name of the operation for error messages.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NoCredentialsError as error:
                raise RuntimeError(
                    "AWS credentials not found. Check your .env file for "
                    "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
                ) from error
            except ParamValidationError as error:
                raise ValueError(
                    f"Invalid parameters for {operation_name}: {error}"
                ) from error
            except ClientError as error:
                error_code = error.response["Error"]["Code"]
                error_message = error.response["Error"]["Message"]

                error_map = {
                    "NoSuchBucket": f"Bucket does not exist: {error_message}",
                    "NoSuchKey": f"Object does not exist: {error_message}",
                    "BucketAlreadyExists": f"Bucket name is already taken globally: {error_message}",
                    "BucketAlreadyOwnedByYou": f"You already own this bucket: {error_message}",
                    "AccessDenied": f"Access denied: {error_message}",
                    "InvalidBucketName": f"Invalid bucket name: {error_message}",
                }

                readable_message = error_map.get(
                    error_code,
                    f"S3 {operation_name} failed [{error_code}]: {error_message}",
                )

                raise RuntimeError(readable_message) from error
        return wrapper
    return decorator
```

### Common Error Codes

| Error Code | Cause | Recommended Action |
|-----------|-------|-------------------|
| `NoSuchBucket` | Bucket does not exist | Check bucket name, create it first |
| `NoSuchKey` | Object key not found | Verify the key, list objects to confirm |
| `BucketAlreadyExists` | Another AWS account owns this name | Choose a different bucket name |
| `BucketAlreadyOwnedByYou` | You already created this bucket | Skip creation, proceed |
| `AccessDenied` | IAM policy or bucket policy blocks access | Check IAM permissions and bucket policy |
| `InvalidBucketName` | Name violates S3 naming rules | Use only lowercase, hyphens, 3-63 chars |
| `NoCredentialsError` | boto3 cannot find AWS credentials | Check `.env` for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` |

---

## Best Practices

### Security

- **Default to private.** Only add public access when explicitly required by the task.
- **Prefer presigned URLs** over public bucket policies when external users need temporary access.
- **Never grant public write** unless the task explicitly requires it, and the user has confirmed the risk.
- **Use IAM policies** with least privilege. The access key should only have permissions for the specific buckets it needs.
- **Enable versioning** on buckets that store important data to protect against accidental deletes.

### Naming

- Bucket names must be **globally unique**, **3-63 characters**, **lowercase letters, numbers, and hyphens only**.
- Use a consistent prefix strategy: `{project}-{environment}-{purpose}` (e.g., `myapp-prod-uploads`).
- Object keys should use forward slashes as logical folder separators (e.g., `users/123/avatar.png`).

### Performance

- Use `upload_file` / `download_file` for large files — they handle multipart transfers automatically.
- Use `put_object` / `get_object` for small content or when you need to stream bytes.
- Use pagination (`get_paginator`) when listing buckets with many objects.

### Cost

- Set lifecycle rules to move infrequently accessed data to cheaper storage classes (S3 Glacier, S3-IA).
- Delete objects and buckets when they are no longer needed.
- Use `prefix` filtering in `list_objects` to avoid listing the entire bucket.

---

## Quick Reference

### Complete Workflow — Create Bucket, Upload, Download

```python
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Initialize client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_DEFAULT_REGION"],
)

bucket_name = "myapp-prod-uploads"

# 1. Check and create bucket (private)
if not bucket_exists(s3_client, bucket_name):
    create_private_bucket(s3_client, bucket_name)

# 2. Upload a file
upload_file(s3_client, bucket_name, "local/report.pdf", "reports/2026/report.pdf")

# 3. Upload string content
upload_content(
    s3_client,
    bucket_name,
    "data/config.json",
    '{"version": 1}',
    content_type="application/json",
)

# 4. List objects
objects = list_objects(s3_client, bucket_name, prefix="reports/")
for obj in objects:
    print(f"  {obj['Key']}")

# 5. Download a file
download_file(s3_client, bucket_name, "reports/2026/report.pdf", "downloaded_report.pdf")

# 6. Generate a temporary share link
url = generate_download_url(s3_client, bucket_name, "reports/2026/report.pdf")

# 7. Clean up
delete_object(s3_client, bucket_name, "data/config.json")
```

### Permission Decision Flow

```
Does the task require public access?
├── No  → create_private_bucket()  (default, most secure)
├── Read only → create_public_read_bucket()
├── Read + Write → create_public_read_write_bucket()  (confirm with user first)
└── Temporary access → Keep private + generate_download_url() / generate_upload_url()
```
