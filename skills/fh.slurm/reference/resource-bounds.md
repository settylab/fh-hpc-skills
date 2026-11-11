# Bounding and sizing jobs on Gizmo

Detail behind "Memory and wall time are not enforced" in `fh.slurm`. Measurements are from lab jobs in 2026.

## Neither `--mem` nor `--time` is enforced

Check the configuration yourself: `scontrol show config | grep -E 'OverTimeLimit|EnforcePartLimits|SelectTypeParameters|ConstrainRAMSpace'`. Measured: a `--mem=12G` job peaked at ~457 GiB; over two weeks of one project's jobs, 11 ran past `--time` (one by +22 h on a 7-day limit) and none ended in state TIMEOUT. `--mem` only chooses the machine, regardless of what already runs there, so an overrun eats co-located jobs' memory and an underestimate can land the job on a node too small for it. The only real bounds are the ones inside the job:

- **Wall:** wrap the real step, `timeout -k 60 <N> <cmd>; rc=$?`, and write durations in ONE unit (`375m`, not `6h15m`: GNU `timeout` rejects compound forms with rc 125). Treat a timeout as inconclusive, never a pass.
- **Memory, single process:** `ulimit -v`, `prlimit --as`, or `resource.setrlimit(RLIMIT_AS)` equal to `--mem`, plus a test that it fires. The rlimit is PER PROCESS: two 1.5 GiB workers ran under a 2 GiB cap.
- **Memory, multi-process:** an in-job RSS watchdog that sums RSS over the **descendant tree** (`/proc/<pid>/stat` field 4 = ppid, `statm` resident pages), not over a process group. GNU `timeout` calls `setpgid()` on its child, so a pgid-keyed watchdog saw only the wrapper shell: a 600 MB child under `timeout` measured a 3 MB peak and was never killed. On a kill, SIGKILL every pgid the tree spans, then every pid. The test that the watchdog FIRES must allocate under the real wrapper (child, grandchild, and under `/usr/bin/timeout`), and a pgid-only variant of the watchdog must fail it.

## `ulimit -v` caps VIRTUAL memory, which misfires on

- **Many-core nodes:** BLAS/OpenMP reserve per-core arenas, so numpy at 1.1 GB RSS hit MemoryError under a 4 GiB cap on a 36-core node. Set `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `BLOSC_NTHREADS` to `--cpus-per-task`.
- **Threaded native code** ("can't start new thread"); zarr + pyarrow (see `fh.python` → Python gotchas).
- **Node.js:** V8 reserves wasm guard regions, so `WebAssembly.instantiate` fails "Cannot allocate Wasm memory" under any few-GiB cap. Bound node by RSS instead.
- **Nested launchers:** a bash `ulimit -v N` sets soft AND hard limit, so a launcher run inside it cannot raise its own cap. A test of a launcher inside a capped job must substitute a cap at or below the outer one.

## Reading MaxRSS

With `jobacct_gather/linux` + `proctrack/cgroup` (check `scontrol show config | grep JobAcctGather`), a `.batch` step's MaxRSS is the peak of the whole process tree but SAMPLED every 60 s: the same job on the same input read 1.96 GB in one run and 5.92 GB in another, and jobs under ~60 s can read near 0. Treat it as a lower bound. If an in-job guard decides the kill, size against the guard's own recorded tree peak plus what the code holds at the same moment, not against sacct.

## Sizing a bound or a memory request

- Size memory from the largest input's stored shape (`.zarray`/`zarr.json` metadata), not from a small fixture or a different tool's MaxRSS. For AnnData value diffs, ALLOWLIST the groups to decode (`obs, var, obsm, uns`): a blocklist of `X`/`layers` still decodes `raw/X` and every dense `obsp` (that diff was the ~457 GiB job above).
- Time at least two input sizes before extrapolating: 2x the bytes took >5.4x the time for a regex screen.
- Size from the driving quantity (rows, cells), fitted on real runs. A dry-run peak measures a different code path (real/dry ratios ranged 0.74 to 8.2).
- Time each step on data that CONTAINS the feature it scales with (a run with zero labels timed none of the label code), then size at ≥5x (≥10x when NFS-bound).
- Time one real case of the EXACT version you will run, not the previous version's rate.
- A reused tool's own hard-coded timeouts (e.g. `timeout 3600 cp -al` inside it) must be resized for the new input too.
- Request CPUs equal to the work that runs concurrently; arms that run one at a time leave the rest idle.
- Make long drivers append each row as it finishes (`O_APPEND` + fsync), so a timeout leaves evidence.

## A silent log is not a hang

An empty log with low `sstat` CPU fits both "deadlocked" and "slow I/O before the first print": a job cancelled as hung had spent 9 minutes reading a file another node read in under one. Wrap long Python jobs in a periodic stack dump from the start (`faulthandler.dump_traceback_later(900, repeat=True)` before `runpy.run_path(...)`), read a dump or a second `sstat` delta before cancelling, and `--exclude` a slow node rather than changing code. Live CPU with no progress meter is "slow, ETA unknown", never "stalled"; compare against a healthy sibling's per-interval CPU.

## A queue estimate is not a state

`--test-only` start estimates were wrong both ways (a job estimated two days out started in 2 minutes; one estimated "now" sat PENDING), and it never shows QOS/partition refusals or reservations. After every submit, read `squeue -u $USER -h -o '%i %T %r %P %q'` within a couple of minutes and act on the reason. Immediately before editing a submitted job's inputs or cancelling it, re-read the state and gate the action in the same command (`[ "$(sacct -X -n -P -o State -j $ID)" = PENDING ] || exit`). Never edit a submitted job's files in place; write new names for a resubmit.
