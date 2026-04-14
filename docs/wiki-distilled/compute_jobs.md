# Job Management (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/

## Key Facts

### Slurm Commands

**Job Submission:**
- `sbatch <script>` -- submits job script, returns immediately with job ID
- `srun <command>` -- immediately executes task, blocks terminal until complete
- `grabnode` -- Fred Hutch-specific command to allocate an interactive terminal on a compute node

**Job Management:**
- `squeue` -- displays running and queued jobs
- `scancel <jobid>` -- signals or terminates jobs
- `salloc` -- obtains job allocation, executes command, releases allocation
- `sstat` -- monitors resource usage of running jobs
- `scontrol` -- modifies job parameters
- `sprio` -- shows job priority factors
- `sacct` -- reviews historical job information
- `hitparade` -- Fred Hutch-specific summary of cluster jobs by user/account

### Common sbatch Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `-p <partition>` | Select partition | campus-new |
| `-t <time>` | Wall time limit | partition default |
| `-n <tasks>` | Number of tasks | 1 |
| `-c <cpus>` | CPUs per task | 1 |
| `-J <name>` | Job name | script name |
| `--qos <qos>` | Quality of Service | (none) |
| `-o <file>` | Redirect stdout | slurm-[jobid].out |
| `--mem <amount>` | Memory request (K/M/G/T) | (advisory) |
| `--nice=<adj>` | Adjust priority | 0 |
| `--mail-user=<email>` | Email notifications | (none) |
| `--mail-type=<type>` | Notification events (BEGIN, END, FAIL, ALL) | (none) |
| `-M <cluster>` | Specify cluster | gizmo |
| `-u <user>` | Filter by username (squeue) | -- |
| `-A <account>` | Filter/set account | PI account |
| `--gpus=<n>` | Request GPUs | 0 |

### Memory Management

Memory is NOT scheduled by Slurm at Fred Hutch (advisory only). Rule of thumb: request one CPU for every 4 GB of memory required for memory-intensive jobs.

### Partitions

| Partition | Default Wall Time | Max Wall Time | Notes |
|-----------|-------------------|---------------|-------|
| campus-new | 3 days | 30 days | Default partition |
| short | -- | <12 hours | Higher core limit |
| restart-new | -- | -- | No limits, preemptible (jobs killed without notice when higher-priority jobs wait) |
| chorus | -- | -- | harmony nodes only (AMD EPYC, L40S GPUs) |

### Preemptible (Restart) Jobs

Submit with both partition and QOS:
```bash
sbatch --partition=restart-new --qos=restart myjob.sh
```
Jobs can be terminated without notice if high-priority jobs are waiting. Every idle CPU is available.

### Slurm Environment Variables

| Variable | Description |
|----------|-------------|
| `SLURM_CPUS_ON_NODE` | Cores allocated on current node |
| `SLURM_JOB_ID` | Primary job identifier |
| `SLURM_MEM_PER_CPU` | Memory per CPU in MB |
| `SLURM_JOB_NODELIST` | Allocated node names |
| `SLURM_SUBMIT_DIR` | Directory from which job was submitted |
| `SLURMD_NODENAME` | Current node hostname |
| `SLURM_JOB_CPUS_PER_NODE` | CPUs per node for this job |

### Job Output

stdout and stderr are captured and written to `slurm-[jobid].out` in the submission directory by default.

### Common Failure Reasons

| Reason | Cause |
|--------|-------|
| Priority | Waiting for higher-priority jobs |
| Resources | Insufficient compute resources available |
| PartitionTimeLimit | Wall time exceeds partition maximum |
| MaxCpuPerAccount | PI account at CPU limit |
| MaxGRESPerAccount | PI account at GPU limit |
| QOSMinCpuNotSatisfied | Not enough CPUs requested for QOS |
| QOSMinMemory | Not enough memory requested for QOS |
| MaxMemPerLimit | Exceeds partition memory limit |

### Key Concepts

- **Account**: PI account for resource enforcement; distinct from HutchNet ID.
- **Priority**: Fair-share algorithm based on historical resource usage.
- **QOS (Quality of Service)**: Mechanism for requesting special scheduling features.
- **Limits**: CPU maximums per account/user ensure equitable access.

## Commands & Examples

```bash
# Submit a 6-core job
sbatch -c 6 myscript.sh my-output

# Submit preemptible job
sbatch --partition=restart-new --qos=restart myjob.sh

# Extend a running job by 2 days
scontrol update jobid=<jobID> timelimit=+2-0

# Email notification directives
#SBATCH --mail-user=fred@fredhutch.org
#SBATCH --mail-type=END

# Check queue
squeue -u $USER

# View job history
sacct -j <jobID>
```

## Common Pitfalls

- Forgetting that memory is advisory-only; use CPU count as a proxy for memory allocation.
- Not specifying wall time and hitting the partition default/maximum.
- Using restart-new partition without checkpointing (jobs can be killed at any time).
- Not checking `sacct` for job failure diagnostics.

## Cross-references

- /scicomputing/compute_platforms/ (node specs and partitions)
- /scicomputing/compute_parallel/ (parallel job patterns)
- /scicomputing/compute_gpu/ (GPU job submission)
- https://github.com/FredHutch/slurm-examples (example scripts)
