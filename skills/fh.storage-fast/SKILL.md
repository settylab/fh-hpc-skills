---
description: "Using /fh/fast/ POSIX storage for scientific data at Fred Hutch"
---

# Fast Storage (/fh/fast/)

TRIGGER when: user asks about /fh/fast/, fast storage, scientific file storage, POSIX storage, lab storage, collaboration folders, or file permissions on the cluster

## Context

Fast storage is the primary high-performance POSIX filesystem for active scientific data at Fred Hutch. Each PI receives 5TB free, with additional capacity available at cost. Data is backed up daily with offsite replication.

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
| Performance | Good sequential throughput via NFS; for random I/O-heavy workloads, stage to `$TMPDIR` or `/dev/shm` |

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_posix/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_overview/
