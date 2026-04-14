# Fred Hutch HPC Live Environment Reference

Probed from the live Gizmo cluster on 2026-04-13.

## Cluster Name and Architecture

The Fred Hutch HPC cluster is called **Gizmo**. It runs Slurm as its workload manager on Ubuntu 18.04 LTS (kernel 4.15.0-213-generic). The cluster name appears in node hostnames: `gizmoj*` (J-class), `gizmok*` (K-class), plus dedicated `harmony*` and `canto*` nodes.

## Partitions

| Partition | Default Time | Max Time | Nodes | CPUs/node | Memory/node | GPU | Preemption | Notes |
|---|---|---|---|---|---|---|---|---|
| **campus-new** (default) | 3 days | 30 days | 198 (37 J + 161 K) | 24 (J) / 36 (K) | 350 GB (J) / 700 GB (K) | 1x GTX 1080 Ti (J) / 1x RTX 2080 Ti (K) | No | General-purpose; MaxCPUsPerNode=36, MaxMemPerNode~774 GB |
| **short** | 1 hour | 12 hours | 198 | same as campus-new | same | same | No | Fast turnaround; 2-min overtime grace |
| **restart-new** | 3 days | 30 days | 198 | same | same | same | Yes (REQUEUE) | Preemptible/scavenger; lowest priority (tier 1) |
| **interactive** | 1 day | 7 days | 198 | same | same | same | No | Highest priority (tier 30000); accessed via `grabnode` |
| **chorus** | 4 hours | 7 days | 8 (harmony01-08) | 32 | ~1.5 TB | 4x NVIDIA L40S | No | GPU-heavy workloads |
| **canto** | 4 hours | 7 days | 3 (canto1-3) | 36 | ~1.5 TB | 1x RTX 2080 Ti | No | High-memory nodes |

Total cluster TRES for campus-new: 6,684 CPUs, ~126 TB RAM, 198 GPUs, 198 nodes.

### Node Classes

**J-class (gizmoj1-gizmoj40, ~37 nodes):** 24 cores, 350 GB RAM, 1x NVIDIA GTX 1080 Ti.

**K-class (gizmok1-gizmok169, ~161 nodes):** 36 cores, 700 GB RAM, 1x NVIDIA RTX 2080 Ti.

**Harmony (harmony01-08, 8 nodes):** 32 cores, ~1.5 TB RAM, 4x NVIDIA L40S per node (32 L40S GPUs total). Chorus partition only.

**Canto (canto1-3, 3 nodes):** 36 cores, ~1.5 TB RAM, 1x RTX 2080 Ti. High-memory partition.

## Available Software Modules

Modules are served from `/app/modules/all` via Lmod.

### Python
Versions: 2.7.16, 2.7.18, 3.7.4, 3.8.2, 3.8.6, 3.9.5, 3.9.6, 3.10.4, 3.10.8, 3.11.3, 3.11.5, 3.12.3.
Fred Hutch curated bundles: `fhPython/3.8.2`, `fhPython/3.8.6`, `fhPython/3.9.6`, `fhPython/3.11.3` (default).

### R
Versions: 3.6.2 through 4.4.2 (default: 4.4.2-gfbf-2024a).
Fred Hutch curated bundles: `fhR/4.0.2` through `fhR/4.4.1` (default: 4.4.1-foss-2023b).

### CUDA
Versions: 9.2.88, 10.1.243, 10.2.89, 11.1.1, 11.3.1, 11.4.1, 11.7.0, 12.0.0, 12.1.1, 12.4.0, 12.6.0 (default).
cuDNN: 8.0.x through 9.5.x, matching CUDA versions.

### Compilers (GCC)
Versions: 7.3.0, 8.3.0, 9.3.0, 10.2.0, 10.3.0, 11.2.0, 11.3.0, 12.2.0, 12.3.0, 13.2.0, 13.3.0 (default).

### Containers
Apptainer: 1.0.1, 1.1.4, 1.1.6 (default). Singularity: 3.5.3 (legacy).

### Workflow Engines
Nextflow: 21.03.0 through 25.10.2 (default). Also available as user install at `~/.local/bin/nextflow`.

### Key Scientific Software
AlphaFold, PyTorch (up to 2.1.2 with CUDA 12.1.1), TensorFlow (up to 2.15.1 with CUDA 12.1.1), JAX, CellRanger (up to 10.0.0), scanpy, scvi-tools, flash-attention, dorado, BEAST/BEAST2, and many bioinformatics tools (SAMtools, BCFtools, BEDTools, STAR, etc.).

## File System Layout

| Path | Purpose | Notes |
|---|---|---|
| `/home/$USER/` | Home directory | Small quota, config files only |
| `/fh/fast/<pi_name>/` | Fast storage | Lab-level persistent storage, organized by PI last name |
| `/fh/fast/<pi>/user/<username>/` | Per-user fast storage | Main working directory |
| `/fh/scratch/delete10/` | Scratch (10-day) | Auto-deleted after 10 days |
| `/fh/scratch/delete30/` | Scratch (30-day) | Auto-deleted after 30 days |
| `/fh/scratch/delete90/` | Scratch (90-day) | Auto-deleted after 90 days |
| `/app/` | Applications | Modules, software, EasyBuild recipes |
| `/app/modules/all/` | Module files | All Lmod module definitions |

Environment variables for scratch: `$DELETE10`, `$DELETE30`, `$DELETE90` point to `/fh/scratch/delete{10,30,90}`. The general scratch variable `$SCRATCH` points to `/fh/scratch/gizmo`.

## Available Tools

| Tool | Path | Notes |
|---|---|---|
| `sbatch`, `srun`, `scancel`, `squeue`, `sacct`, `sinfo` | Slurm (in PATH) | Standard job scheduler commands |
| `grabnode` | `/app/bin/grabnode` | Interactive node allocation (prompts for cores, memory, days, GPU) |
| `ml`, `module` | Shell functions (Lmod) | Module loading system |
| `singularity` | `/app/bin/singularity` | Container runtime (legacy) |
| `apptainer` | Via `module load Apptainer` | Container runtime (current) |
| `nextflow` | `~/.local/bin/nextflow` or via module | Workflow engine |

## Key Environment Variables

| Variable | Value / Purpose |
|---|---|
| `SLURM_SCOPE` | `project` (sandbox-enforced) |
| `SCRATCH` | `/fh/scratch/gizmo` |
| `DELETE10` | `/fh/scratch/delete10` |
| `DELETE30` | `/fh/scratch/delete30` |
| `DELETE90` | `/fh/scratch/delete90` |
| `MAMBA_ROOT_PREFIX` | User's mamba/conda root |

## Interactive Access

`grabnode` is the standard way to get an interactive session. It prompts for number of cores (1-36), memory, duration, and whether you need a GPU. Maximum per user: 3 jobs, 36 cores, 1 GPU concurrently on interactive nodes.
