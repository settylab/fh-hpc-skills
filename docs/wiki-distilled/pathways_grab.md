# Getting an Interactive Session on a Gizmo Node

Source: https://sciwiki.fredhutch.org/pathways/path-grab/

## Key Facts

- `grabnode` is the primary method to get an interactive session on a gizmo compute node
- It prompts for: number of cores, memory amount, and estimated time required
- It runs from any rhino login node and uses `srun` internally
- It accepts common `sbatch` options and flags beyond the interactive prompts
- Interactive sessions are subject to Slurm allocation policies that can cause startup delays
- "Invalid account" errors mean your HutchNet ID lacks PI account association; contact SciComp

## Commands & Examples

```bash
# Connect to a rhino login node first
ssh HutchNetID@rhino

# Launch an interactive session on gizmo
grabnode
# Prompts for: cores (default 1), memory, walltime

# grabnode also accepts sbatch-style flags
grabnode --mem=16G -c 4
```

## Common Pitfalls

- Running compute-heavy work directly on rhino instead of using grabnode
- Requesting more resources than needed, which delays allocation
- Not understanding that grabnode sessions are Slurm jobs and count against your allocation
- Forgetting to exit the grabnode session when done (holds resources idle)

## Cross-references

- Interactive sessions overview: /pathways/path-interactive/
- Batch computing: /pathways/path-batch-computing/
- Compute platforms (node specs): /scicomputing/compute_platforms/
- Job management: /scicomputing/compute_jobs/
