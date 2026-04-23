---
description: "Etiquette and self-diagnosis for working on multi-tenant nodes (rhino login nodes, barnacle-shared gizmok, shared interactive sessions) on the Fred Hutch Gizmo cluster"
---

# fh.shared-nodes

TRIGGER when: user asks about shared compute, rhino vs gizmo,
"is this node busy", memory pressure on a multi-tenant node,
`barnacle`, `gizmok1`, joining a lab-shared node, whether it is
safe to run something locally, or how to avoid disrupting other
users on a node.

## Context

Any node where your process can affect another user's work is a
**shared node**. The etiquette for these nodes is different from
a dedicated allocation: memory in particular is not time-sliced,
so an OOM from your process kills everyone's work, not just yours.

This skill is the etiquette layer. For the mechanics of getting a
session in the first place see `fh.interactive-sessions`; for
partition / resource specs see `fh.cluster-overview` and
`fh.partitions`.

## What counts as a shared node

- **Rhino login nodes** (`rhino01` .. `rhino03`). Default landing
  after `ssh rhino`. Always multi-tenant. Arbiter enforces a cap
  of roughly 16 cores / 86 GB per user and throttles (not kills)
  when exceeded for several minutes. Light interactive use is
  fine; heavy compute is anti-social regardless of the cap.
- **Settylab gizmok shared tenancy** (e.g. `gizmok1`) managed via
  `barnacle`. Multiple lab members hold 1-CPU Slurm placeholder
  jobs on the same node to keep SSH alive, then share the full
  CPU / RAM via tmux + jupyter. See "Settylab pattern" below.
- **Any `grabnode` / `srun --pty` session** can become shared
  simply by convention: if lab members coexist on one node to
  reuse an allocation, the same etiquette applies even when the
  Slurm accounting hides it.

**Not** shared: a dedicated `grabnode` you hold alone, or batch
jobs you run under your own `--exclusive` or single-user
allocation.

## How to self-diagnose

```bash
# Who am I and where?
hostname                            # rhino* → login node, gizmo* → compute
whoami
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-none}"

# Who else is here?
w                                   # active shells + what they're running
users                               # just the usernames
ps -eo user,pid,pcpu,pmem,rss,cmd --sort=-pmem | head -20
```

- `hostname` starting with `rhino` → shared login node, full stop.
- `hostname` starting with `gizmo` or `gizmok` → compute node.
  Check `w` / `ps` to see whether anyone else is active. On a
  `barnacle`-managed node there will be multiple unrelated users.
- Inside a Slurm allocation, `scontrol show job $SLURM_JOB_ID`
  shows exactly which resources are yours. Anything above that
  budget belongs to someone else.

## What agents can and cannot do

**Rhino:** light interactive compute only — `jq`, `grep`, `awk`,
git, small Python one-liners, module searches. No multi-GB
dataset loads, no ML training, no `-j$(nproc)` parallel builds,
no background `while true` loops. If a task would plausibly
exceed a few seconds of CPU or a few hundred MB of RAM, move it
to `grabnode` / `sbatch`.

**Shared gizmo (including barnacle-managed gizmok):** compute is
permitted, but **memory is the shared resource that matters
most**. CPU can be time-sliced by the scheduler; RAM cannot. An
OOM on a shared node takes down co-tenants' kernels too. Prefer
streaming / chunked loads and keep headroom.

**Your own dedicated allocation:** use what you asked for, but
still respect the whole-node cap (RAM + CPU) if your job might
oversubscribe.

## Memory etiquette

```bash
free -h                             # current RAM situation
ps -o rss -p $$                     # this shell's resident size (KB)
```

```python
# From inside Python
import psutil
psutil.virtual_memory().available / 1e9    # GB free system-wide
psutil.Process().memory_info().rss / 1e9   # GB this process is using
```

- Check `free -h` before loading anything large.
- Prefer streaming / backed readers for large files:
  `sc.read_h5ad(path, backed='r')`, `dask.dataframe.read_parquet`,
  `pyarrow`'s chunked / dataset API, `pandas.read_csv(..., chunksize=...)`.
- Drop intermediates explicitly: `del bigvar; import gc; gc.collect()`.
  This matters more on shared nodes than dedicated ones because
  your RSS is someone else's ceiling.
- Watch your own process while it runs: `top -p $$` in another
  pane. Kill early if RSS crosses a reasonable fraction of node
  RAM given who else is on the box.
- In `sbatch` scripts, always set `--mem=` (or `--mem-per-cpu=`)
  explicitly. Under-request and re-run if you must; don't
  over-request and starve the queue.

## CPU etiquette

- Cap thread-pool libraries before they grab every core:
  `export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4`.
  Respect admin-set caps when present.
- For Python pools, pick `max_workers` relative to your fair
  share of the node, not `os.cpu_count()` (which reports the
  whole machine, including other tenants' CPUs).
- For long-running background work on a shared node, prefix with
  `nice -n 10` and/or `ionice -c 3` so foreground users preempt
  you automatically.
- Never fork-bomb a shared node. `for i in ...; do python ... & done`
  without a semaphore is a smell; use GNU `parallel -j N`,
  `xargs -P N`, or a proper Slurm array.

## Settylab pattern: `barnacle` on `gizmok1`

Settylab shares `gizmok1` via
[barnacle](https://github.com/settylab/barnacle). Each user holds
a few 1-CPU Slurm placeholder jobs so SSH stays alive across the
7-day job limit; the actual compute runs inside tmux on the node,
with all users sharing the node's full CPU / RAM pool.

**There is a watcher on `gizmok1`.** @dotto (Dominik) runs
`barnacle watch` on `gizmok1` to welcome new settylab users and
hand over placeholder slots automatically when someone joins.
It's a live process, not just a script library — if it's down,
joining still works but the auto-handover and welcome side won't
fire.

**Before joining, check the target node:**

```bash
# From rhino, with the barnacle checkout on your PATH or PWD
barnacle -n gizmok1 status
```

This prints node state, load, who owns which slots, how many
placeholder (free) slots are available, and — via the running-
jobs list — whether a `barnacle_watch` / `barnacle watch` process
is alive. Read it for two things before joining:

1. Is the watcher running? If not, your `join` will still submit
   jobs but you won't get the automatic handover.
2. Are there free slots? If everything is already claimed, your
   `join` would bump someone or fail — don't.

**Joining, once the status check looks sane:**

```bash
barnacle -n gizmok1 join          # default 3 staggered slots
```

Then `ssh gizmok1.fhcrc.org` directly (no need to hop via rhino
once your slots are running) and work inside tmux. Memory
etiquette above applies with extra emphasis: you share RAM with
every other lab member on the node.

**Releasing:** `barnacle -n gizmok1 leave` when you're done so
the slots return to the free pool. Don't leave a barnacle
tenancy parked indefinitely while idle.

Anything beyond this — onboarding a brand-new user, repairing
broken extension chains, teardown, etc. — lives in the barnacle
repo, not this skill: <https://github.com/settylab/barnacle>.

## Agent checklist

1. Run `hostname` at session start. If it matches `rhino*`, treat
   every subsequent command as "on a shared login node" and skip
   heavy compute.
2. Run `free -h` and `w` once to know RAM budget and neighbors.
3. In Slurm jobs, set `--mem` and a realistic `--time` explicitly.
4. Cap thread-pool env vars (`OMP_NUM_THREADS` etc.) before
   launching numerical work on a shared node.
5. No unbounded background loops or `&`-fan-outs on a shared node.
6. On `gizmok1`: `barnacle -n gizmok1 status` before `join`;
   `barnacle -n gizmok1 leave` when done.
7. If a task needs real resources, prefer a dedicated `grabnode`
   or `sbatch` allocation over local compute on a shared node.

## See also

- `fh.interactive-sessions` — how to actually obtain a session
  (`grabnode`, `srun --pty`).
- `fh.slurm` — `--mem`, `--cpus-per-task`, job arrays.
- `fh.partitions` — which partition fits which workload.
- `fh.cluster-overview` — node classes and total capacity.
- `fh.monitoring` — cluster-wide load and queue state.
- `barnacle` repo: <https://github.com/settylab/barnacle>.
