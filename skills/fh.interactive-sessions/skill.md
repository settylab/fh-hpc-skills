---
description: "Getting interactive sessions on Gizmo cluster nodes using grabnode and srun, including resource flags and session management"
---

# fh.interactive-sessions

TRIGGER when: user asks about interactive sessions, grabnode, getting a shell on gizmo, debugging on compute nodes, or running commands interactively on the cluster.

## Context

Fred Hutch provides two layers of interactive computing. Rhino nodes are shared login nodes for light tasks. Gizmo nodes are the compute cluster, accessed via `grabnode` for dedicated interactive sessions with reserved resources.

## Connecting to the Cluster

```bash
# 1. Connect to a rhino login node (requires VPN if off-campus)
ssh HutchNetID@rhino

# 2. Launch an interactive session on a gizmo compute node
grabnode
```

`grabnode` prompts for:
- **CPUs**: number of cores (default 1, request only what you need)
- **Memory**: RAM in GB
- **Walltime**: how long you need the session
- **GPU**: whether you need GPU access

## grabnode Details

- Uses `srun` internally to allocate resources on the `interactive` partition
- Accepts standard `sbatch` flags for advanced use: `grabnode --mem=16G -c 4`
- Maximum limits: 36 cores, 1 GPU, 3 concurrent interactive jobs per user
- Interactive partition has highest scheduling priority, 7-day max walltime
- Sessions are Slurm jobs and count against your allocation

### Passing sbatch Flags

`grabnode` accepts common sbatch options directly:
```bash
# Request 4 CPUs for 8 hours
grabnode --cpus-per-task=4 --time=08:00:00

# Request a GPU
grabnode --gpus=1

# Request a specific partition with GPU
grabnode --partition=chorus --gpus=1
```

### When to Use grabnode

- Interactive data exploration and debugging
- Testing scripts before submitting batch jobs
- Software compilation that requires compute resources
- Short interactive analyses that exceed rhino capacity

### When NOT to Use grabnode

- Long-running analyses (use `sbatch` instead)
- Jobs that do not require interactive input (use `sbatch`)
- Anything that can be scripted and submitted as a batch job

An idle grabnode session still consumes allocated resources, reducing availability for other users.

### Ending Your Session

Type `exit` or press Ctrl-D to release the node and return to rhino.

## Alternative: Direct srun

```bash
# Allocate a session manually (equivalent to grabnode but less convenient)
srun --partition=interactive --cpus-per-task=4 --mem=16G --time=4:00:00 --pty bash
```

## Troubleshooting

**"Invalid account" error:** Your HutchNet ID is not associated with a PI account on the cluster. Contact SciComp (scicomp@fredhutch.org).

**Session won't start:** Resources may be fully allocated. Try requesting fewer CPUs/memory, or check cluster utilization with `squeue` and `sinfo`.

**Connection dropped:** Reconnect to rhino and run `grabnode` again. Previous session may still be running; check with `squeue -u $USER` and cancel if needed with `scancel <jobid>`.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Release nodes promptly when done (do not leave idle sessions open)
- Do not run compute-heavy work directly on rhino login nodes
- Use `grabnode` for development/testing, then convert to batch jobs for production runs
- Use `sbatch` for non-interactive work instead of grabnode

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/pathways/path-grab/
- Interactive sessions: https://sciwiki.fredhutch.org/pathways/path-interactive/
- Compute platforms: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/
