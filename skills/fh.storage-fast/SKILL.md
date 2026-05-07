---
description: "Using /fh/fast/ POSIX storage at Fred Hutch — Isilon-backed, daily-backed-up, the durable home for lab data, manuscripts, code, analytical outputs, and long-term scientific files"
---

# Fast Storage (/fh/fast/)

TRIGGER when: user asks about /fh/fast/, fast storage, Isilon, scientific file storage, POSIX storage, lab storage, collaboration folders, file permissions on the cluster, where to put long-term project data, or where backed-up storage lives.

## Context

Fast storage is the primary high-performance POSIX filesystem for active scientific data at Fred Hutch. Each PI receives 5TB free, with additional capacity available at cost. Data is backed up daily with offsite replication.

This is the **durability tier** — the place for any data whose loss would cost more than re-running a job: notebooks, manuscripts, derived figures, lab-curated data, code repos cloned for active work. Performance is fine for typical analytical I/O but `/fh/fast/` is not the bulk-throughput winner (see `fh.storage-scratch` for read-heavy staging and `fh.storage` for the cross-tier decision rules).

## Path Structure

```
/fh/fast/lastname_f/
├── pub/          # Publicly readable, hutch-wide sharing
├── SR/           # Shared Resource data (genomics, compbio)
│   └── ngs/      # Sequencing data auto-deposited here
├── app/          # Group software and binaries
├── grp/          # Lab folder (lastname_f_grp access group)
├── project1/     # Project-specific (lastname_f_project1_grp)
└── user/         # Individual user workspaces
    └── username/
```

PI directories use the naming convention `lastname_f` (last name + first initial, e.g., `smith_s`).

## Access

### Linux / HPC Nodes
```bash
ls /fh/fast/lastname_f/
cd /fh/fast/lastname_f/user/$USER
```

### Windows
- Mapped drive: `X:\fast\lastname_f\`
- UNC path: `\\center.fhcrc.org\fh\fast\lastname_f\`

### Mac (SMB)
```
smb://fhcrc.org;HUTCHID@center.fhcrc.org/fh/fast/lastname_f
```

Disable volume indexing for performance:
```bash
sudo mdutil -a -i off
sudo mdutil -i on /Volumes/mac-name
```

### Access Requirements
- On-campus: wired or Marconi wireless
- Off-campus: VPN required

## Genomics Shared Resource

Sequencing data auto-deposits to `/fh/fast/lastname_f/SR/ngs/`. Do NOT alter permissions on this folder tree or SR cores will be unable to deliver data.

## Collaboration Folders

To share data between labs, email scicomp with:
- Hutchnet IDs of collaborators
- Folder path
- Permission level (read-only or read/write)

Collaboration folders are supported in Fast and Working only.

### Blind Parent Directories

You may have access to a subfolder but not the parent directory listing:

```bash
# This fails (no listing permission on parent):
ls -l /fh/fast/pi_a

# This works (direct path):
ls -l /fh/fast/pi_a/collaboration

# SMB mount the collaboration folder directly:
# smb://center.fhcrc.org/fh/fast/pi_a/collaboration
```

## Instructions

When helping users with fast storage:

1. Confirm the PI directory name (`lastname_f` convention)
2. Point users to the appropriate subfolder (`user/` for personal, `grp/` for shared lab, `project*/` for projects)
3. Warn about altering SR directory permissions
4. For cross-lab sharing, direct them to email scicomp
5. For large data transfers, suggest Motuz (web-based) or HutchGO (Globus)

## Infrastructure Details

| Property | Value |
|----------|-------|
| NFS server | `silver` (Isilon cluster) |
| Protocol | NFSv3, 128KB read / 512KB write block size, hard mount |
| Quota | 5TB free per PI, expandable at cost |
| Backup | Daily on-campus + offsite replication |
| Snapshots | Available for quick recovery |
| PHI | **NOT approved** (no access auditing); use Secure or Economy/S3 |
| Physical location | On-premise data center, low-latency from gizmo nodes |
| Performance | Median sequential read 335 MiB/s [IQR 284–357], write 223 MiB/s [204–234], metadata 4.6 s/1000 files [4.4–4.9], random 4 KiB reads 2933 ops/s [2768–3045]. n=28 weekly fleet runs across 21 distinct gizmo nodes, Apr 2026. For random I/O-heavy workloads, stage to `$TMPDIR` (caveat: only fast on `gizmok*` nodes — see `fh.storage-scratch`) or `/dev/shm`. |

### Performance under cluster load

Per the Apr-2026 weekly benchmark (n=28 Slurm runs, cluster load 0.44–0.90), `/fh/fast/` sequential write throughput correlates negatively with cluster load (Spearman ρ = −0.43, p = 0.023). Expect ~20–25 % degradation at peak vs the 70 %-loaded baseline. Sequential read shows the same direction more weakly (ρ = −0.37, p = 0.050). Metadata and random-read ops/s are not load-correlated.

Implication: bulk-write batch jobs land best when the cluster is in the lower half of its busy band. For agents writing many GiB to `/fh/fast/`, check `hitparade` or `sshare`-derived load before committing — if you have flexibility, the queue gap-fill window after midnight historically shows lower load. The exact slope is inside the 0.44–0.90 load range observed; behaviour at lower loads is unmeasured.

Full data: `docs/benchmarks/storage_performance.md` and `docs/benchmarks/weekly_summary.tsv` in this repo.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_posix/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_overview/
