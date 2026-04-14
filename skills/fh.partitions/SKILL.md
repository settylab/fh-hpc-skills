---
description: "Gizmo cluster partitions guide (campus-new, short, restart-new, chorus, interactive) with limits and node specs"
---

# Fred Hutch Gizmo Partitions

TRIGGER when: user asks which partition to use, wants to know partition limits, encounters partition-related errors, or needs to understand node generations on the Gizmo cluster.

## Context

For a quick overview of all cluster resources, see fh.cluster-overview.

The Gizmo cluster organizes compute nodes into partitions. Each partition has different time limits, resource limits, and node types. Choosing the right partition affects how quickly your job starts and how long it can run.

## Instructions

### Partition Overview

| Partition | Max Wall Time | Node Gens | Notes |
|-----------|---------------|-----------|-------|
| **campus-new** | 30 days (default 3 days) | j, k | Default partition (QOS: public). Good for most workloads. |
| **short** | 12 hours (default 1 hour) | j, k | Same nodes as campus-new, 2-min overtime grace. Quick jobs. |
| **restart-new** | 30 days (default 3 days) | j, k | Preemptible (REQUEUE). Lowest priority. Requires `--qos=restart`. |
| **chorus** | 7 days (default 4 hours) | harmony | AMD EPYC nodes with L40S GPUs. Max 8 CPUs per QOS. |
| **interactive** | 7 days (default 1 day) | j, k | For interactive sessions via `grabnode`. Highest priority. |
| **canto** | 7 days (default 4 hours) | canto | High-memory nodes with 1.5 TB RAM. |

### Node Specifications

| Generation | Count | CPU | Cores/Node | Memory/Node | Partitions |
|-----------|-------|-----|------------|-------------|------------|
| j | 37 | Intel Gold 6146 | 24 | 384 GB | campus-new, short, interactive |
| k | 161 | Intel Gold 6154 | 36 | 768 GB | campus-new, short, interactive |
| harmony | 8 | AMD EPYC 9354P | 32 | 1536 GB | chorus |
| canto | 3 | AMD or Intel | 36 | 1540 GB | canto |

### Decision Guide

**"My job runs in a few hours"** --> Use `short` partition for faster scheduling:
```bash
sbatch -p short -t 4:00:00 myjob.sh
```

**"My job runs for days"** --> Use `campus-new` (default). Set wall time explicitly:
```bash
sbatch -t 7-00:00:00 myjob.sh
```

**"I need massive resources and can checkpoint"** --> Use `restart-new`. Jobs here can be killed and requeued at any time, so your code must be idempotent or write checkpoints:
```bash
sbatch --partition=restart-new --qos=restart myjob.sh
```

**"I need L40S GPUs or 1.5 TB RAM"** --> Use `chorus`:
```bash
sbatch --partition=chorus --gpus=1 myjob.sh
```
Remember to `module purge` and load fresh modules inside your script because harmony nodes run a different OS.

**"I need an interactive terminal on a compute node"** --> Use `grabnode` (see fh.interactive-sessions skill). The interactive partition runs on the same j/k nodes as campus-new but with the highest scheduling priority (PriorityTier=30000).

### Chorus Partition Special Requirements

Harmony nodes use AMD EPYC processors and a different OS than j/k nodes. Environment modules from rhino/gizmo may not work. In your job script:

```bash
#!/bin/bash
#SBATCH --partition=chorus
#SBATCH --gpus=1

# CRITICAL: purge rhino modules and load chorus-compatible ones
module purge
module load <chorus-compatible-module>

your_command_here
```

### Checkpointing for restart-new Partition

Jobs on `restart-new` can be killed and requeued at any time. Without checkpointing, all progress is lost. Here are concrete recipes:

**Python (pickle or torch) with SIGTERM handler:**
```python
import signal
import sys
import pickle
from pathlib import Path

CHECKPOINT = Path("checkpoint.pkl")

def save_and_exit(signum, frame):
    """Handle SIGTERM from Slurm preemption."""
    print(f"Caught signal {signum}, saving checkpoint...")
    with open(CHECKPOINT, "wb") as f:
        pickle.dump({"iteration": current_iter, "state": model_state}, f)
    sys.exit(0)

signal.signal(signal.SIGTERM, save_and_exit)
signal.signal(signal.SIGUSR1, save_and_exit)

# Resume from checkpoint if it exists
if CHECKPOINT.exists():
    with open(CHECKPOINT, "rb") as f:
        ckpt = pickle.load(f)
    current_iter = ckpt["iteration"]
    model_state = ckpt["state"]
else:
    current_iter = 0
    model_state = initialize()

# Main loop
for i in range(current_iter, total_iterations):
    current_iter = i
    model_state = train_step(model_state)
    # Periodic checkpoint every N iterations
    if i % 100 == 0:
        with open(CHECKPOINT, "wb") as f:
            pickle.dump({"iteration": i, "state": model_state}, f)
```

For PyTorch, replace `pickle.dump` with `torch.save({"epoch": epoch, "model": model.state_dict(), "optimizer": optimizer.state_dict()}, CHECKPOINT)`.

**R (saveRDS) with periodic checkpointing:**
```r
checkpoint_file <- "checkpoint.rds"

# Resume if checkpoint exists
if (file.exists(checkpoint_file)) {
  state <- readRDS(checkpoint_file)
  start_iter <- state$iteration + 1
  results <- state$results
} else {
  start_iter <- 1
  results <- list()
}

for (i in start_iter:total_iterations) {
  results[[i]] <- run_analysis(i)
  # Save checkpoint every 50 iterations
  if (i %% 50 == 0) {
    saveRDS(list(iteration = i, results = results), checkpoint_file)
  }
}
# Final save
saveRDS(list(iteration = total_iterations, results = results), checkpoint_file)
```

**Sbatch script for checkpointable restart-new jobs:**
```bash
#!/bin/bash
#SBATCH --partition=restart-new
#SBATCH --qos=restart
#SBATCH --signal=B:USR1@120    # Send SIGUSR1 120 seconds before kill
#SBATCH --requeue
#SBATCH --time=3-00:00:00

python my_checkpointable_script.py
```

### Fair-Share Awareness

Your scheduling priority depends on recent usage. Heavy consumption lowers your priority for subsequent jobs. Use `sshare` and `hitparade` to understand your current standing:

```bash
# Check your fair-share score (1.0 = idle, approaches 0 with heavy use)
sshare -u $USER

# See cluster-wide utilization by account
hitparade
```

**Recovery strategies when your priority is low:**
- Stop submitting temporarily to let your fair-share score recover.
- Submit tightly-constrained jobs (short walltime, few CPUs) that can backfill into gaps.
- Use `--nice=100` for non-urgent work so it yields to higher-priority users.
- Use `--time-min` to let the scheduler exploit short gaps.

### Local Scratch Storage (/loc)

Each node provides fast local scratch at `/loc`:
- j nodes: 7 TB @ 300 MB/s
- k nodes: 6 TB @ 300 MB/s
- harmony nodes: 3 TB @ 300 MB/s

Use `/loc/scratch/$SLURM_JOB_ID/` for temporary I/O-intensive work. Clean up after your job.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload: short jobs on `short`, long jobs on `campus-new`
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies
- Verify partition choice and resource limits before submitting. Mismatched wall times or partition constraints are a common source of wasted queue time and failed jobs.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
