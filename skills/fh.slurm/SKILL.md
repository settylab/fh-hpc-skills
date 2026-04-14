---
description: "Submitting and managing Slurm jobs on the Fred Hutch Gizmo cluster (sbatch, srun, scancel, squeue, sacct, job arrays, workflow managers)"
---

# Fred Hutch Slurm Job Management

TRIGGER when: user wants to submit a batch job, check job status, cancel a job, view job history, write an sbatch script, use job arrays, or troubleshoot Slurm errors on the Fred Hutch HPC cluster.

## Context

Fred Hutch uses Slurm as its workload manager on the Gizmo cluster. Jobs are submitted from the `rhino` login nodes and run on `gizmo` compute nodes. Every user is associated with a PI account (format: `lastname_f`, e.g., `setty_m`) that governs resource limits and fair-share scheduling. Accounts are organized under division codes (e.g., bs=Basic Sciences, cb=Computational Biology, vi=Virology). Check your account with `sacctmgr show user $USER withassoc format=User,Account`.

## Instructions

### Submitting Jobs

Use `sbatch` to submit a job script. The script should contain `#SBATCH` directives:

```bash
#!/bin/bash
#SBATCH --job-name=myjob
#SBATCH --cpus-per-task=4
#SBATCH --time=1-00:00:00
#SBATCH --partition=campus-new
#SBATCH --output=slurm-%j.out
#SBATCH --mail-user=user@fredhutch.org
#SBATCH --mail-type=END,FAIL

# Initialize module system in scripts
source /app/lmod/lmod/init/profile
module load Python/3.11.3-GCCcore-12.3.0

python my_analysis.py
```

Submit with: `sbatch myscript.sh`

For quick one-off commands, use `srun` (blocks until complete):
```bash
srun --cpus-per-task=4 --time=02:00:00 my_command
```

### Common sbatch Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `-c` / `--cpus-per-task` | CPUs per task | `-c 4` |
| `-n` / `--ntasks` | Number of tasks | `-n 1` |
| `-t` / `--time` | Wall time (D-HH:MM:SS) | `-t 1-00:00:00` |
| `--time-min` | Minimum useful time (enables backfill) | `--time-min=2:00:00` |
| `-p` / `--partition` | Partition | `-p campus-new` |
| `-J` / `--job-name` | Job name | `-J alignment` |
| `-o` / `--output` | Output file | `-o slurm-%j.out` |
| `--mem` | Memory (K/M/G/T) | `--mem=16G` |
| `--gpus` | GPUs | `--gpus=1` |
| `-A` / `--account` | PI account | `-A lastname_f` |
| `--nice` | Lower scheduling priority | `--nice=100` |
| `--mail-user` | Email address | |
| `--mail-type` | Events: BEGIN,END,FAIL,ALL | |

### Backfill Scheduling with --time-min

Shorter jobs are more likely to start quickly because the scheduler can backfill them into gaps. If your job can make useful progress in less than the maximum wall time, use `--time-min` alongside `--time` to let the scheduler know:

```bash
# Job needs at most 24h, but can do useful work in as little as 2h
sbatch --time=1-00:00:00 --time-min=2:00:00 myjob.sh
```

The scheduler may start the job in a 4-hour gap it would otherwise skip, allocating somewhere between `--time-min` and `--time`. This is especially useful for checkpointable workloads on `campus-new`.

### Memory at Fred Hutch

Memory is advisory. Slurm ensures nodes have enough installed RAM but does not enforce per-job limits. Rule of thumb: request 1 CPU for every 4 GB of memory needed if exceeding 4 GB. Default unit is megabytes; always specify G for gigabytes.

### Monitoring Jobs

```bash
# View your queued/running jobs
squeue -u $USER

# View all jobs in a partition
squeue -p campus-new

# Cluster-wide summary by user/account
hitparade

# Detailed job info
scontrol show job <jobID>

# Resource usage of a running job
sstat -j <jobID>

# Historical job info (after completion)
sacct -j <jobID> --format=JobID,JobName,Partition,State,ExitCode,Elapsed,MaxRSS
```

**Limit squeue polling.** Scripts or monitoring loops that call `squeue` should sleep at least 30-60 seconds between calls. Tight polling (every few seconds) stresses the Slurm controller and can degrade scheduling for everyone on the cluster.

### Resource Profiling with sacct

After a job completes, use `sacct` to measure actual resource consumption before scaling up. This prevents over-requesting CPUs, memory, or walltime on production runs.

```bash
# One-off profiling of a completed job
sacct -j <jobID> --format=JobID%20,JobName,Elapsed,State,ExitCode,MaxRSS,AllocCPUS,AllocTRES%32

# Recommended: add this to ~/.bashrc or ~/.zshrc for consistent output
export SACCT_FORMAT="JobID%20,JobName,User,Partition,Elapsed,State,ExitCode,MaxRSS,AllocTRES%32"
```

With `SACCT_FORMAT` set, a bare `sacct -j <jobID>` gives you everything you need for post-mortem analysis. Profile a representative test job, then add a 15-20% buffer for production runs.

### Modifying and Canceling Jobs

```bash
# Cancel a job
scancel <jobID>

# Cancel all your jobs
scancel -u $USER

# Extend wall time of a running job by 2 days
scontrol update jobid=<jobID> timelimit=+2-0

# Lower priority for non-urgent work
sbatch --nice=100 myscript.sh
```

### Job Arrays

Run the same script many times with different inputs:
```bash
#!/bin/bash
#SBATCH --array=1-100
#SBATCH --cpus-per-task=1
#SBATCH --time=4:00:00
#SBATCH --output=slurm-%A_%a.out

# $SLURM_ARRAY_TASK_ID gives the current index (1 through 100)
python process.py --sample $SLURM_ARRAY_TASK_ID
```

**Test before scaling.** Always run a small subset first to catch errors early. If you are already on a compute node (`hostname` returns something other than `rhino*`), you can test commands directly without submitting a job. Otherwise:
```bash
# Test with 3 tasks before submitting the full array
sbatch --array=1-3 myjob.sh
# Check outputs, then submit the rest
sbatch --array=4-100 myjob.sh
```

**Skip completed work.** When rerunning after partial failure or code changes that only affect a subset, avoid repeating work that already succeeded:
```bash
#!/bin/bash
#SBATCH --array=1-100

OUTFILE="results/sample_${SLURM_ARRAY_TASK_ID}.csv"
if [ -f "$OUTFILE" ]; then
    echo "Output exists, skipping task $SLURM_ARRAY_TASK_ID"
    exit 0
fi
python process.py --sample $SLURM_ARRAY_TASK_ID --output "$OUTFILE"
```

Alternatively, resubmit only the failed tasks:
```bash
# Find which tasks failed from sacct
sacct -j <arrayJobID> --format=JobID,State | grep FAILED
# Resubmit only those (e.g., tasks 7,23,51)
sbatch --array=7,23,51 myjob.sh
```

### Array Job Pitfalls

**Off-by-one errors.** `SLURM_ARRAY_TASK_ID` starts at whatever you specify in `--array`. If your input files are zero-indexed (`file_0.txt` through `file_9.txt`), use `--array=0-9`, not `--array=1-10`. Mismatches silently process the wrong files or fail on missing inputs.

**Stable task-to-config mapping.** If you read parameters from a config file using `SLURM_ARRAY_TASK_ID` as a line index, that mapping must not change while jobs are pending or running. Adding or removing lines from the config file while an array is in flight will silently corrupt results. Snapshot your config file before submission:
```bash
cp params.tsv params_jobXXX.tsv   # freeze before submitting
# In job script, read from the frozen copy
```

**Check exit codes.** A failed array task produces empty or truncated output. Downstream steps that consume these outputs without checking will run on garbage. Always verify after an array completes:
```bash
# Check for any non-zero exit codes
sacct -j <arrayJobID> --format=JobID%20,State,ExitCode | grep -v "COMPLETED.*0:0"
```

### Job Dependency Chaining

Chain multi-step pipelines so each stage starts only after the previous one succeeds:

```bash
# Submit step 1
JOB1=$(sbatch --parsable step1.sh)

# Step 2 starts only after step 1 succeeds
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 step2.sh)

# Step 3 after step 2
sbatch --dependency=afterok:$JOB2 step3.sh
```

Dependency types: `afterok` (success), `afternotok` (failure, for cleanup), `afterany` (regardless of exit code), `after` (after start). For array jobs, `aftercorr` runs each task only after the corresponding task in the previous array completes.

For complex multi-step pipelines, consider a workflow manager (Nextflow, Cromwell/WDL) instead of manual dependency chains. Workflow managers handle retries, caching, and partial reruns automatically.

### Preemptible (Restart) Jobs

Access all idle cluster CPUs with no limits, but jobs can be killed and requeued without notice:
```bash
sbatch --partition=restart-new --qos=restart myjob.sh
```
Only use this for workloads that are either idempotent (safe to rerun from scratch) or checkpointable. For long-running computations, write periodic checkpoints so the job can resume where it left off:
```bash
#!/bin/bash
#SBATCH --partition=restart-new
#SBATCH --qos=restart
#SBATCH --signal=B:USR1@120  # Signal 120s before kill

CHECKPOINT="checkpoint.pt"

# Handle preemption signal
trap 'echo "Preempted, saving..."; python save_checkpoint.py; exit 0' USR1

# Resume from checkpoint if it exists
python train.py --checkpoint "$CHECKPOINT"
```

### Job Output

By default, stdout and stderr are captured in `slurm-<jobID>.out` in the submission directory. Customize with `-o` and `-e` flags.

### Slurm Environment Variables

Use these inside your job scripts:
- `$SLURM_JOB_ID` -- job identifier
- `$SLURM_CPUS_ON_NODE` -- allocated cores
- `$SLURM_JOB_CPUS_PER_NODE` -- CPUs per node
- `$SLURM_MEM_PER_CPU` -- memory per CPU in MB
- `$SLURM_JOB_NODELIST` -- allocated node names
- `$SLURM_SUBMIT_DIR` -- submission directory
- `$SLURMD_NODENAME` -- current node hostname
- `$SLURM_ARRAY_TASK_ID` -- array index (in job arrays)

```bash
# Example: pass allocated cores to a tool
bowtie2 -p $SLURM_CPUS_ON_NODE -x index -U reads.fq -S output.sam
```

### Workflow Managers

For multi-step pipelines, Fred Hutch recommends Nextflow or WDL (Cromwell) rather than manually chaining sbatch scripts.

### Troubleshooting Pending Jobs

| Pending Reason | Meaning |
|----------------|---------|
| Priority | Waiting behind higher-priority jobs |
| Resources | Not enough resources currently available |
| PartitionTimeLimit | Requested time exceeds partition max |
| MaxCpuPerAccount | PI account at CPU limit |
| MaxGRESPerAccount | PI account at GPU limit |

## Principles

- Request only the resources you need (CPUs, memory, time). Over-requesting wastes cluster capacity and delays your own jobs via fair-share.
- Use appropriate partitions for your workload (see fh.partitions skill).
- Use `--nice=100` for non-urgent batch work to be a good cluster citizen.
- Respect shared infrastructure and other users.
- Use versioned environments for reproducibility (always pin module versions in scripts).
- Always initialize the module system in bash scripts: `source /app/lmod/lmod/init/profile`
- Check job output files for errors after completion.
- Convert repeated interactive commands into batch scripts.
- Review job scripts critically before submission. Verify paths, resource requests, and logic are correct -- a mistyped output path or wrong array range can waste hours of cluster time and produce misleading results.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
- Batch computing pathway: https://sciwiki.fredhutch.org/pathways/path-batch-computing/
- Slurm examples: https://github.com/FredHutch/slurm-examples
- SchedMD Slurm docs: https://slurm.schedmd.com/documentation.html
