# Parallel Computing (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_parallel/

## Key Facts

### Parallel Workload Classification

- **Pleasantly Parallel**: Independent steps with no dependencies. Examples: simulations, GWAS, chromosome-by-chromosome analyses. Best fit for Slurm job arrays.
- **Sequential**: Each step depends on the previous step. Nearly impossible to speed up with additional processors.
- **Highly Connected**: Steps communicate with neighboring steps. Requires low-latency communication (MPI). Examples: weather forecasts, climate simulations.

### Parallel Techniques

1. **Workflow Managers**: Nextflow, WDL for orchestrating multi-step pipelines.
2. **Task Marshaling**: Rslurm (R package), GNU make for coordinating independent tasks.
3. **Threading**: Multiple cores on a single node (OpenMP, multi-threaded libraries).
4. **Message Passing (MPI)**: Communication across multiple nodes.

### Slurm Parallel Job Patterns

```bash
# Run 6 independent copies across different CPUs (pleasantly parallel)
srun --ntasks=6 myprogram

# Run single copy with 6 CPUs (threaded application)
srun --ntasks=1 --cpus-per-task=6 myprogram

# Run MPI program across 6 tasks
srun --ntasks=6 --cpus-per-task=1 mpirun myprogram
```

### Key Environment Variable

`SLURM_JOB_CPUS_PER_NODE` contains the allocated CPU core count. Use it in your scripts:
```bash
bowtie2 -p ${SLURM_JOB_CPUS_PER_NODE} ...
```

## Common Pitfalls

- Requesting multiple tasks when a threaded application only needs multiple CPUs per task.
- Not using `$SLURM_JOB_CPUS_PER_NODE` to pass core count to applications (hardcoding instead).
- Attempting MPI jobs without proper module setup.
- Not distinguishing between pleasantly parallel (use arrays) and threaded (use cpus-per-task) workloads.

## Cross-references

- /scicomputing/compute_jobs/ (job submission basics)
- https://github.com/FredHutch/slurm-examples (community examples)
