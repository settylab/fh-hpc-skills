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

- **Nextflow**: Pipeline orchestration with built-in Slurm integration. Fred Hutch maintains a Nextflow Catalog.
- **WDL (Workflow Description Language)**: Supported via Cromwell/PROOF. Fred Hutch maintains a WILDS WDL Library.
- **GNU make**: Simple dependency-based parallelism.
- **Rslurm**: R package for submitting Slurm jobs from R scripts.

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

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_parallel/
- Slurm examples: https://github.com/FredHutch/slurm-examples
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
