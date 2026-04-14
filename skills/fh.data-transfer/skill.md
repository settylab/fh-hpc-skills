---
description: "Moving data in and out of Fred Hutch storage (Motuz, Globus, S3, Aspera) including migration and archival to Economy Cloud"
---

# Data Transfer at Fred Hutch

TRIGGER when: user mentions data transfer, uploading data, downloading data, Motuz, Globus, Aspera, moving files to/from S3, large file transfers, data migration, Economy Cloud, archiving data from fast, or freeing up storage space.

## Context

Fred Hutch provides multiple tools for transferring data between local storage, cloud (S3), and external sources. The right tool depends on source, destination, data size, and security requirements.

## Storage Tiers

| Storage | Mount Point | Backed Up | Purpose |
|---------|------------|-----------|---------|
| Fast File | `/fh/fast/<pi>/` | Yes | Primary research data (active projects) |
| Temp | `/hpc/temp/` | No | Working space for compute jobs |
| Economy Cloud | S3 buckets | Yes | Long-term archival, cost-effective |

Economy Cloud buckets are named `fh-pi-<lastname>-<initial>-eco` (private) and `fh-pi-<lastname>-<initial>-eco-public` (public).

## Instructions

### Tool Selection Guide

| Scenario | Tool |
|----------|------|
| Campus storage to/from S3 (web UI) | Motuz |
| Large transfers between institutions | Globus |
| AWS S3 from command line | AWS CLI |
| S3 from Windows/Mac GUI | Mountain Duck / Cyberduck |
| Genomics data portals (NCBI, EBI) | Aspera |
| Large external datasets for staging | wget to /hpc/temp, then aws s3 sync |

### Motuz (Web Transfer)

Access at https://motuz.fredhutch.org (campus/VPN required). Supports campus filesystems, S3, Azure, Google Cloud, SFTP, and more.

AWS S3 setup:
1. Get credentials from AWS SSO Portal
2. In Motuz: Cloud Connections > New Connection > S3 (STS credentials)
3. Enter bucket name (format: `fh-pi-lastname-initial-eco`)

If "md5 hash differ" errors occur: add KMS Encryption key ARN from bucket properties.

**Important:** Motuz copies but does NOT delete source files. This is a safety feature. After confirming a transfer completed successfully, manually delete source files if you want to reclaim space.

### AWS CLI

```bash
ml awscli
aws sso login

# Upload
aws s3 cp file.txt s3://fh-pi-doe-j-eco/path/

# Download
aws s3 cp s3://fh-pi-doe-j-eco/path/file.txt .

# Sync directory
aws s3 sync localdir/ s3://fh-pi-doe-j-eco/remotedir/

# Cross-lab transfer (ACL required)
aws s3 cp --acl bucket-owner-full-control file.txt s3://fh-pi-other-lab-eco/
```

### Globus Connect Personal

```bash
ml GlobusConnectPersonal
globusconnect -setup --no-gui   # first time
nohup globusconnect -start &    # run in tmux/screen
```

Configure paths in `~/.globusonline/lta/config-paths`:
```
~/,0,1
/fh/fast/lastname_f,0,1
```

Manage transfers at https://app.globus.org/.

### Ingesting Large External Datasets

```bash
cd /hpc/temp/lastname_f/
mkdir data_staging
wget --recursive --no-clobber ftp://source.example.org/data/
aws s3 sync data_staging/ s3://fh-pi-doe-j-eco/imported_data/
rm -rf data_staging  # after verification
```

Never download large temporary data directly into `/fh/fast`.

### Migrating Data to Economy Cloud

For archiving data from Fast File to Economy Cloud:

1. **Obtain AWS Credentials** -- Get credentials configured for S3 Economy Cloud access (see fh.credentials skill or contact SciComp)
2. **Connect to Campus Network** -- Must be on campus WiFi or connected via VPN
3. **Transfer via Motuz or AWS CLI** -- Use the methods above to copy data to your `fh-pi-<lastname>-<initial>-eco` bucket
4. **Verify and Clean Up** -- Confirm the transfer completed successfully, then manually delete source files to reclaim space

Economy Cloud has different access patterns than Fast File (S3 API, not POSIX). Keep actively used data on Fast File for POSIX access from rhino/gizmo.

### File Snapshots (Recovery)

Every directory has a `.snapshot` subdirectory for recovering deleted files:
```bash
ls .snapshot                    # list available snapshots
cp -avr .snapshot/daily.2024_01_15_0010/deleted_file .
```

### Pre-Signed URLs (Temporary Sharing)

For non-sensitive data only (NO PHI/PII). Maximum 7 days validity. Generate via AWS Console, CLI, or SDK.

## Principles

- Always verify transfer integrity before deleting any source data
- Use Economy Cloud for data you need to retain but do not actively access
- Data in Temp is NOT backed up; migrate important results to Fast or Economy Cloud
- NEVER expose credentials or share AWS access keys
- NEVER make PHI/PII data publicly accessible
- Follow Fred Hutch data security policies

## References

- SciComp Wiki Motuz: https://sciwiki.fredhutch.org/compdemos/motuz/
- SciComp Wiki Globus: https://sciwiki.fredhutch.org/compdemos/globus-personal/
- SciComp Wiki AWS S3: https://sciwiki.fredhutch.org/compdemos/aws-s3/
- SciComp Wiki Snapshots: https://sciwiki.fredhutch.org/compdemos/snapshots/
- SciComp Wiki Large Data Ingestion: https://sciwiki.fredhutch.org/compdemos/ingest-Large-Data/
- Migration pathway: https://sciwiki.fredhutch.org/pathways/path-migrating-data-from-fast-to-cloud/
- AWS credentials: https://sciwiki.fredhutch.org/scicomputing/access_credentials/
- Object storage: https://sciwiki.fredhutch.org/scicomputing/store_objectstore/
