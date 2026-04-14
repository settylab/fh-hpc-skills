# Run a Non-Interactive (Batch) Job on Gizmo

Source: https://sciwiki.fredhutch.org/pathways/path-batch-computing/

## Key Facts

- SLURM is the workload manager for the gizmo computing cluster
- `sbatch` submits a job script and returns immediately; `srun` blocks until execution completes
- Job arrays handle thousands of homogeneous jobs; workflow managers (WDL, Nextflow) handle multi-step analyses
- Output goes to `slurm-<jobid>.out` by default; use `-o` flag with `%j` for custom naming
- Memory is advisory: request 1 CPU for every 4GB needed if exceeding 4GB
- Memory units: append K, M, G, or T (default is megabytes)

## Commands & Examples

```bash
# Get a sample script from Fred Hutch examples
wget https://github.com/FredHutch/slurm-examples/blob/main/01-introduction/1-hello-world/01.sh

# Submit a basic batch job
sbatch myscript.sh

# Submit with specific resources
sbatch -c 6 --mem=24G -t 2-00:00:00 myscript.sh

# Redirect output
sbatch -o myjob-%j.out myscript.sh

# Common SBATCH directives in a script header
#!/bin/bash
#SBATCH -c 4                           # 4 CPUs
#SBATCH --mem=16G                      # 16 GB memory
#SBATCH -t 1-00:00:00                  # 1 day walltime
#SBATCH -J my_job_name                 # Job name
#SBATCH -o my_job-%j.out               # Output file
#SBATCH --mail-user=you@fredhutch.org  # Email notifications
#SBATCH --mail-type=END                # Notify on completion

# Monitor and manage jobs
squeue -u $USER                        # View your jobs
scancel <jobid>                        # Cancel a job
scancel -u $USER                       # Cancel all your jobs
sstat -a -j <jobid>                    # Monitor resource usage
hitparade                              # Cluster usage summary

# Adjust walltime on a running job
scontrol update jobid=<id> timelimit=+2-0

# Use restart/preemptible partition
sbatch --partition=restart-new --qos=restart myjob.sh

# Lower priority (nice) for non-urgent jobs
sbatch --nice=100 myscript.sh
```

## SLURM Environment Variables (available inside batch scripts)

- `SLURM_CPUS_ON_NODE` -- cores allocated on this node
- `SLURM_JOB_ID` -- job identifier
- `SLURM_MEM_PER_CPU` -- memory per CPU in MB
- `SLURM_JOB_NODELIST` -- allocated node names
- `SLURM_SUBMIT_DIR` -- directory job was submitted from
- `SLURMD_NODENAME` -- current node hostname

## Common sbatch Options

| Option | Purpose |
|--------|---------|
| `-p` | Change partition |
| `-t` | Request walltime |
| `-n` | Number of tasks (default: 1) |
| `-c` | CPUs per task (default: 1) |
| `-J` | Job name |
| `--qos` | Quality of Service |
| `-o` | Output file |
| `--mem` | Memory requirement |

## Common Pitfalls

- Using `wget` with the GitHub HTML URL instead of the raw URL for scripts
- Not requesting enough memory and having jobs killed silently
- Not checking job output files for errors after completion
- Requesting excessive resources (delays scheduling, wastes allocation)
- Forgetting that `--mem` default unit is megabytes, not gigabytes

## Cross-references

- SLURM job management: /scicomputing/compute_jobs/
- Parallel computing: /scicomputing/compute_parallel/
- Workflow managers (Nextflow, WDL): /scicomputing/compute_platforms/
- Fred Hutch slurm-examples repo: https://github.com/FredHutch/slurm-examples
