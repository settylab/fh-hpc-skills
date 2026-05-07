# Storage performance analysis — Fred Hutch HPC

**Scope:** comparison of the five storage surfaces reachable from a Gizmo node.

**Single-host baseline:** rhino, 2026-04-17, single run, 3 reps per metric.
**Weekly fleet:** 28 Slurm jobs across 21 distinct gizmo nodes, 4 scheduled
slots/day (03:15 / 09:30 / 14:30 / 21:00), 2026-04-18 → 2026-04-24.
All 28 weekly jobs `COMPLETED 0:0`. Aggregated to
`docs/benchmarks/weekly_summary.tsv`; analysis pipeline in
`docs/benchmarks/analyze_weekly.py`.

## TL;DR

For typical Setty Lab NFS workloads:

- **Bulk sequential reads:** `/hpc/temp/` median **565 MiB/s** beats `/fh/working/`
  (416) and `/fh/fast/` (335). The ~40% margin from the rhino baseline holds and
  widens slightly across the fleet.
- **Bulk sequential writes:** `/fh/working/` (median 278 MiB/s) edges out `/fh/fast/`
  (223) and `/hpc/temp/` (202). Spread is narrow — none of the three NFS tiers
  blow the others out on writes.
- **Many small files:** `/fh/working/` (4.0 s / 1000 files) and `/fh/fast/`
  (4.6 s) beat `/hpc/temp/` (10.4 s) by ~2.5×. Don't put `git`-style
  many-tiny-files workloads on `/hpc/temp/`.
- **Random 4 KiB reads:** `/fh/working/` (2954 ops/s) ≈ `/fh/fast/` (2933 ops/s)
  > `/hpc/temp/` (2075). Within ~30% across NFS tiers, no clear winner.
- **`/tmp` on a Gizmo node depends on the node class.** `gizmok*` nodes have
  fast NVMe-class scratch (~2100 MiB/s write, ~1820 MiB/s read, ~7800 random
  ops/s). `gizmoj*` nodes have ~10× slower scratch (~205 MiB/s, ~218 MiB/s,
  ~235 ops/s). Same Slurm `--tmp` request, very different storage tier.
- **`/dev/shm`** beats every other surface by 5×–100×. Counts against the job's
  `--mem` allocation.

## Filesystems tested

| Label | Path | Backing | Mount | Notes |
|---|---|---|---|---|
| `fast` | `/fh/fast/setty_m/user/$USER` | Isilon (`silver`) | NFSv3, rsize=128 KiB, wsize=512 KiB | 11 PB pool, daily backup, lab quota 5 TB |
| `temp` | `/hpc/temp/setty_m/$USER` | scratch.chromium | NFSv4.1, rsize=wsize=1 MiB | 2.5 PB pool, 30-day purge from creation, `touch` does NOT reset |
| `working` | `/fh/working/setty_m/$USER` | Osmium-nfs | NFSv3, rsize=128 KiB, wsize=512 KiB | 866 TB pool, snapshots only, no daily backup |
| `localtmp` | `/tmp/` (compute node) | NVMe (gizmok), spinning/SATA SSD (gizmoj) | local | On compute nodes this is `$TMPDIR` / `$SCRATCH_LOCAL`, job-lifetime only |
| `shm` | `/dev/shm/` | tmpfs | RAM | Consumes the job's `--mem` allocation |

## Methodology

Each filesystem ran four metrics:

1. **Sequential write** — `dd if=/dev/zero of=seq.bin bs=1M count=2048 conv=fdatasync` with `oflag=direct` when supported.
2. **Sequential read** — `dd if=seq.bin of=/dev/null bs=1M count=2048` with `iflag=direct` when supported.
3. **Metadata** — wall-clock time to create + stat + delete 1000 one-byte files.
4. **Random 4 KiB reads** — 500 random-offset reads from a freshly written 256 MiB file. `posix_fadvise(POSIX_FADV_DONTNEED)` evicts cached pages; `POSIX_FADV_RANDOM` hints the kernel away from read-ahead. Portable across NFS, ext4, and tmpfs (O_DIRECT has cross-FS buffer-alignment quirks).

Direct I/O on sequential tests for `fast`, `temp`, `working`, `localtmp`. tmpfs does not implement O_DIRECT, so `shm` uses buffered I/O — which is fine because tmpfs *is* RAM.

**Caveats:**

- No file-level cache drop on NFS between reps (no root). fadvise DONTNEED on the client invalidates client-side pages; server-side caches may still help repeat reads.
- Sequential reads on NFS with `iflag=direct` force server fetches per block, so read numbers are closer to wire throughput than cache hits.
- The 2 GiB sequential file is below the page cache; only direct I/O guarantees we measure the network path.
- `--begin` is a Slurm lower bound. Under heavy load a job can start hours after its target. The "time-of-day" axis is the *scheduled* bucket, not necessarily a clean morning/evening split. See "Time-of-day effect" below.
- All 28 weekly jobs landed on Gizmo nodes; none on rhino. Per-node variance is real (especially `localtmp`, see below) and the fleet does not hold node fixed.

## Results — weekly fleet medians (n=28)

Median value per (filesystem, metric) across the 28 weekly runs, IQR in
brackets. The single-host rhino baseline (2026-04-17, n=1) is reproduced
in the last column for reference.

| Metric | `fast` | `temp` | `working` | `localtmp` | `shm` | rhino n=1 |
|---|---|---|---|---|---|---|
| Sequential write (MiB/s) | 223 [204–234] | 202 [193–210] | **278** [250–306] | 991 [205–2142]* | **2426** [2291–2489] | 216 / 212 / 245 / 2174 / 2320 |
| Sequential read (MiB/s)  | 335 [284–357] | **565** [532–580] | 416 [337–492] | 1002 [219–1824]* | **5397** [5073–5773] | 395 / 556 / 375 / 1864 / 4408 |
| Metadata (s / 1000 files, **lower = faster**) | 4.6 [4.4–4.9] | 10.4 [8.0–12.0] | **4.0** [3.3–4.5] | **0.08** [0.05–0.08] | **0.05** [0.04–0.05] | 5.2 / 11.7 / 5.1 / 0.07 / 0.06 |
| Random 4 KiB reads (ops/s) | 2933 [2768–3045] | 2075 [1787–2273] | **2954** [2214–3380] | 3842 [235–7823]* | **412016** [343806–491207] | 2433 / 2025 / 1873 / 7809 / 256 395 |

\* `localtmp` is bimodal across the fleet — see the per-node section. The
single-population median and IQR collapse two distinct hardware classes
into one row and should not be cited on their own.

Full long-form data: `docs/benchmarks/weekly_summary.tsv`.
Per-(fs,metric) summary: `docs/benchmarks/medians_iqr.tsv`.

## Cluster-load effect on NFS

For each NFS tier, Spearman ρ between the metric and the cluster-CPU
load fraction (`slurm_cpus_alloc / slurm_cpus_total`, recorded at run
start; range across the 28 runs: 0.44–0.90):

| Tier | Metric | Spearman ρ | p | Comment |
|---|---|---|---|---|
| `fast` | seq_write | **−0.43** | 0.023 | Load up → write throughput down. Real but modest (~20–25 % drop near peak). |
| `fast` | seq_read | −0.37 | 0.050 | Borderline; same direction. |
| `fast` | metadata_s | −0.25 | 0.21 | n.s. |
| `fast` | random_read_ops | −0.05 | 0.78 | n.s. |
| `temp` | seq_write | −0.14 | 0.48 | n.s. |
| `temp` | seq_read | +0.00 | 0.98 | **Insulated from cluster load.** |
| `temp` | metadata_s | +0.10 | 0.62 | n.s. |
| `temp` | random_read_ops | −0.01 | 0.96 | n.s. |
| `working` | seq_write | −0.14 | 0.48 | n.s. |
| `working` | seq_read | **−0.60** | **0.0007** | Strong negative — the `working` Osmium head degrades visibly under cluster load. |
| `working` | metadata_s | +0.17 | 0.40 | n.s. |
| `working` | random_read_ops | −0.16 | 0.42 | n.s. |

**Takeaway.** `/hpc/temp/` is the most load-tolerant of the three NFS
tiers — its sequential read throughput barely shifts as the cluster
fills up. `/fh/working/` is the most load-sensitive on bulk reads
(ρ=−0.60, p<0.001). `/fh/fast/` shows a real-but-modest write
slowdown under load.

The cluster never dipped below ~44 % loaded during the week, so this is
not a low-load vs high-load contrast — it is the slope inside the 44–90
% band. Lower-load behaviour is unobserved.

Per-fs-metric Spearman table: `docs/benchmarks/nfs_load_corr.tsv`.

## Per-node variance on `/tmp`

The fleet split 14:14 between `gizmoj*` and `gizmok*` nodes, and the two
cohorts represent two different `/tmp` hardware classes:

| Cohort | Hosts (in fleet) | n runs | seq_write (MiB/s) | seq_read (MiB/s) | metadata (s) | random ops/s |
|---|---|---|---|---|---|---|
| `gizmoj*` (slow) | gizmoj1, j7, j15, j16, j19, j22, j28, j35 | 14 | **204** [186–209] | **218** [215–227] | 0.08 [0.06–0.08] | **235** [230–239] |
| `gizmok*` (NVMe) | gizmok2, k8, k10, k18, k29, k61, k64, k100, k112, k116, k124, k138, k140 | 14 | **2144** [2038–2209] | **1824** [1813–1827] | 0.06 [0.05–0.17] | **7824** [7710–7903] |

The signal flagged in the handoff (gizmoj26 ~10× slower than rhino) is
not gizmoj26-specific. **Every `gizmoj*` node in the fleet shows the same
~200 MiB/s `/tmp`.** Every `gizmok*` node shows ~2 GiB/s. The within-cohort
spread is tight; between-cohort spread is an order of magnitude.

This means the established "stage to `$TMPDIR`" advice is conditional on
the node class:

- **Best-case** (`gizmok*`): staging copy ~2 GiB/s, in-job random reads
  ~7800 ops/s. Comfortably beats every NFS tier on every metric.
- **Worst-case** (`gizmoj*`): staging *write* ~205 MiB/s, slower than
  `/fh/working/` (278) and roughly tied with `/fh/fast/` (223).
  Random-read on `/tmp` is **15× slower than `/fh/fast/`** (235 vs 2933
  ops/s). On a `gizmoj` node, staging an input to `/tmp` for random
  reads is a net loss.

Recommendation summary in `fh.storage-scratch` should:

- Note that `/tmp` performance varies by ~10× between Gizmo node
  classes.
- Add a one-liner: if random-read latency is critical, prefer the
  Slurm `--constraint=` knob (or target `gizmok*` via partition
  features) over relying on `$TMPDIR` being uniformly fast.
- For pure sequential staging on `gizmoj*` nodes, $TMPDIR offers no
  speedup and the staging-copy time is wasted.

Per-host table: `docs/benchmarks/host_localtmp.tsv`.

## Time-of-day effect

Kruskal-Wallis across the four `--begin` buckets (03:15 / 09:30 / 14:30
/ 21:00, n=7 each), per (filesystem, metric). Pairwise follow-up via
Mann-Whitney with Benjamini-Hochberg correction across all pairs.

| Result | Detail |
|---|---|
| Significant KW (p<0.05) | only `/hpc/temp/` random_read_ops, p=0.037 |
| BH-significant pairwise (q<0.10) | **none** |

**Takeaway: no actionable time-of-day effect at this sample size.** The
single Kruskal-Wallis hit on `temp` random reads doesn't survive the
follow-up. Per-bucket cluster load also overlaps strongly across all
four scheduled times, so the buckets don't even cleanly separate the
load axis: `--begin` only sets a lower bound, and Slurm fills in based
on resources, not wall clock. Repeated weeks (or fixed-load buckets
constructed post-hoc) would be a better instrument.

KW table: `docs/benchmarks/time_of_day_kw.tsv`.
Pairwise MWU table: `docs/benchmarks/time_of_day_mwu.tsv`.

## Per-fs ordering robustness

Within each metric, how often does a single run reproduce the
fleet-wide median ordering of the five filesystems?

| Metric | Global median order (best → worst) | n_runs matching | fraction |
|---|---|---|---|
| seq_write_MiBs | shm > localtmp > working > fast > temp | 8 / 28 | 29 % |
| seq_read_MiBs | shm > localtmp > temp > working > fast | 11 / 28 | 39 % |
| metadata_s | shm > localtmp > working > fast > temp | 19 / 28 | 68 % |
| random_read_ops | shm > localtmp > working > fast > temp | 5 / 28 | 18 % |

The `shm > localtmp > NFS` partition is rock solid. Within the three
NFS tiers, ordering is volatile — especially on random reads, where the
fast/temp/working tier swaps freely with each run. **Don't quote a
specific tier ordering between fast/working/temp from a single run.**

Per-run ordering: `docs/benchmarks/ordering_robustness.tsv`.
Summary: `docs/benchmarks/ordering_robustness_summary.tsv`.

## Figures

| File | Content |
|---|---|
| `figures/fig1_box_per_fs.png` | Box + strip per (fs, metric) across the 28 weekly runs. |
| `figures/fig2_nfs_vs_load.png` | NFS metrics vs cluster load. 4×3 panels, Spearman ρ + p annotated. |
| `figures/fig3_localtmp_per_host.png` | Per-host `localtmp` strip plot. The `gizmoj` / `gizmok` cohorts visually separate. |
| `figures/fig4_time_of_day.png` | Box per `--begin` bucket per fs, NFS + localtmp panels. |
| `figures/fig5_ordering_heatmap.png` | Per-run filesystem rank, four metrics. |
| `figures/fig6_load_distribution.png` | Cluster load distribution + per-bucket load (sanity check on the TOD axis). |

## Recommendations

| Workload shape | Primary choice | Reason |
|---|---|---|
| Read one big file sequentially (alignment, bulk matrix load) | `/hpc/temp/` | Median 565 MiB/s read, load-insulated |
| Many small files (per-cell, per-sample, per-iteration) | `/fh/working/` (then `/fh/fast/`) | 2.5× faster metadata than `/hpc/temp/` |
| Random 4 KiB reads | `/fh/fast/` or `/fh/working/` (≈ tied) | `/hpc/temp/` is ~30 % slower |
| I/O-heavy single-node, on `gizmok*` | `$TMPDIR` (NVMe) | ~2 GiB/s, ~7800 random ops/s — beats every NFS tier |
| I/O-heavy single-node, on `gizmoj*` | **stay on `/fh/working/`** | NVMe is not present; `/tmp` is ~205 MiB/s and ~235 random ops/s |
| In-memory fits in RAM | `/dev/shm/` (and budget `--mem`) | RAM speed |
| Primary copy (only copy of the data) | `/fh/fast/` (backed up) | Durability |

## Future considerations

- Add a sequential write test on a known-loaded NFS server to
  characterize `/fh/working/`'s slope explicitly. The −0.60 read ρ
  suggests the Osmium head needs better instrumentation.
- A small-file write test (10 000 × 4 KiB files, aggregate throughput) —
  closer to the lab's `dataset.info` scatter-gather pattern than the
  2 GiB single-file metric.
- Repeat with node affinity (`--constraint=` or per-cohort sbatch) to
  separate node-class effects from the FS axis.
- Track `gizmoj` vs `gizmok` partition features in `fh.partitions` and
  reference from `fh.storage-scratch`.
- If `Cirro` adoption grows, measure it alongside.

## Reproducing

```bash
# Submit the 28-job weekly fleet
cd /fh/fast/setty_m/user/$USER/nexus/work/fh-hpc-skills
docs/benchmarks/schedule_week.sh

# After the week ends
sacct --starttime YYYY-MM-DD --endtime YYYY-MM-DD \
      --name storage_bench --format JobID,State,ExitCode,Elapsed,NodeList -P \
  | column -t -s '|'
ls docs/benchmarks/results/*_summary.tsv | wc -l   # expect 28+

python3 docs/benchmarks/aggregate_results.py > docs/benchmarks/weekly_summary.tsv
module load Seaborn/0.13.2-gfbf-2024a   # pulls in pandas, scipy, matplotlib, seaborn
python3 docs/benchmarks/analyze_weekly.py
```

Single-host run on rhino (peak ~2.3 GiB per NFS tier during sequential phase):

```bash
python3 docs/benchmarks/storage_bench.py
```

Runtime: ~5 min per Slurm job; ~8 min on rhino for all five FS labels.
