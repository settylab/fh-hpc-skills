---
description: "Parallel computing patterns on Fred Hutch Gizmo (array jobs, threading, MPI, workflow managers)"
---

# Fred Hutch Parallel Computing

TRIGGER when: user wants to run parallel jobs, asks about job arrays, needs multi-threaded or MPI jobs, wants to parallelize an analysis, or asks about workflow managers on the Gizmo cluster.

## Context

Parallel computing on the Gizmo cluster falls into distinct patterns depending on whether tasks are independent, threaded, or communicating. Choosing the right pattern determines both correctness and efficiency.

## Instructions

### Identify Your Parallel Pattern

**Pleasantly Parallel** (independent tasks, no communication):
Examples: running the same analysis on different samples, simulations with different parameters, per-chromosome analyses.
--> Use **Slurm job arrays** or a **workflow manager**.

**Threaded** (single program, multiple cores on one node):
Examples: multi-threaded alignment (bowtie2 -p), matrix operations, compression.
--> Use `--cpus-per-task`.

**Message Passing** (multiple processes communicating across nodes):
Examples: weather simulations, large-scale distributed computing.
--> Use MPI with `--ntasks`.

### Job Arrays (Pleasantly Parallel)

Run many copies of the same script with different inputs:

```bash
#!/bin/bash
#SBATCH --job-name=array-job
#SBATCH --array=1-100
#SBATCH --cpus-per-task=1
#SBATCH --time=2:00:00
#SBATCH --output=slurm-%A_%a.out

# Each task gets a unique SLURM_ARRAY_TASK_ID (1 through 100)
INPUT_FILE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" input_files.txt)
my_analysis $INPUT_FILE
```

Useful array syntax:
- `--array=1-100` -- tasks 1 through 100
- `--array=1-100%10` -- max 10 running simultaneously
- `--array=1,5,9,13` -- specific task IDs

**Test first, then scale.** If you are already on a compute node (`hostname` returns something other than `rhino*`), test your command directly before submitting anything. Otherwise, run a small subset (`--array=1-3`) and verify outputs before launching the full array. This catches path errors, missing dependencies, and unexpected resource usage early.

**Make arrays resumable.** Structure outputs so each task writes to a predictable path and checks whether it already succeeded. This lets you rerun the full array after fixing a bug without repeating completed work, and makes it trivial to resubmit only the failed indices:
```bash
# Find failed tasks from a completed array job
sacct -j <arrayJobID> --format=JobID%20,State | grep FAILED
# Resubmit only those
sbatch --array=7,23,51 myjob.sh
```

### Multi-threaded Jobs

For applications that use multiple CPU cores on a single node:

```bash
#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=4:00:00

# Use the Slurm variable to set thread count
bowtie2 -p ${SLURM_JOB_CPUS_PER_NODE} -x ref -1 reads_1.fq -2 reads_2.fq -S output.sam

# Or for generic threaded programs:
export OMP_NUM_THREADS=${SLURM_JOB_CPUS_PER_NODE}
my_threaded_program
```

### Multi-task Jobs (srun)

Run independent copies across CPUs:
```bash
# 6 independent copies
srun --ntasks=6 myprogram

# Single copy with 6 CPUs (threading)
srun --ntasks=1 --cpus-per-task=6 myprogram
```

### MPI Jobs

For message-passing programs that communicate across nodes:
```bash
#!/bin/bash
#SBATCH --ntasks=6
#SBATCH --cpus-per-task=1
#SBATCH --time=8:00:00

module load OpenMPI/4.1.1-GCC-11.2.0
srun myprogram
```

### Workflow Managers

For multi-step pipelines with complex dependencies:

- **Nextflow**: Pipeline orchestration with built-in Slurm integration. Fred Hutch maintains a Nextflow Catalog. Nextflow natively supports `-resume`, which skips completed steps on rerun.
- **WDL (Workflow Description Language)**: Supported via Cromwell/PROOF. Fred Hutch maintains a WILDS WDL Library. Cromwell caches completed tasks by default.
- **GNU make**: Simple dependency-based parallelism. Skips targets whose outputs are newer than their inputs.
- **Rslurm**: R package for submitting Slurm jobs from R scripts.

A key advantage of workflow managers over hand-rolled array scripts is built-in support for partial reruns and avoiding redundant computation.

### Reproducible Random Number Generation in Parallel Jobs

Calling `set.seed()` or `np.random.seed()` once is not sufficient in parallel contexts because execution order is not guaranteed. Each parallel task needs its own independent, reproducible PRNG stream.

**Python: Use NumPy SeedSequence.spawn()**
```python
import numpy as np

# Derive independent streams from a single root seed
ROOT_SEED = 42
ss = np.random.SeedSequence(ROOT_SEED)
child_seeds = ss.spawn(100)  # one per worker/task

# Each worker creates its own generator
rng = np.random.default_rng(child_seeds[worker_id])
```

**Python in Slurm array jobs: derive per-task seeds**
```python
import numpy as np
import os

ROOT_SEED = 42
task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])
ss = np.random.SeedSequence(ROOT_SEED)
child_seeds = ss.spawn(int(os.environ.get("SLURM_ARRAY_TASK_COUNT", task_id + 1)))
rng = np.random.default_rng(child_seeds[task_id])
```

**R: Use L'Ecuyer-CMRG with the future framework**
```r
library(future)
library(future.apply)

plan(multisession, workers = 4)
# future.seed = TRUE uses L'Ecuyer-CMRG automatically
results <- future_lapply(1:100, function(i) {
  runif(10)
}, future.seed = TRUE)
```

**R in Slurm array jobs: derive per-task seed**
```r
RNGkind("L'Ecuyer-CMRG")
root_seed <- 42
task_id <- as.integer(Sys.getenv("SLURM_ARRAY_TASK_ID"))
set.seed(root_seed + task_id)
```

Always record the root seed, PRNG algorithm, and number of workers in your logs or metadata. This ensures any result can be reproduced exactly by rerunning the same task with the same seed derivation.

### Key Environment Variables for Parallel Jobs

| Variable | Use |
|----------|-----|
| `SLURM_JOB_CPUS_PER_NODE` | Set thread count in your application |
| `SLURM_ARRAY_TASK_ID` | Current array task index |
| `SLURM_ARRAY_JOB_ID` | Parent array job ID |
| `SLURM_NTASKS` | Total number of tasks |

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use job arrays for independent tasks, not separate sbatch calls
- Set thread counts from Slurm variables, never hardcode
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies
- Review scripts critically before large-scale submission. Double-check array ranges, output paths, and resource requests -- mistakes multiply across hundreds of tasks.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_parallel/
- Slurm examples: https://github.com/FredHutch/slurm-examples
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
