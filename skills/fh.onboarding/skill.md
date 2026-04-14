---
description: "New user onboarding checklist for Fred Hutch computational resources"
---

# Fred Hutch HPC Onboarding

TRIGGER when: user is new to Fred Hutch computing, asks about getting started, or needs orientation to HPC resources

## Context

New Fred Hutch research community members need to set up access to computing resources, understand the cluster architecture, and learn key tools and policies. This guide provides the essential first steps.

## Instructions

### Step 1: Get Connected

- Join Fred Hutch Slack with your @fredhutch.org email (no invitation needed). Consortium members at UW and Children's Hospital are also welcome.
- Key Slack channels: #scicomp-general, #nextflow, #wiki-contributors

### Step 2: Understand the Infrastructure

- **Rhino**: Shared login nodes for light interactive work, prototyping, job submission. 3 nodes (rhino01-03) via round-robin SSH. Do NOT run compute-intensive tasks here (1,000 CPU-second limit).
- **Gizmo**: Compute cluster for actual work. Access via `grabnode` (interactive) or `sbatch` (batch).
- **Storage**: `/fh/fast/` (fast, primary), Economy Cloud (S3 buckets, accessed via `aws s3`), `/hpc/temp/` (temporary staging)

### Step 3: Access the Cluster

```bash
ssh hutchnetid@rhino
```

For GUI applications, use NoMachine or `ssh -Y`.

### Step 4: Learn grabnode

```bash
grabnode
# Prompts: CPUs (1-36), Memory (default 20GB), Duration (1-7 days), GPU (yes/no)
```

### Step 5: Learn Basic Job Submission

```bash
sbatch myscript.sh
squeue -u $USER        # check your jobs
scancel <jobid>        # cancel a job
```

### Step 6: Understand Partitions

| Partition | Use Case | Max Time |
|-----------|----------|----------|
| campus-new | General purpose (default) | 30 days |
| short | Many brief jobs | 12 hours |
| interactive | grabnode sessions | 7 days |
| restart | Fault-tolerant, preemptable | 30 days |
| chorus | GPU workloads | 7 days |

### Step 7: Set Up Software Environment

```bash
# Search available modules
module spider python

# Load specific version (always specify version!)
ml Python/3.10.8-GCCcore-12.2.0

# Save a collection for reproducibility
module save myenv
ml restore myenv
```

Do NOT load modules in ~/.bashrc.

### Step 8: Use Local Scratch for I/O

In batch jobs, use `$TMPDIR` (not `/tmp`) for fast local SSD storage. It is automatically cleaned up.

### Step 9: AWS and Cloud Access

Request AWS credentials for S3 storage and cloud computing. Configure with `aws sso login`.

### Support Resources

- **SciComp Office Hours**: Weekly Teams meeting
- **Effective Computing Drop-In**: Biweekly Teams meeting
- **Data House Calls**: Schedule personalized sessions with the Data Science team
- **SciWiki**: https://sciwiki.fredhutch.org (community-maintained documentation)
- **Training**: "Intro to Fred Hutch Cluster Computing" course

### Login Node Policies (Arbiter)

Rhino nodes enforce resource limits via Arbiter:
- Normal: 16 cores, 86GB memory
- Exceeding limits for 5+ minutes triggers throttling (not killing)
- Email notifications sent on penalty activation

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki Onboarding: https://sciwiki.fredhutch.org/compdemos/onboard/
- SciComp Wiki Rhino: https://sciwiki.fredhutch.org/compdemos/howtoRhino/
- SciComp Wiki Grabnode: https://sciwiki.fredhutch.org/compdemos/grabnode/
- SciComp Wiki Partitions: https://sciwiki.fredhutch.org/compdemos/gizmo_partition_index/
