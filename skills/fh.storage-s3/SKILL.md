---
description: "Using Economy storage (AWS S3) for archival, large datasets, and PHI at Fred Hutch"
---

# Economy Storage (AWS S3)

TRIGGER when: user asks about S3 storage, economy storage, object storage, aws s3, archiving data, large dataset storage, boto3, rclone, or data sharing via S3

## Context

Economy storage uses AWS S3 for scalable, cost-effective storage of large datasets and archives. Each PI receives 100TB free. It supports PHI through encryption at rest and access auditing. Data is not mountable as a filesystem; it requires specialized tools.

## Managed Buckets

Each PI receives these managed S3 buckets:

| Bucket | Naming Convention | Purpose |
|--------|-------------------|---------|
| Private | `fh-pi-lastname-f-eco` | Primary economy storage |
| Public | `fh-pi-lastname-f-eco-public` | Publicly accessible data |
| Scratch | `fh-pi-lastname-f-nextflow-scratch` | Temporary pipeline scratch |

## Access Tools

### AWS CLI (recommended for scripting)
```bash
# List bucket contents
aws s3 ls s3://fh-pi-lastname-f-eco/

# Copy file to S3
aws s3 cp local_file.bam s3://fh-pi-lastname-f-eco/data/

# Sync a directory
aws s3 sync /fh/fast/lastname_f/user/me/project/ s3://fh-pi-lastname-f-eco/project/

# Download from S3
aws s3 cp s3://fh-pi-lastname-f-eco/data/file.bam ./
```

### Python (boto3)
```python
import boto3
s3 = boto3.client('s3')
s3.download_file('fh-pi-lastname-f-eco', 'data/file.bam', 'local_file.bam')
s3.upload_file('local_file.bam', 'fh-pi-lastname-f-eco', 'data/file.bam')
```

### R (aws.s3)
```r
library(aws.s3)
save_object("data/file.csv", bucket = "fh-pi-lastname-f-eco", file = "local.csv")
put_object("local.csv", object = "data/file.csv", bucket = "fh-pi-lastname-f-eco")
```

### Other Tools
- **Motuz**: Web-based transfers between Fred Hutch storage tiers and S3
- **Mountain Duck / CyberDuck**: Desktop GUI for browsing S3 buckets
- **rclone**: Flexible CLI for cloud sync operations

## Scratch Bucket Auto-Deletion

Objects in these prefixes are automatically deleted:

| Prefix | Retention |
|--------|-----------|
| `delete10/` | 10 days |
| `delete30/` | 30 days |
| `delete60/` | 60 days (default) |

Deletion is based on object creation date, not last access.

## Data Sharing

1. **Direct bucket access**: Grant read, write, or read-write to collaborators
2. **Pre-signed URLs**: Temporary single-file access links (time-limited)
3. **Public access**: IP-restricted or unrestricted
4. **Cross-AWS account**: For collaborators with their own AWS accounts
5. External collaborator access expires annually by default

## Key Policies

- **Versioning**: Deleted objects recoverable for 60 days
- **Intelligent Tiering**: Enabled by default (automatic cost optimization)
- **Encryption**: At rest, appropriate for PHI
- **Bulk transfer speed**: 30-40TB/hour between S3 buckets
- **Quota**: 100TB free per PI, costs beyond that

## Administrator Capabilities

Data Managers/Admins can:
- Recover deleted objects within the 60-day versioning window
- Initiate Glacier retrievals for archived data
- Manage permissions beyond standard user restrictions

## Instructions

When helping users with Economy/S3 storage:

1. Confirm the PI bucket name follows `fh-pi-lastname-f-eco` convention
2. Recommend `aws s3` CLI for scripting, Motuz for web-based transfers
3. For PHI data, confirm Economy/S3 is approved (encryption + auditing)
4. Warn about scratch bucket auto-deletion policies
5. For data sharing, recommend pre-signed URLs for temporary access
6. Remind users that S3 is not a filesystem (no `cd`, `ls` as usual)

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_objectstore/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_overview/
