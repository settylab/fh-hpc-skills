---
description: "Running Apptainer/Docker containers on the Fred Hutch Gizmo cluster"
---

# Fred Hutch Containers (Apptainer)

TRIGGER when: user wants to run Docker containers on the cluster, asks about Apptainer/Singularity, needs containerized software, or wants reproducible environments on Gizmo.

## Context

Docker requires root access and cannot run directly on the shared Fred Hutch cluster (rhino/gizmo). Apptainer (formerly Singularity) is the supported container runtime, allowing users to run Docker images on the cluster without administrator privileges.

## Instructions

### Why Containers on HPC

- Reproducible environments independent of cluster module versions
- Access to software not available as Lmod modules
- Portability across systems (local, cloud, cluster)
- Consistent environments for publications and collaborations

### Running Docker Images with Apptainer

Apptainer can pull and run Docker images directly:

```bash
# Pull a Docker image and convert to SIF (Apptainer format)
apptainer pull docker://biocontainers/samtools:v1.9-4-deb_cv1

# Run a command inside the container
apptainer exec samtools_v1.9-4-deb_cv1.sif samtools --version

# Interactive shell inside the container
apptainer shell samtools_v1.9-4-deb_cv1.sif

# Run the container's default entrypoint
apptainer run samtools_v1.9-4-deb_cv1.sif
```

### Using Containers in Slurm Jobs

```bash
#!/bin/bash
#SBATCH --job-name=container-job
#SBATCH --cpus-per-task=4
#SBATCH --time=4:00:00

apptainer exec my_container.sif my_analysis_command --threads $SLURM_JOB_CPUS_PER_NODE
```

### Bind Mounts

Apptainer automatically mounts your home directory. For other paths (e.g., `/fh/fast/`), use bind mounts:

```bash
apptainer exec --bind /fh/fast/:/fh/fast/ my_container.sif my_command
```

### Container Sources

- **WILDS Docker Library** (GitHub/DockerHub): Tested bioinformatics containers maintained by Fred Hutch
- **Fred Hutch DockerHub**: Institutional containers
- **Docker Hub**: General-purpose containers
- **Quay.io**: Red Hat container registry
- **BioContainers**: Community bioinformatics containers

### GPU Containers

For GPU workloads, use the `--nv` flag to expose NVIDIA GPUs inside the container:

```bash
apptainer exec --nv my_gpu_container.sif python train.py
```

### Building Custom Containers

Build containers on your local machine (where you have root/Docker access), push to a registry, then pull on the cluster:

```bash
# On your local machine:
docker build -t myuser/myimage:v1 .
docker push myuser/myimage:v1

# On the cluster:
apptainer pull docker://myuser/myimage:v1
```

## Principles

- Prefer Lmod modules when available (lower overhead than containers)
- Use containers for software not available as modules or when exact reproducibility is required
- Store SIF files in your lab's fast directory, not in your home directory (they can be large)
- Tag container images with versions for reproducibility (never use `:latest` in production scripts)
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies
- Verify bind mounts and paths before batch submission. A missing `--bind` causes silent failures where the container runs but cannot see input data, producing empty or misleading outputs.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_environments/
- Apptainer docs: https://apptainer.org/docs/user/latest/
- WILDS Docker Library: https://github.com/FredHutch/docker-images
