---
description: "AWS cloud computing at Fred Hutch (AWS Batch, WDL/PROOF, Nextflow, CloudShell)"
---

# Fred Hutch Cloud Computing (AWS)

TRIGGER when: user asks about cloud computing, AWS Batch, running workflows on AWS, PROOF/Cromwell, or needs to scale beyond the on-premise Gizmo cluster.

## Context

Fred Hutch provides multiple methods for leveraging AWS cloud computing, from beginner-friendly (PROOF) to advanced (direct AWS Batch). Cloud computing complements the on-premise Gizmo cluster for workloads that benefit from elastic scaling or specific cloud services.

## Instructions

### Options Overview

| Method | Complexity | Best For |
|--------|-----------|----------|
| **PROOF (WDL)** | Low | Researchers wanting cloud execution without AWS expertise |
| **Nextflow on AWS** | Medium | Pipeline developers already using Nextflow |
| **AWS Batch** | High | Advanced users needing direct cloud control |
| **CloudShell** | Low | Quick AWS CLI tasks |

### WDL with PROOF

WDL (Workflow Description Language) is an open-source workflow language that works across compute infrastructures. Fred Hutch offers PROOF as a user-friendly interface:

- PROOF handles Cromwell server configuration automatically.
- Submit WDL workflows without managing cloud infrastructure.
- Ideal entry point for cloud computing at Fred Hutch.
- See the WILDS WDL Library for vetted workflow templates.

### Nextflow on AWS

Nextflow can use AWS as a backend execution resource:

- Configure Nextflow to submit jobs to AWS Batch.
- This is an **emerging service, not currently fully supported** at Fred Hutch.
- Consult SciComp before relying on this for production workloads.

### AWS Batch

Direct access to AWS EC2 resources for batch computing:

- Uses Docker containers (required, not optional).
- Dynamic resource provisioning based on workload.
- Built-in queueing system for job management.
- **No traditional file systems**: no home directories, no /fh/fast, no /tmp. Use S3 for data storage.
- Ideal for standardized, repeatable processing pipelines.

### CloudShell

Browser-based AWS shell accessible from the AWS Management Console:

- AWS CLI pre-installed and authenticated.
- 1 GB persistent storage in home directory.
- No charges for CloudShell itself (services you enable may incur costs).
- Good for quick AWS administration tasks.

### Key Differences from On-Premise

| Aspect | Gizmo (On-Premise) | AWS Cloud |
|--------|-------------------|-----------|
| File systems | /home, /fh/fast, /hpc/temp | S3, EBS |
| Job manager | Slurm | AWS Batch / PROOF |
| Containers | Optional (Apptainer) | Required (Docker) |
| Scaling | Fixed nodes | Elastic |
| Cost | Included in overhead | Pay per use |
| Data locality | Fast network access | Data transfer costs |

## Principles

- Start with PROOF/WDL if you are new to cloud computing.
- Account for data transfer costs when moving data between on-premise and cloud.
- Use S3 for cloud data storage, not EBS volumes.
- Prefer on-premise Gizmo when data is already on-site and cloud elasticity is not needed.
- Follow Fred Hutch data security policies (especially for PHI/PII).
- Consult SciComp for guidance on cloud architecture.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_cloud/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/access_aws/
