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
| `-p` / `--partition` | Partition | `-p campus-new` |
| `-J` / `--job-name` | Job name | `-J alignment` |
| `-o` / `--output` | Output file | `-o slurm-%j.out` |
| `--mem` | Memory (K/M/G/T) | `--mem=16G` |
| `--gpus` | GPUs | `--gpus=1` |
| `-A` / `--account` | PI account | `-A lastname_f` |
| `--nice` | Lower scheduling priority | `--nice=100` |
| `--mail-user` | Email address | |
| `--mail-type` | Events: BEGIN,END,FAIL,ALL | |

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

# $SLURM_ARRAY_TASK_ID gives the current index (1 through 100)
python process.py --sample $SLURM_ARRAY_TASK_ID
```

### Preemptible (Restart) Jobs

Access all idle cluster CPUs with no limits, but jobs can be killed without notice:
```bash
sbatch --partition=restart-new --qos=restart myjob.sh
```
Only use this for checkpointable or easily re-runnable workloads.

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

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
- Batch computing pathway: https://sciwiki.fredhutch.org/pathways/path-batch-computing/
- Slurm examples: https://github.com/FredHutch/slurm-examples
- SchedMD Slurm docs: https://slurm.schedmd.com/documentation.html
