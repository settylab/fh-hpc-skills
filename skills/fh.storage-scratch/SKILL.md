---
description: "Using /hpc/temp/ scratch and task-optimized temporary storage at Fred Hutch"
---

# Scratch and Temporary Storage

TRIGGER when: user asks about scratch storage, temp storage, /hpc/temp, temporary files, job-local storage, working storage, or intermediate compute files

## Context

Fred Hutch provides several temporary/task-optimized storage options for intermediate computational data. These are NOT backed up and should NEVER hold the only copy of important data.

**CRITICAL: Do not store the primary or only copy of any dataset in temp storage. Always ensure a durable copy exists in Fast or Economy/S3.**

Note: the old network-scratch path `/fh/scratch/delete{10,30,90}/` has been fully decommissioned. `/hpc/temp/` is the sole replacement.

## Storage Options

### Temp (`/hpc/temp`) — Primary Scratch

| Property | Value |
|----------|-------|
| Path | `/hpc/temp/<pi_lastname_f>/<username>/` (Setty Lab: `/hpc/temp/setty_m/$USER/`) |
| NFS server | `scratch.chromium.fhcrc.org` (140.107.223.133) |
| Protocol | NFSv4.1, 1 MiB read/write block size, hard mount |
| Available on | rhino, gizmo nodes, managed workstations |
| Backup | None (snapshots every 30 minutes, ~1hr recovery window) |
| Purge | **30 days from file creation date.** `touch`/access does NOT reset the timer. |
| Cost | Free |
| Performance | Network-attached. Higher sequential read throughput than `/fh/fast/` (larger NFS block), but slower metadata ops — see the benchmark in `docs/benchmarks/` |

```bash
# Create a working directory in temp
mkdir -p /hpc/temp/setty_m/$USER/my_analysis

# Copy input data
cp /fh/fast/setty_m/user/$USER/input.bam /hpc/temp/setty_m/$USER/my_analysis/

# Run analysis
# ... your pipeline ...

# Copy results back to durable storage
cp /hpc/temp/setty_m/$USER/my_analysis/results.tsv /fh/fast/setty_m/user/$USER/
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

Tier-level summary (latency/throughput class):

| Storage | Latency | Throughput class | Shared | Persists | Capacity |
|---------|---------|------------------|--------|----------|----------|
| `/dev/shm` (tmpfs) | ~ns | Memory speed | No (node-local) | Job only | Your `--mem` |
| `$TMPDIR` / `$SCRATCH_LOCAL` | ~us | SSD/NVMe | No (node-local) | Job only | Node disk |
| `/hpc/temp` | ~ms | NFSv4.1, 1 MiB blocks | Yes (cluster-wide) | 30 days | Large |
| `/fh/working` | ~ms | NFSv3, 128 KiB / 512 KiB | Yes (cluster-wide) | No purge | 20 TB |
| `/fh/fast` | ~ms | NFSv3, 128 KiB / 512 KiB | Yes (cluster-wide) | Persistent | PI quota |

Measured on a rhino node (median of 3 reps; full script + caveats: `docs/benchmarks/storage_bench.py`):

| Metric | `/fh/fast` | `/hpc/temp` | `/fh/working` | `/tmp` (NVMe) | `/dev/shm` (tmpfs) |
|---|---|---|---|---|---|
| Sequential write (MiB/s) | 216 | 212 | 245 | 2174 | **2320** |
| Sequential read (MiB/s)  | 395 | 556 | 375 | 1864 | **4408** |
| Metadata (s / 1000 files) | 5.2 | 11.7 | 5.1 | **0.07** | **0.06** |
| Random 4 KiB reads (ops/s) | 2433 | 2025 | 1873 | 7809 | **256 395** |

**Takeaways:**

- `/dev/shm` beats disk by 10× on throughput and 70–100× on metadata/random I/O, but it consumes your Slurm `--mem` allocation.
- Local `/tmp` (NVMe SSD on rhino; on gizmo nodes it is `$TMPDIR` / `$SCRATCH_LOCAL`) is 9× faster than any NFS tier for sequential I/O and ~70× faster on metadata. Use it for I/O-heavy single-node jobs.
- Among NFS tiers, `/hpc/temp` has the best bulk sequential read (1 MiB block size), but ~2× slower metadata than `/fh/fast` or `/fh/working`. For many-small-files workloads, prefer `/fh/fast` or stage to `$TMPDIR`.
- `/fh/working` and `/fh/fast` track very close to each other (same NFS block size, similar Isilon/Osmium backends).

Numbers are single-host, single-run; rerun under your own load before relying on them for capacity planning. See `docs/benchmarks/storage_performance.md` for the full report.

### Cloud Scratch (S3)

| Property | Value |
|----------|-------|
| Bucket | `fh-pi-lastname-f-nextflow-scratch` |
| Auto-delete prefixes | `delete10/`, `delete30/`, `delete60/` |
| Cost | Charged |

Deletion is based on object creation date, not last access.

### Local /tmp Staging Pattern (Copy In, Compute, Copy Out)

For I/O-heavy workloads (genome alignment, variant calling, many intermediate files), stage data to node-local storage to avoid hammering the shared filesystem. This is the single most effective I/O optimization on a shared cluster:

```bash
#!/bin/bash
#SBATCH --tmp=200G   # Reserve local scratch space

# 1. Copy input to local disk
cp /fh/fast/lastname_f/data/sample.bam $TMPDIR/
cp /fh/fast/lastname_f/data/reference.fa* $TMPDIR/

# 2. Run compute entirely on local disk
cd $TMPDIR
samtools sort sample.bam -o sorted.bam -@ $SLURM_CPUS_ON_NODE
samtools index sorted.bam

# 3. Copy results back to durable storage
cp sorted.bam sorted.bam.bai /fh/fast/lastname_f/results/

# Local files are automatically cleaned up when the job ends
```

### I/O Anti-Patterns to Avoid

**Many small files.** Writing thousands of small files to a shared filesystem (per-sample CSVs, per-cell pickle files, one-line-per-file logging) overwhelms metadata servers and degrades performance for every user on the cluster. Aggregate outputs into a single file (HDF5, AnnData, combined TSV) instead.

**Tight open/close loops.** Repeatedly opening and closing a file in a loop (appending one line at a time to a log, writing one record per iteration) generates disproportionate metadata traffic. Buffer writes in memory and flush periodically, or write to a single open file handle:
```python
# Bad: opens and closes the file 10,000 times
for i in range(10000):
    with open("log.txt", "a") as f:
        f.write(f"iteration {i}\n")

# Good: single open, single close
with open("log.txt", "w") as f:
    for i in range(10000):
        f.write(f"iteration {i}\n")
```

**Running I/O-heavy jobs directly on /fh/fast/.** The Fast filesystem is optimized for moderate, concurrent access, not for a single job doing millions of small reads/writes. Use `/hpc/temp/` or `$TMPDIR` for active computation and copy results back when done.

## Instructions

When helping users with temporary storage:

1. Identify the performance and durability needs of the workflow
2. Recommend temp (`/hpc/temp`) for short-lived intermediate files (default choice)
3. Recommend job-local (`$TMPDIR`) for maximum I/O on single-node jobs
4. Recommend Working for longer-lived working copies where a primary exists elsewhere
5. Always remind users to copy results to durable storage (Fast or Economy/S3) when done
6. Suggest workflow managers (Nextflow, Snakemake, Cromwell) for automated staging
7. Flag I/O anti-patterns (many small files, tight open/close loops) and suggest alternatives

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_task/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_posix/
