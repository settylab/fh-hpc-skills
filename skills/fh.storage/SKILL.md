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

1. **Active scientific data — durable home** (notebooks, manuscripts, derived figures, code, lab-curated data, analysis outputs you'll cite): Use **Fast** (`/fh/fast/`). Daily backup + offsite replication. Performance is fine for typical analytical I/O but `/fh/fast/` is not the bulk-throughput winner — see `fh.storage-fast` and `fh.storage-scratch` for the per-metric picture.

2. **Bulk sequential reads** (loading a large matrix, alignment input, model checkpoint): Use **Temp** (`/hpc/temp/`). Per the Apr-2026 weekly benchmark (n=28), `/hpc/temp/` median read is 565 MiB/s vs 335 (`fast`) and 416 (`working`), and is the only NFS tier whose seq-read throughput is **insulated from cluster load** (Spearman ρ ≈ 0 across 0.44–0.90 cluster load). 30-day purge from creation date — never use as primary copy.

3. **Bulk writes and metadata-heavy work** (large file writes, many small files, build trees, conda envs): Use **Working** (`/fh/working/`). Median write 278 MiB/s and metadata 4.0 s/1000 files both beat the other NFS tiers. Caveat: `/fh/working/` is the most load-sensitive on bulk reads (ρ = −0.60, p = 7×10⁻⁴) — degrades visibly under heavy cluster load. No automatic purge but no backup guarantee.

4. **Job-local scratch on a compute node** (`$TMPDIR`, `/tmp`, `$SCRATCH_LOCAL`): conditional on node class. `gizmok*` nodes have ~2 GiB/s NVMe scratch and beat every NFS tier. `gizmoj*` nodes are ~10× slower across all metrics — staging *for random reads* on a `j` node is a net loss. See `fh.storage-scratch` "Per-node variance" for the cohort caveat.

5. **In-memory tmpfs** (`/dev/shm/`): Beats every disk-backed tier by 5×–100×. Counts against the job's `--mem` allocation; size accordingly.

6. **Large archival datasets** or data you access infrequently: Use **Economy/S3** (`fh-pi-lastname-f-eco`). Cheapest per-TB, auto-tiered.

7. **PHI or PII data**: Use **Secure** (`/fh/secure/`) for POSIX access, or **Economy/S3** for object storage. Both support encryption at rest + access auditing.

8. **Documents and collaboration**: Use **OneDrive** for non-scientific files. 2TB per user, real-time collaboration.

Empirical baseline for items 2–4: `docs/benchmarks/storage_performance.md` and `docs/benchmarks/weekly_summary.tsv`. Median+IQR across 28 Slurm runs on 21 distinct gizmo nodes, Apr 2026.

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
