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

Build containers from **definition files** (Dockerfile or Apptainer `.def`), never from interactive sandbox modifications. This ensures builds are reproducible and auditable. Store definition files alongside workflow code in version control.

**Build on compute nodes, not login nodes.** Container builds are resource-intensive and will be killed or cause problems on rhino login nodes. Use `grabnode` or submit a Slurm job:

```bash
grabnode  # request a compute node first

# Build Apptainer image from definition file
apptainer build my_image.sif my_image.def

# Or pull from a registry
apptainer pull docker://myuser/myimage:v1
```

To use a registry-based workflow, build and push from a machine with Docker access (local workstation or CI), then pull on the cluster:

```bash
# On your local machine or CI:
docker build -t myuser/myimage:v1 .
docker push myuser/myimage:v1

# On the cluster (from a compute node):
apptainer pull docker://myuser/myimage:v1
```

### SHA256 Digest Pinning

Tags are mutable — `v1.0` today may point to different bytes tomorrow. Pin base images and dependencies by SHA256 digest for reproducibility:

```dockerfile
# Bad: mutable tag
FROM ubuntu:22.04

# Good: digest-pinned
FROM ubuntu@sha256:2b7412e6465c3c7fc5bb21d3e6f1917c167358449fecac8176c6e496e5c1f05f
```

In Apptainer definition files:
```
Bootstrap: docker
From: ubuntu@sha256:2b7412e6465c3c7fc5bb21d3e6f1917c167358449fecac8176c6e496e5c1f05f
```

Find digests with:
```bash
docker inspect --format='{{index .RepoDigests 0}}' ubuntu:22.04
# Or from a registry:
skopeo inspect docker://ubuntu:22.04 | jq '.Digest'
```

Pin every stage in multi-stage builds. Record the digest in your version control so the build is fully traceable.

### Multi-Stage Builds

Use multi-stage builds to separate build-time dependencies from the runtime image. This reduces image size and attack surface:

```dockerfile
# Stage 1: Build
FROM ubuntu@sha256:abc123... AS builder
RUN apt-get update && apt-get install -y build-essential cmake
COPY . /src
RUN cd /src && cmake . && make

# Stage 2: Runtime (minimal)
FROM ubuntu@sha256:abc123...
COPY --from=builder /src/my_tool /usr/local/bin/
ENTRYPOINT ["my_tool"]
```

This pattern is valuable for tools that need compilers or large build chains at build time but only a small binary at runtime.

### BioContainers

Over 9,000 bioinformatics tools are available as pre-built containers through BioContainers, generated from Bioconda recipes.

**Important: The AWS ECR Public Gallery mirror for BioContainers was deprecated in August 2025.** If you have old scripts or configs pulling from `public.ecr.aws/biocontainers/`, update them. The recommended alternatives are:

- **Seqera Containers** (https://seqera.io/containers/) — the current recommended registry for BioContainers images
- **Quay.io** — `quay.io/biocontainers/<tool>:<version>`
- **Build locally** from Bioconda recipes if registry access is unreliable

### Conda/Mamba Inside Container Builds

If your Dockerfile or `.def` file installs packages via conda or mamba, use only conda-forge and bioconda channels. Anaconda.org is blocked on Gizmo, and container builds that depend on the `defaults` channel will fail or produce non-redistributable images.

```dockerfile
# Install micromamba and use only open channels
RUN micromamba install -y -n base -c conda-forge -c bioconda \
    samtools=1.19 bcftools=1.19 && \
    micromamba clean --all --yes
```

Alternatively, use pre-built BioContainers (which are built from Bioconda recipes with open channels) rather than rebuilding from scratch.

### Containers for Complex Software Stacks

For projects with complex, interdependent dependencies (e.g., GPU libraries + bioinformatics tools + custom compiled code), containers are strongly preferred over environment modules or conda alone. NERSC and other national computing centers have found that containers provide the most reliable path to reproducibility when the software stack has deep dependency trees or requires specific system library versions.

Use containers when:
- The software requires a specific OS or system library version
- Multiple tools with conflicting dependencies must coexist
- The environment must be identical across local, cluster, and cloud
- You need to archive the exact computational environment for publication

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
