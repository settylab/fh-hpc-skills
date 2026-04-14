# HPC Exploration Agent Report

Probed: 2026-04-13
Cluster: Gizmo (Fred Hutchinson Cancer Center)
OS: Ubuntu 18.04 LTS, kernel 4.15.0-213-generic

## Summary

The Gizmo cluster has 209 compute nodes across 6 Slurm partitions, with a total of ~6,684 CPUs and 233 GPUs. The cluster uses Lmod for environment modules, served from `/app/modules/all/`.

## Partition Inventory

198 general nodes (37 J-class with 24 cores/350 GB/GTX 1080 Ti, 161 K-class with 36 cores/700 GB/RTX 2080 Ti) are shared across 4 partitions: campus-new (default, 30d), short (12h), interactive (7d, via grabnode), and restart-new (30d, preemptible).

8 Harmony nodes (32 cores, 1.5 TB, 4x L40S each) form the chorus partition for GPU-heavy work. 3 Canto nodes (36 cores, 1.5 TB, 1x RTX 2080 Ti) provide high-memory capacity.

## Software Ecosystem Highlights

Python: 2.7.16 through 3.12.3, plus Fred Hutch curated `fhPython` bundles.
R: 3.6.2 through 4.4.2, plus `fhR` bundles up to 4.4.1.
CUDA: 9.2 through 12.6.0 with matching cuDNN.
GCC: 7.3.0 through 13.3.0.
Containers: Apptainer 1.1.6 (default), Singularity 3.5.3 (legacy).
ML frameworks: PyTorch up to 2.1.2, TensorFlow up to 2.15.1, JAX up to 0.4.25, all with CUDA support.
Workflow: Nextflow up to 25.10.2.
Bio: CellRanger 10.0.0, AlphaFold, scanpy, scvi-tools, STAR, BCFtools, and hundreds more.

## File Systems

Fast storage at `/fh/fast/<pi>/user/<username>/` is the primary working directory. Scratch is auto-purged on 10/30/90-day schedules at `/fh/scratch/delete{10,30,90}/`. Home directories are small and quota-limited. Modules and software live under `/app/`.

## Observations

1. The L40S GPUs on Harmony nodes (chorus partition) are the most capable GPUs on the cluster at 48 GB VRAM each, with 4 per node. This is the go-to for multi-GPU training or large models.
2. Every general node has a GPU (1080 Ti or 2080 Ti), so GPU access is broadly available even on campus-new without special requests.
3. The `grabnode` tool provides a guided interactive allocation experience, with per-user limits of 36 cores and 1 GPU across up to 3 concurrent interactive sessions.
4. The restart-new partition allows long-running preemptible jobs at the lowest priority, suitable for checkpointable workloads that can tolerate requeue.

## Files Created

- `docs/wiki-distilled/hpc-live-environment.md` -- Full reference document with tables covering partitions, modules, file systems, tools, and environment variables.
- `skills/fh.cluster-overview/skill.md` -- Concise skill document for quick cluster specs and partition selection guidance.
- `shared/reports/hpc-explore-agent.md` -- This report.
