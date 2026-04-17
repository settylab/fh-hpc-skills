---
description: "Overview of Fred Hutch storage tiers: home, fast, /hpc/temp, economy/S3, working, and secure"
---

# Fred Hutch Data Storage Overview

TRIGGER when: user asks about storage options, where to store data, storage tiers, data management strategy, or which storage to use at Fred Hutch

## Context

Fred Hutch provides multiple storage tiers optimized for different use cases. Choosing the right tier depends on data size, performance needs, durability requirements, security classification, and cost.

## Storage Tiers at a Glance

| Tier | Path / Access | Free Quota | Backup | PHI OK | Best For |
|------|--------------|------------|--------|--------|----------|
| Home | `/home/HUTCHID` | 100GB (hard) | 7-day snapshots + offsite | No | Shell configs, personal files |
| Fast | `/fh/fast/lastname_f/` | 5TB per PI | Daily + offsite | No | Active scientific data, instrument output |
| Working | `/fh/working/lastname_f/` | 20TB | Snapshots only | No | Secondary working copies |
| Temp | `/hpc/temp` | Unlimited | None | No | Intermediate job files (30-day purge) |
| Secure | `/fh/secure/lastname_f/` | 750GB per PI | Yes (audited) | Yes | PII, access-audited data |
| Economy (S3) | `fh-pi-lastname-f-eco` | 100TB per PI | 60-day versioning | Yes | Archival, large datasets, PHI |
| OneDrive | Office 365 | 2TB per user | Cloud multi-DC | Yes | Documents, admin files |

## Decision Guide

1. **Active scientific data** (genomics, imaging, analysis outputs): Use **Fast** (`/fh/fast/`). Best I/O performance, backed up daily.

2. **Large archival datasets** or data you access infrequently: Use **Economy/S3** (`fh-pi-lastname-f-eco`). Cheapest per-TB, auto-tiered.

3. **Temporary intermediate files** from compute jobs: Use **Temp** (`/hpc/temp`) or job-local storage. Free, auto-purged.

4. **Working copies** of data whose primary lives elsewhere: Use **Working** (`/fh/working/`). No backup guarantee.

5. **PHI or PII data**: Use **Secure** (`/fh/secure/`) for POSIX access, or **Economy/S3** for object storage. Both support encryption at rest + access auditing.

6. **Documents and collaboration**: Use **OneDrive** for non-scientific files. 2TB per user, real-time collaboration.

## Security Classification

All tiers encrypt data at rest. Encryption in transit is provided via SMB only; NFS (used on HPC nodes) is unencrypted but confined to the datacenter network.

For PHI, a storage system must provide:
- Encryption at rest
- Encryption in transit
- Access auditing

Approved for PHI: Secure, Economy Cloud (S3), OneDrive.

## Instructions

When advising on storage choice:

1. Ask what kind of data (size, sensitivity, access pattern)
2. Recommend the appropriate tier from the table above
3. Warn if the user is about to put the only copy of data in `/hpc/temp/` (auto-deleted 30 days after creation)
4. For PHI, confirm the chosen system is ISO-approved
5. For large transfers between tiers, suggest Motuz or HutchGO (Globus)

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_overview/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_posix/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_objectstore/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_task/
