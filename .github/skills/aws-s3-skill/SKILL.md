---
name: aws-s3-skill
description: Complete guide for AWS S3 operations using the boto3 Python SDK. Covers checking bucket existence, creating buckets with configurable public read/write permissions, uploading files, downloading files, listing objects, deleting objects, and presigned URLs. Use this skill whenever a task involves creating, configuring, or interacting with an S3 bucket.
---

# Instructions

This skill covers all AWS S3 bucket and object operations using the `boto3` Python SDK. Read the documentation file below for complete API usage, permission configuration, and code patterns.

---

## Prerequisite — AWS Credentials Check (Do This First)

Before executing any task from this skill, you **must** verify that AWS credentials are available:

1. Look for a `.env` file (or `.env.example` if `.env` does not exist) in the project root.
2. Check that **all three** of the following variables are defined and have non-empty values:

   ```
   AWS_ACCESS_KEY_ID=<your-access-key>
   AWS_SECRET_ACCESS_KEY=<your-secret-key>
   AWS_DEFAULT_REGION=<your-aws-region>
   ```

3. **If any of these keys are missing or empty, STOP immediately.** Do not proceed with any code generation. Instead, ask the user:

   > "I need AWS credentials to continue. Please add the following to your `.env` file:
   > - `AWS_ACCESS_KEY_ID` — your IAM access key
   > - `AWS_SECRET_ACCESS_KEY` — your IAM secret key
   > - `AWS_DEFAULT_REGION` — your preferred AWS region (e.g., `us-east-1`)
   >
   > You can create these in the AWS IAM Console under Security Credentials. Once they are set, let me know and I'll continue."

4. Once the keys are confirmed present, **always** load them from the environment — never hardcode them:

   ```python
   import os
   import boto3
   from dotenv import load_dotenv

   load_dotenv()

   s3_client = boto3.client(
       "s3",
       aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
       aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
       region_name=os.environ["AWS_DEFAULT_REGION"],
   )
   ```

> **Never** pass raw credential strings in code. All AWS keys must come from environment variables loaded at runtime. This applies to every code example in S3_DOCS.md — override any hardcoded placeholder with `os.environ[...]`.

---

## Documentation Files

### S3_DOCS.md — Complete S3 Operations Guide

**Read this for**: checking if a bucket exists, creating buckets with public/private read/write permissions, configuring bucket policies, uploading files, downloading files, listing objects, deleting objects, generating presigned URLs, and error handling.

**Location**: [.github/skills/aws-s3-skill/documentation/S3_DOCS.md](documentation/S3_DOCS.md)

---

## Quick Decision Guide

| Task | Section in S3_DOCS.md |
|------|-----------------------|
| Check if a bucket exists | Bucket Existence Check |
| Create a private bucket | Create Bucket — Private |
| Create a publicly readable bucket | Create Bucket — Public Read |
| Create a publicly writable bucket | Create Bucket — Public Read/Write |
| Upload a file | Upload Files |
| Upload with public read access | Upload Files — Public Read |
| Download a file | Download Files |
| List objects in a bucket | List Objects |
| Delete an object | Delete Objects |
| Delete a bucket | Delete Bucket |
| Generate a temporary download link | Presigned URLs |
| Error handling | Error Handling |
