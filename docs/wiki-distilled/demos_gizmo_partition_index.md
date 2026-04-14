# Gizmo Cluster Partitions

Source: https://sciwiki.fredhutch.org/compdemos/gizmo_partition_index/

## Partition Overview

Slurm partitions organize and associate compute resources with adjustable attributes controlling job limits and scheduling.

| Partition | Guaranteed | Priority | Default Time | Max Time | Limits |
|-----------|-----------|----------|-------------|----------|--------|
| campus-new | Yes | Normal | 3 days | 30 days | 800 cores/account |
| short | Yes | Normal | 1 hour | 12 hours | 8000 core-hours/account |
| interactive | Yes | Higher | 1 day | 7 days | 36 cores/user, 1 GPU/user |
| restart | No | Low | 3 days | 7 days | No limit |
| chorus | Yes | Normal | 1 day | 5 days | 1-4 GPU, 8 CPU max/job |

## Partition Descriptions

**campus-new**: Default general-purpose partition for typical workloads. Flexible allocation parameters.

**short**: For high-volume brief jobs. Limits expressed as committed core-hours per account rather than concurrent core counts, allowing greater parallelism.

**interactive**: Used by `grabnode` for interactive node access. Per-user limits with elevated scheduling priority.

**restart**: Unlimited cores but no runtime guarantees. Jobs may be preempted when higher-priority work needs resources. Good for fault-tolerant workloads.

**chorus**: GPU-capable nodes (harmony). Requires GPU requests in job submissions. Tighter limits due to GPU scarcity (1-4 GPUs, max 8 CPUs per job).
