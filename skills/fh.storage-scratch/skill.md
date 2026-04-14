---
description: "Using /hpc/temp/ scratch and task-optimized temporary storage at Fred Hutch"
---

# Scratch and Temporary Storage

TRIGGER when: user asks about scratch storage, temp storage, /hpc/temp, temporary files, job-local storage, working storage, or intermediate compute files

## Context

Fred Hutch provides several temporary/task-optimized storage options for intermediate computational data. These are NOT backed up and should NEVER hold the only copy of important data.

**CRITICAL: Do not store the primary or only copy of any dataset in temp or scratch storage. Always ensure a durable copy exists in Fast or Economy/S3.**

## Deprecation Notice

**`/fh/scratch/` is deprecated and no longer mounted.** The environment variables `$SCRATCH`, `$DELETE10`, `$DELETE30`, `$DELETE90` still exist in shell profiles but point to nonexistent paths. Do NOT use them. Use `/hpc/temp/` instead.

## Storage Options

### Temp (`/hpc/temp`) — Primary Scratch

| Property | Value |
|----------|-------|
| Path | `/hpc/temp/<pi_lastname_fi>/<username>/` |
| NFS server | `scratch.chromium.fhcrc.org` (140.107.223.133) |
| Protocol | NFSv4.1, 1MB read/write block size, hard mount |
| Available on | rhino, gizmo nodes, managed workstations |
| Backup | None (snapshots every 30 minutes, ~1hr recovery window) |
| Purge | Files deleted 30 days after creation date |
| Cost | Free |
| Performance | Network-attached; good throughput for sequential I/O, higher latency than local disk |

```bash
# Create a working directory in temp
mkdir -p /hpc/temp/$USER/my_analysis

# Copy input data
cp /fh/fast/lastname_f/user/$USER/input.bam /hpc/temp/$USER/my_analysis/

# Run analysis
# ... your pipeline ...

# Copy results back to durable storage
cp /hpc/temp/$USER/my_analysis/results.tsv /fh/fast/lastname_f/user/$USER/
```

### Working (`/fh/working`)

| Property | Value |
|----------|-------|
| Path | `/fh/working/lastname_f/` |
| Available on | All rhino/gizmo nodes |
| Backup | None (snapshots available) |
| Purge | No automatic purge |
| Quota | 20TB default, expandable to 50TB (at cost) |
| Access | PI/lab researchers only |

Use Working for datasets where a primary copy exists elsewhere (e.g., in Economy/S3) and you need a working copy for active analysis.

### Job-Local Storage (`$SCRATCH_LOCAL`, `$TMPDIR`)

| Property | Value |
|----------|-------|
| Path | `$SCRATCH_LOCAL` → `/loc/scratch`, also `$TMPDIR` |
| Available on | The specific node running your Slurm job |
| Storage type | Directly-attached local disk (SSD/NVMe on newer nodes) |
| Duration | Job lifecycle only — destroyed when job ends |
| Cost | Free |
| Performance | **Fastest I/O** — no network overhead, ideal for random reads, many small files, databases |

Best for single-node jobs that need maximum I/O throughput. Use `$TMPDIR` or `$SCRATCH_LOCAL` within your Slurm job script. Data is irrecoverably destroyed when the job ends.

```bash
#!/bin/bash
#SBATCH --job-name=fast-io
#SBATCH --tmp=100G    # Request 100GB local scratch

# Stage data to local disk for fast I/O
cp /fh/fast/lastname_f/user/$USER/big_index.db $TMPDIR/
# Run with local I/O
my_tool --db $TMPDIR/big_index.db --output $TMPDIR/results/
# Copy results back before job ends
cp -r $TMPDIR/results/ /fh/fast/lastname_f/user/$USER/
```

### In-Memory tmpfs (`/dev/shm`, `/tmp` in jobs)

| Property | Value |
|----------|-------|
| Path | `/dev/shm` (POSIX shared memory), `/tmp` (may be tmpfs in job context) |
| Storage type | RAM-backed filesystem (tmpfs) |
| Capacity | Up to ~378 GB on K-class nodes (shares RAM with your job) |
| Duration | Job lifecycle |
| Cost | Consumes your job's memory allocation |
| Performance | **Absolute fastest** — memory speed, no disk I/O at all |

Use `/dev/shm` for truly I/O-critical temporary data (e.g., sorting, intermediate indexes). Be aware this **consumes your job's memory** — request enough `--mem` to cover both your application and tmpfs usage.

Slurm sets `$TMPDIR` per-job to an isolated temporary directory that is cleaned up automatically when the job exits. Always prefer `$TMPDIR` over hardcoding `/tmp` to avoid collisions with other jobs on the same node.

```bash
#!/bin/bash
#SBATCH --mem=200G   # Must cover app + tmpfs usage

# Use RAM-backed storage for extreme I/O
cp /fh/fast/lastname_f/user/$USER/index.db /dev/shm/
my_tool --db /dev/shm/index.db --output $TMPDIR/results/
cp -r $TMPDIR/results/ /fh/fast/lastname_f/user/$USER/
```

## Performance Comparison

| Storage | Latency | Throughput | Shared | Persists | Capacity |
|---------|---------|------------|--------|----------|----------|
| `/dev/shm` (tmpfs) | ~ns | Memory speed | No (node-local) | Job only | Your `--mem` |
| `$TMPDIR` / `$SCRATCH_LOCAL` | ~us | SSD/NVMe | No (node-local) | Job only | Node disk |
| `/hpc/temp` | ~ms | NFS4 1MB blocks | Yes (cluster-wide) | 30 days | Large |
| `/fh/working` | ~ms | NFS | Yes (cluster-wide) | No purge | 20TB |
| `/fh/fast` | ~ms | NFS 128K/512K | Yes (cluster-wide) | Persistent | PI quota |

### Cloud Scratch (S3)

| Property | Value |
|----------|-------|
| Bucket | `fh-pi-lastname-f-nextflow-scratch` |
| Auto-delete prefixes | `delete10/`, `delete30/`, `delete60/` |
| Cost | Charged |

Deletion is based on object creation date, not last access.

## Instructions

When helping users with temporary storage:

1. Identify the performance and durability needs of the workflow
2. Recommend temp (`/hpc/temp`) for short-lived intermediate files (default choice)
3. Recommend job-local (`$TMPDIR`) for maximum I/O on single-node jobs
4. Recommend Working for longer-lived working copies where a primary exists elsewhere
5. Always remind users to copy results to durable storage (Fast or Economy/S3) when done
6. Suggest workflow managers (Nextflow, Snakemake, Cromwell) for automated staging

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_task/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_posix/
