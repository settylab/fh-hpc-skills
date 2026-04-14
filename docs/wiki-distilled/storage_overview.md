# Data Storage Overview

Source: https://sciwiki.fredhutch.org/scicomputing/store_overview/

## Storage Tiers

| Resource | Cost | Backup | Best Use | Quota |
|----------|------|--------|----------|-------|
| Home | Free | On-campus + offsite, 7-day snapshots | User settings, configs | 100GB hard limit |
| Fast | Free up to 5TB/PI, $$$ beyond | On-campus + offsite, daily backups | High-performance instrument data | 5TB free per PI |
| Economy Cloud (S3) | Free up to 100TB/PI, $ beyond | Cloud multi-datacenter, 90-day undelete | Archiving, large datasets, PHI | 100TB free per PI |
| Working | Charged over 20TB | On-campus snapshots only | Datasets with durable primary copy | 20TB default |
| Regulated | TBD | On-campus snapshots | Regulated/agreement-covered datasets | TBD |
| HPC/Temp | Free | None | Temporary intermediate files | N/A |
| OneDrive | Free | Cloud multi-datacenter | Administrative files, documents | 2TB per user |

## Security Capabilities

| Feature | Secure | Fast | Economy Cloud | Regulated | Working | HPC/Temp | OneDrive |
|---------|--------|------|---------------|-----------|---------|----------|----------|
| Encryption at Rest | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Access Auditing | Yes | Yes | Yes | No | No | No | Yes |
| PII Approved | Yes | No | Yes | No | No | No | Yes |

Encryption in transit: SMB only. NFS (HPC) is unencrypted but datacenter-confined.

## PHI Data Requirements

Systems storing PHI must support:
1. Encryption at rest
2. Encryption in transit
3. Access auditing (file access logging)

Only ISO-approved systems qualify. De-identified data can use any platform.
Approved for PHI: Secure, Economy Cloud (S3), OneDrive.

## Support Contacts

- General data consulting: email `scicomp`
- Genomics data: email `bioinformatics`
- Data management strategy: Data House Call via `ocdo.fredhutch.org`
- HIPAA compliance: Institutional IRB
- MyDB self-service: `mydb.fredhutch.org/login`
