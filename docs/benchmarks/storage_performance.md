# Storage performance analysis — Fred Hutch HPC

**Date:** 2026-04-17
**Host:** rhino (single node), Linux 4.15.0-213-generic, 754 GiB RAM
**Method:** `docs/benchmarks/storage_bench.py`, median of 3 reps per metric
**Scope:** comparison of the five storage surfaces reachable from a rhino node

## TL;DR

For an NFS workload on Setty Lab accounts today:

- **Bulk sequential reads:** `/hpc/temp/` is ~40% faster than `/fh/fast/` (NFSv4.1 with 1 MiB blocks vs NFSv3 with 128 KiB reads).
- **Many small files / tight open-close loops:** `/fh/fast/` or `/fh/working/` are ~2× faster than `/hpc/temp/`.
- **Genuinely I/O-bound single-node jobs:** stage to `$TMPDIR` (local NVMe) or `/dev/shm` (RAM). They beat every NFS surface by 10×–100×, at the cost of capacity.
- **`/fh/scratch/` is fully decommissioned** — no longer mounted on rhino or gizmo. `/hpc/temp/setty_m/$USER/` is the sole replacement.

## Filesystems tested

| Label | Path | Backing | Mount | Notes |
|---|---|---|---|---|
| `fast` | `/fh/fast/setty_m/user/$USER` | Isilon (`silver`) | NFSv3, rsize=128 KiB, wsize=512 KiB | 11 PB pool, daily backup, lab quota 5 TB |
| `temp` | `/hpc/temp/setty_m/$USER` | scratch.chromium | NFSv4.1, rsize=wsize=1 MiB | 2.5 PB pool, 30-day purge from creation, `touch` does NOT reset |
| `working` | `/fh/working/setty_m/$USER` | Osmium-nfs | NFSv3, rsize=128 KiB, wsize=512 KiB | 866 TB pool, snapshots only, no daily backup |
| `localtmp` | `/tmp/` (rhino) | ext4 on NVMe | local | On compute nodes this is `$TMPDIR`/`$SCRATCH_LOCAL`, job-lifetime only |
| `shm` | `/dev/shm/` | tmpfs | RAM | Consumes the job's `--mem` allocation; 378 GiB on this host |

## Methodology

Each filesystem ran four metrics:

1. **Sequential write** — `dd if=/dev/zero of=seq.bin bs=1M count=2048 conv=fdatasync` with `oflag=direct` when supported.
2. **Sequential read** — `dd if=seq.bin of=/dev/null bs=1M count=2048` with `iflag=direct` when supported.
3. **Metadata** — wall-clock time to create + stat + delete 1000 one-byte files.
4. **Random 4 KiB reads** — 500 random-offset reads from a freshly written 256 MiB file. `posix_fadvise(POSIX_FADV_DONTNEED)` is called beforehand to drop cached pages; `POSIX_FADV_RANDOM` hints the kernel not to read ahead. This approach is portable across NFS, ext4, and tmpfs (O_DIRECT has cross-FS buffer-alignment quirks).

Direct I/O was used for sequential tests on `fast`, `temp`, `working`, and `localtmp`. tmpfs does not implement O_DIRECT, so `shm` uses buffered I/O — for tmpfs this is not a distortion because the backing *is* RAM.

**Caveats:**

- Single host, single run per metric (3 reps of each). Shared-NFS load varies with cluster activity.
- No file-level cache drop on NFS between reps (no root). fadvise DONTNEED on the client invalidates client-side pages; server-side caches may still help repeat reads.
- Sequential reads on NFS with `iflag=direct` force server fetches per block, so read numbers are closer to wire throughput than cache hits.
- The 2 GiB sequential file is below the 378 GiB page cache; only direct I/O guarantees we measure the network path.

## Results

Medians, 3 reps each, all runs within ~10% relative stdev:

| Metric | `fast` | `temp` | `working` | `localtmp` | `shm` |
|---|---|---|---|---|---|
| Sequential write (MiB/s) | 216 | 212 | 245 | 2174 | **2320** |
| Sequential read (MiB/s)  | 395 | 556 | 375 | 1864 | **4408** |
| Metadata (s / 1000 files) | 5.2 | 11.7 | 5.1 | **0.07** | **0.06** |
| Random 4 KiB reads (ops/s) | 2433 | 2025 | 1873 | 7809 | **256 395** |

## Interpretation

### NFS tiers are close on writes, split on reads

Sequential writes land in the same ~200–250 MiB/s band across all three NFS surfaces. The limiting factor is probably the wsize and the client's TCP pipeline, not the backend. `working` was marginally faster (245 MiB/s median) but not by a margin that should influence placement.

Sequential reads differ meaningfully:

- `temp` at **556 MiB/s** benefits from the NFSv4.1 1 MiB rsize. Fewer RPCs per MiB transferred, higher effective pipelining.
- `fast` and `working` sit at ~375–395 MiB/s, consistent with their 128 KiB rsize on NFSv3.

Implication: if a pipeline streams large files (BAMs, FASTQs, zarr chunks) and does not do many small reads, reading from `/hpc/temp/` is free performance. The catch is metadata.

### Metadata cost: `/hpc/temp/` is ~2× slower

`temp` is 11.7 s / 1000 files vs ~5.1 s on `fast` / `working`. That is a real cliff for many-small-files workloads:

- per-cell output pickles
- per-sample TSV dumps
- git-style content-addressable stores
- log-per-iteration debugging

Such workloads should run on `fast` or stage to `$TMPDIR`. The 1 MiB NFS block that wins us sequential read speed on `temp` does not help when the workload is dominated by metadata RPCs.

### Node-local tiers crush NFS

Local NVMe (`localtmp`, on rhino's `/tmp`) and RAM (`shm`) are in a different performance class:

- ~10× the sequential throughput of NFS
- ~70× faster metadata
- 3× (NVMe) to 100× (tmpfs) on random 4 KiB reads

The catch: capacity and lifetime. `/tmp` on rhino is 44 GiB; on gizmo compute nodes, `$SCRATCH_LOCAL` is job-lifetime and sized per node. `/dev/shm` is RAM-backed and deducts from your Slurm `--mem`.

The established pattern in `fh.storage-scratch` — copy input to `$TMPDIR`, compute, copy results back to `/fh/fast/` — is the right default for I/O-heavy single-node jobs, and the numbers support it:

```
/fh/fast --[cp]--> $TMPDIR (~2 GiB/s, unshared)
                   |
                 compute
                   |
/fh/fast <--[cp]-- $TMPDIR
```

Even counting the copy time, if the job reads each file more than once, staging wins.

### Random 4 KiB reads on NFS: all within ~30%

Across `fast` / `temp` / `working`, random small reads are 1.9k–2.4k ops/s. This is the regime where NFS latency dominates; block size and server pool matter less because each op is a separate RPC round-trip. For this workload profile there is no meaningful preference between the three NFS tiers.

## Recommendations

| Workload shape | Primary choice | Reason |
|---|---|---|
| Read one big file sequentially (alignment, bulk matrix load) | `/hpc/temp/` | 40% faster read throughput |
| Many small files (per-cell, per-sample, per-iteration) | `/fh/fast/` | 2× faster metadata |
| I/O-heavy single-node (sort, index, dedup) | `$TMPDIR` on a `--tmp=…G` Slurm job | 10× everything, at job-scope only |
| In-memory sort / hash / index that fits in RAM | `/dev/shm/` (and budget `--mem`) | RAM speed |
| Primary copy (only copy of the data) | `/fh/fast/` or Economy/S3 | Backed up / durable |

## Future considerations

- Repeat on a gizmo compute node to compare with rhino. Compute nodes have different NIC configurations and `$SCRATCH_LOCAL` may be larger-SSD than rhino's `/tmp`.
- Rerun at different times (weekday-peak vs weekend-quiet) to see how much shared-NFS load shifts the NFS numbers.
- Add a small-file sequential write test (create 10 000 × 4 KiB files, aggregate throughput) — the lab's `dataset.info`-heavy scatter-gather pattern is closer to this than to the 2 GiB single-file test.
- If `Cirro` adoption grows, measure it alongside. It is not on the node filesystem.
- Consider streaming benchmarks against the backing Isilon/Osmium/scratch heads directly to separate client-side from server-side bottlenecks.

## Reproducing

Outside the agent sandbox (writes to `/hpc/temp` require full permissions):

```bash
cd /fh/fast/setty_m/user/$USER/nexus/work/fh-hpc-skills
python3 docs/benchmarks/storage_bench.py
# or skip any tier:
python3 docs/benchmarks/storage_bench.py --skip working
```

Runtime: ~8 min for all five filesystems. Cleans up after itself; peak disk use ~2.3 GiB per tier during the sequential phase.
