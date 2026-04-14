# Compute Quick Start (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_quickstart/

## Key Facts

- This page is DEPRECATED. Content has moved to /pathways/path-batch-computing/.
- The pathway covers: Slurm fundamentals, creating/obtaining a script, submitting with `sbatch`, and reading output logs.

## Essential Concepts (from pathway)

- **Slurm**: Workload manager used on Fred Hutch's gizmo computing cluster.
- **gizmo**: The computing nodes of the HPC cluster.
- **rhino**: The login nodes for accessing the cluster.
- **Node**: An individual server in the cluster.
- Submit jobs with `sbatch`, output appears as a log file named with the jobID.
- For larger workloads: use Slurm job arrays (homogeneous jobs) or workflow managers (WDL, Nextflow, Cromwell).

## Commands & Examples

```bash
# Download example script from FredHutch/slurm-examples
wget https://github.com/FredHutch/slurm-examples/blob/main/01-introduction/1-hello-world/01.sh

# Submit a job
sbatch 01.sh
```

## Common Pitfalls

- Bookmarks to the old quickstart URL will land on a near-empty redirect page.
- New users should start with the pathway page, not this deprecated page.

## Cross-references

- /pathways/path-batch-computing/ (replacement content)
- /scicomputing/compute_jobs/ (detailed job management)
- https://github.com/FredHutch/slurm-examples (example scripts)
