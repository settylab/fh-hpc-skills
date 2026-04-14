# fh.cluster-overview

Current Gizmo cluster specs, partitions, and resource limits. Verified against the live cluster on 2026-04-13.

## When to Use

Use this skill when a user asks about Fred Hutch HPC resources, partition limits, GPU availability, node specs, or how to choose the right partition for their workload.

## Cluster: Gizmo

Slurm-managed HPC cluster at Fred Hutchinson Cancer Center. ~209 compute nodes across 6 partitions.

## Partitions at a Glance

| Partition | Max Time | Nodes | CPUs | RAM | GPU | Use Case |
|---|---|---|---|---|---|---|
| **campus-new** (default) | 30 days | 198 | 24-36 | 350-700 GB | 1x 1080Ti or 2080Ti | General batch jobs |
| **short** | 12 hours | 198 | 24-36 | 350-700 GB | 1x 1080Ti or 2080Ti | Quick jobs, faster scheduling |
| **restart-new** | 30 days | 198 | 24-36 | 350-700 GB | 1x 1080Ti or 2080Ti | Preemptible/scavenger, can be killed |
| **interactive** | 7 days | 198 | 24-36 | 350-700 GB | 1x 1080Ti or 2080Ti | Via `grabnode`, highest priority |
| **chorus** | 7 days | 8 | 32 | ~1.5 TB | 4x L40S | Multi-GPU / large model training |
| **canto** | 7 days | 3 | 36 | ~1.5 TB | 1x 2080Ti | High-memory workloads |

For detailed partition specs, node hardware, and decision guide, see the fh.partitions skill.

## Node Hardware

**J-class (gizmoj, 37 nodes):** 24 cores, 350 GB RAM, 1x GTX 1080 Ti (11 GB VRAM).
**K-class (gizmok, 161 nodes):** 36 cores, 700 GB RAM, 1x RTX 2080 Ti (11 GB VRAM).
**Harmony (8 nodes):** 32 cores, ~1.5 TB RAM, 4x L40S (48 GB VRAM each, 192 GB per node). Chorus partition.
**Canto (3 nodes):** 36 cores, ~1.5 TB RAM, 1x RTX 2080 Ti.

## Choosing a Partition

**Need a quick test run?** Use `short` (12h max, fast scheduling).
**Standard batch work?** Use `campus-new` (default, up to 30 days).
**Interactive/debugging?** Use `grabnode` which targets the `interactive` partition.
**Checkpointable long job?** Use `restart-new` for scavenger priority (jobs may be preempted and requeued).
**Multi-GPU or large models?** Use `chorus` to get up to 4x L40S GPUs per node.
**High-memory (>700 GB)?** Use `canto` or `chorus` for ~1.5 TB RAM nodes.

## GPU Summary

| GPU | VRAM | Nodes | Partition |
|---|---|---|---|
| GTX 1080 Ti | 11 GB | 37 (J-class) | campus-new, short, interactive, restart-new |
| RTX 2080 Ti | 11 GB | 161 (K-class) + 3 (canto) | campus-new, short, interactive, restart-new, canto |
| L40S | 48 GB | 8 (harmony) | chorus |

Total GPUs: 198 (campus-new) + 32 (chorus) + 3 (canto) = 233.

## Resource Limits

Per campus-new partition: MaxCPUsPerNode=36, MaxMemPerNode=~774 GB.
Interactive (grabnode) limits: 36 cores max, 1 GPU max, 3 concurrent jobs per user.

## Quick Commands

```bash
grabnode                              # Interactive session
sbatch --partition=campus-new job.sh  # Submit batch job (default partition)
sbatch --partition=short job.sh       # Quick job (<12h)
sbatch --partition=chorus --gres=gpu:l40s:4 job.sh  # Multi-GPU on chorus
squeue -u $USER                       # Check your jobs
sinfo -o "%P %D %c %m %G"            # Partition overview
```

## Key Paths

```
/fh/fast/<pi>/user/<you>/    # Primary working storage (NFS, persistent, backed up)
/hpc/temp/<pi>/<you>/        # Temp scratch (NFS4, 30-day auto-delete, free)
$SCRATCH_LOCAL (/loc/scratch) # Job-local SSD (fastest I/O, destroyed at job end)
/fh/working/<pi>/            # Working copies (NFS, no auto-purge, 20TB default)
/app/modules/all/            # Software modules
# NOTE: /fh/scratch/ is deprecated and no longer mounted. Use /hpc/temp/ instead.
```
