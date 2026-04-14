# Object Storage (AWS S3 / Economy)

Source: https://sciwiki.fredhutch.org/scicomputing/store_objectstore/

## Overview

AWS S3 object storage offers superior scalability and cost-efficiency compared to POSIX file storage. Not mountable as a filesystem; requires specialized tools.

## Managed S3 Buckets

Each PI receives managed buckets with naming convention:
- Private: `fh-pi-lastname-f-eco`
- Public: `fh-pi-lastname-f-eco-public`
- Scratch: `fh-pi-lastname-f-nextflow-scratch`

## Access Tools

| Tool | Use Case |
|------|----------|
| AWS CLI (`aws s3`) | Command-line operations, scripting |
| Mountain Duck / CyberDuck | Desktop GUI access |
| Motuz | Web-based transfers between storage tiers |
| Python `boto3` | Programmatic access from Python |
| R `aws.s3` | Programmatic access from R |
| `rclone` | Flexible CLI for cloud storage sync |

## Scratch Bucket Auto-Deletion

Objects placed in these prefixes are automatically deleted:
- `delete10/` -- deleted after 10 days
- `delete30/` -- deleted after 30 days
- `delete60/` -- default deletion period (60 days)

Deletion is based on object creation date, not last access.

## Data Sharing Methods

1. **Direct bucket access**: Grant read, write, or read-write permissions to collaborators
2. **Pre-signed URLs**: Temporary, single-file access links
3. **Public access**: IP-restricted or unrestricted
4. **Cross-AWS account access**: For collaborators with their own AWS accounts

## Key Policies

- Data versioning retained for 60 days after deletion (recovery possible)
- Intelligent Tiering enabled by default (automatic cost optimization)
- Encrypted at rest; appropriate for PHI
- Bulk transfers between S3 buckets: 30-40TB/hour capacity
- External collaborator access expires annually by default

## Administrator Capabilities

Data Managers/Admins can:
- Recover deleted objects (within 60-day versioning window)
- Initiate Glacier retrievals
- Manage permissions beyond standard user restrictions

## Quotas

- 100TB free per PI
- Costs apply beyond 100TB
