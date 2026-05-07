---
description: "Scratch and task-optimized storage at Fred Hutch — /hpc/temp (NFS, 30-day purge, bulk-read winner), $TMPDIR / /tmp / $SCRATCH_LOCAL (node-local NVMe on gizmok* but ~10x slower on gizmoj*), /dev/shm (tmpfs/RAM), and /fh/working (long-lived working copies). Covers the staging-copy pattern for I/O-heavy jobs."
---

# Scratch and Temporary Storage

TRIGGER when: user asks about scratch storage, temp storage, /hpc/temp, $TMPDIR, /tmp, /loc/scratch, $SCRATCH_LOCAL, /dev/shm, tmpfs, node-local storage, staging input data, intermediate compute files, /fh/working, or working storage on the cluster

## Context

Fred Hutch provides several temporary/task-optimized storage options for intermediate computational data. These are NOT backed up and should NEVER hold the only copy of important data.

**CRITICAL: Do not store the primary or only copy of any dataset in temp storage. Always ensure a durable copy exists in Fast or Economy/S3.**

Note: the old network-scratch path `/fh/scratch/delete{10,30,90}/` has been fully decommissioned. `/hpc/temp/` is the sole replacement.

## Quick decision guide (free-to-choose case)

If you are NOT in a sandbox with restricted writes — i.e., you can pick any path on the cluster — match the workload shape against this table. All claims below are grounded in the Apr-2026 weekly fleet benchmark (n=28, full table further down).

| Workload shape | Primary choice | Why |
|---|---|---|
| Read one big file sequentially (load 100 GiB matrix, alignment input, model checkpoint) | `/hpc/temp/` | Median read 565 MiB/s, ~40 % above `/fh/fast/` and `/fh/working/`. **Load-insulated** (ρ ≈ 0 across 0.44–0.90 cluster load). |
| Write one big file sequentially (bulk output, large checkpoint) | `/fh/working/` | Median write 278 MiB/s, beats `/fh/fast/` (223) and `/hpc/temp/` (202). Unlike `/fh/fast/`, no observed load-sensitivity on writes. |
| Many small files: pip caches, conda envs, R libraries, build trees, per-cell pickles | `/fh/working/` (then `/fh/fast/`) | Metadata 4.0 s/1000 files vs 4.6 (`fast`) and 10.4 (`temp`). `/hpc/temp/` is ~2.5× slower on metadata — avoid. |
| Long-term storage of analytical artifacts (notebooks, manuscripts, figures, derived data you'll cite) | `/fh/fast/` | Daily backup + offsite replication (`/fh/working/` and `/hpc/temp/` are not backed up). See `fh.storage-fast`. |
| Job-local scratch, single-job lifetime, on `gizmok*` | `$TMPDIR` (NVMe `/tmp`) | ~2 GiB/s, ~7800 random ops/s — beats every NFS tier on every metric. |
| Job-local scratch, single-job lifetime, on `gizmoj*` | **stay on `/fh/working/` or `/fh/fast/`** | NVMe is not present on `j` nodes; `/tmp` is ~205 MiB/s and ~235 random ops/s — staging copies *for random reads* is a 12–15× loss. |
| In-memory dataset that fits in RAM (sorting, intermediate index, small-but-hot file) | `/dev/shm/` | Median read 5397 MiB/s, random reads 412 016 ops/s. **Counts against `--mem`** — request enough for app + tmpfs. |
| Working-dir during interactive `grabnode` / `srun --pty` development | `/fh/working/` (project tree) or `/fh/fast/user/$USER` (user tree) | Both are session-persistent. `/hpc/temp/` is fine for a scratch session as long as no 30-day-purge file is the only copy. |

**Sandbox-constrained case** (the agent-sandbox restricts writes outside `/fh/fast/`, `/hpc/temp/`, and `~/.claude/`): use `/hpc/temp/setty_m/$USER/` for transient scratch, `/fh/fast/setty_m/user/$USER/` for durable outputs. The free-to-choose rules above still apply *within* those two paths; you just can't reach `/fh/working/`, `/dev/shm/`, or node-local `/tmp` directly from the sandboxed shell. Inside an `sbatch` job submitted *from* the sandbox, the job runs unsandboxed on the compute node and can use any of the above.

When the data doesn't support a strong claim (e.g., random 4 KiB reads on the three NFS tiers are within ~30 %, ordering swaps run-to-run), don't optimise — pick the durability/lifecycle tier that fits and move on.

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

Measured across the cluster fleet over a week (n=28 Slurm runs across 21 distinct gizmo nodes, 4 scheduled slots/day, Apr 18–24 2026; median [IQR]). Full report: `docs/benchmarks/storage_performance.md`. Raw long-form: `docs/benchmarks/weekly_summary.tsv`.

| Metric | `/fh/fast` | `/hpc/temp` | `/fh/working` | `/tmp` (gizmok* NVMe) | `/tmp` (gizmoj*) | `/dev/shm` |
|---|---|---|---|---|---|---|
| Sequential write (MiB/s) | 223 [204–234] | 202 [193–210] | **278** [250–306] | **2144** [2038–2209] | 204 [186–209] | **2426** [2291–2489] |
| Sequential read (MiB/s)  | 335 [284–357] | **565** [532–580] | 416 [337–492] | 1824 [1813–1827] | 218 [215–227] | **5397** [5073–5773] |
| Metadata (s / 1000, lower = faster) | 4.6 [4.4–4.9] | 10.4 [8.0–12.0] | **4.0** [3.3–4.5] | 0.06 [0.05–0.17] | 0.08 [0.06–0.08] | **0.05** [0.04–0.05] |
| Random 4 KiB reads (ops/s) | 2933 [2768–3045] | 2075 [1787–2273] | **2954** [2214–3380] | **7824** [7710–7903] | 235 [230–239] | **412 016** [343 806–491 207] |

**Takeaways (per the Apr-2026 weekly benchmark):**

- `/dev/shm` beats every disk-backed surface by 5×–100× on every metric; consumes your job's `--mem` allocation.
- **`/tmp` is bimodal across the gizmo fleet.** Every `gizmok*` node tested has fast NVMe (~2 GiB/s, ~7800 random ops/s, beats every NFS tier). Every `gizmoj*` node tested is ~10× slower across all metrics (~205 MiB/s, ~235 random ops/s). Same `--tmp` Slurm request, very different storage tier — see "Per-node variance" below.
- Among NFS tiers: `/hpc/temp` is the **bulk sequential read winner** (median 565 MiB/s, ~40 % above `/fh/fast/` and `/fh/working/`) and is the only NFS tier whose seq-read throughput is **insulated from cluster load** (Spearman ρ = +0.00 over 0.44–0.90 load). `/fh/working` is the **bulk write and metadata winner** (278 MiB/s write, 4.0 s metadata), but is the most load-sensitive on bulk reads (ρ = −0.60, p = 7×10⁻⁴ — the Osmium head visibly degrades under heavy cluster load).
- Random 4 KiB reads on the three NFS tiers are within ~30 % of each other; `/fh/fast/` and `/fh/working/` are roughly tied at ~2940 ops/s, `/hpc/temp/` is ~30 % lower at 2075.
- The `shm > localtmp > NFS` ordering is rock-solid run-to-run. **Within the three NFS tiers, ordering swaps freely** — especially on random reads, where the median ordering matches only 18 % of single runs. Don't quote a single-run NFS-tier ranking as fact.

### Per-node variance on `/tmp` — the `gizmoj` / `gizmok` cohort split

The Apr-2026 fleet split 14:14 between `gizmoj*` and `gizmok*` runs. Every `gizmoj*` host observed (8 distinct: j1, j7, j15, j16, j19, j22, j28, j35) is ~10× slower on `/tmp` than every `gizmok*` host observed (13 distinct: k2, k8, k10, k18, k29, k61, k64, k100, k112, k116, k124, k138, k140). Same Slurm `--tmp` request lands on very different hardware.

Operational implication: the "stage to `$TMPDIR`" advice below is **conditional on landing on a `gizmok*` node**. On a `gizmoj*` node:

- Staging *write* (~205 MiB/s) is slower than `/fh/working/` (278) and roughly tied with `/fh/fast/` (223) — the staging-copy round trip is wasted time.
- *Random-read* on `/tmp` is **15× slower than `/fh/fast/`** (235 vs 2933 ops/s). Staging an input for random-read workloads on a `gizmoj` node is a net loss.

If random-read latency is critical, prefer Slurm node features/constraints to land on `gizmok*` (or stay on `/fh/working/`/`/fh/fast/`) over relying on `$TMPDIR` being uniformly fast. Spot-check unobserved nodes before trusting the cohort generalization.

Numbers are population medians+IQR across the weekly fleet, not a single host. Different week → different cluster load distribution → different exact slopes; rerun under your own load before bet-the-paper decisions. See `docs/benchmarks/storage_performance.md` for the full report and figures.

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
