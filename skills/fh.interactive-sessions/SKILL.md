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

`grabnode` prompts interactively for four parameters in order:

1. **CPUs/cores** — "How many CPUs/cores would you like to grab on the node? [1-36]"
2. **Memory (GB)** — "How much memory (GB) would you like to grab? [default]"
   Default = cores × 20 GB, capped at 683 GB
3. **Days** — "Please enter the max number of days you would like to grab this node: [1-7]"
   Default = 1 day
4. **GPU** — "Do you need a GPU? [y/N]"
   Default = no GPU

Before prompting, it shows your existing interactive sessions via `squeue`.

## grabnode Details

- Uses `srun --pty` internally to allocate resources on the `interactive` partition
- Passes any extra command-line arguments directly to `srun` (standard Slurm flags)
- Maximum limits: 36 cores, 683 GB memory, 1 GPU, 7 days, 3 concurrent interactive jobs per user
- Interactive partition has highest scheduling priority (PriorityTier=30000)
- Sessions are Slurm jobs and count against your allocation
- X11 forwarding is enabled automatically if `$DISPLAY` is set

### Passing Extra Slurm Flags

`grabnode` passes trailing arguments through to `srun`:
```bash
# Request a specific partition
grabnode --partition=chorus

# Any valid srun flag works
grabnode --constraint=<feature>
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
- Do not run compute-heavy work directly on rhino login nodes (see `fh.shared-nodes` for multi-tenant etiquette, including the settylab `barnacle` pattern on `gizmok1`)
- Use `grabnode` for development/testing, then convert to batch jobs for production runs
- Use `sbatch` for non-interactive work instead of grabnode
- Validate job scripts on a small input before submitting large batch runs. If you are already on a compute node (check `hostname` — anything other than `rhino*` means you are on a compute node), you can test commands directly using the node's resources. Otherwise, use `grabnode` interactively or submit a short `sbatch --array=1-1 -p short` test job.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/pathways/path-grab/
- Interactive sessions: https://sciwiki.fredhutch.org/pathways/path-interactive/
- Compute platforms: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/
