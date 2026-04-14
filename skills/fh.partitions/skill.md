---
description: "Gizmo cluster partitions guide (campus-new, short, restart-new, chorus, interactive) with limits and node specs"
---

# Fred Hutch Gizmo Partitions

TRIGGER when: user asks which partition to use, wants to know partition limits, encounters partition-related errors, or needs to understand node generations on the Gizmo cluster.

## Context

For a quick overview of all cluster resources, see fh.cluster-overview.

The Gizmo cluster organizes compute nodes into partitions. Each partition has different time limits, resource limits, and node types. Choosing the right partition affects how quickly your job starts and how long it can run.

## Instructions

### Partition Overview

| Partition | Max Wall Time | Node Gens | Notes |
|-----------|---------------|-----------|-------|
| **campus-new** | 30 days (default 3 days) | j, k | Default partition (QOS: public). Good for most workloads. |
| **short** | 12 hours (default 1 hour) | j, k | Same nodes as campus-new, 2-min overtime grace. Quick jobs. |
| **restart-new** | 30 days (default 3 days) | j, k | Preemptible (REQUEUE). Lowest priority. Requires `--qos=restart`. |
| **chorus** | 7 days (default 4 hours) | harmony | AMD EPYC nodes with L40S GPUs. Max 8 CPUs per QOS. |
| **interactive** | 7 days (default 1 day) | j, k | For interactive sessions via `grabnode`. Highest priority. |
| **canto** | 7 days (default 4 hours) | canto | High-memory nodes with 1.5 TB RAM. |

### Node Specifications

| Generation | Count | CPU | Cores/Node | Memory/Node | Partitions |
|-----------|-------|-----|------------|-------------|------------|
| j | 37 | Intel Gold 6146 | 24 | 384 GB | campus-new, short, interactive |
| k | 161 | Intel Gold 6154 | 36 | 768 GB | campus-new, short, interactive |
| harmony | 8 | AMD EPYC 9354P | 32 | 1536 GB | chorus |
| canto | 3 | AMD or Intel | 36 | 1540 GB | canto |

### Decision Guide

**"My job runs in a few hours"** --> Use `short` partition for faster scheduling:
```bash
sbatch -p short -t 4:00:00 myjob.sh
```

**"My job runs for days"** --> Use `campus-new` (default). Set wall time explicitly:
```bash
sbatch -t 7-00:00:00 myjob.sh
```

**"I need massive resources and can checkpoint"** --> Use `restart-new`:
```bash
sbatch --partition=restart-new --qos=restart myjob.sh
```

**"I need L40S GPUs or 1.5 TB RAM"** --> Use `chorus`:
```bash
sbatch --partition=chorus --gpus=1 myjob.sh
```
Remember to `module purge` and load fresh modules inside your script because harmony nodes run a different OS.

**"I need an interactive terminal on a compute node"** --> Use `grabnode` (see fh.interactive-sessions skill). The interactive partition runs on the same j/k nodes as campus-new but with the highest scheduling priority (PriorityTier=30000).

### Chorus Partition Special Requirements

Harmony nodes use AMD EPYC processors and a different OS than j/k nodes. Environment modules from rhino/gizmo may not work. In your job script:

```bash
#!/bin/bash
#SBATCH --partition=chorus
#SBATCH --gpus=1

# CRITICAL: purge rhino modules and load chorus-compatible ones
module purge
module load <chorus-compatible-module>

your_command_here
```

### Local Scratch Storage (/loc)

Each node provides fast local scratch at `/loc`:
- j nodes: 7 TB @ 300 MB/s
- k nodes: 6 TB @ 300 MB/s
- harmony nodes: 3 TB @ 300 MB/s

Use `/loc/scratch/$SLURM_JOB_ID/` for temporary I/O-intensive work. Clean up after your job.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload: short jobs on `short`, long jobs on `campus-new`
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_jobs/
