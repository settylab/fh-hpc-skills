# Apptainer Containers on Fred Hutch HPC

Source: https://sciwiki.fredhutch.org/compdemos/Apptainer/

## Overview

Apptainer (formerly Singularity) is a container platform enabling non-root users to run containers on shared HPC environments, unlike Docker which requires admin privileges. Available on rhino and gizmo nodes.

## Loading and Basic Usage

```bash
ml Apptainer

# Pull a Docker image and convert to SIF
apptainer pull docker://ghcr.io/apptainer/lolcow

# Run the container
apptainer run lolcow_latest.sif
```

## Remote Builder (Sylabs Cloud)

```bash
apptainer remote add --no-login SylabsCloud cloud.sylabs.io
apptainer remote use SylabsCloud
apptainer pull --arch amd64 library://sakriwedg/default/lolcow:latest
```

Note: Sylabs remote builder requires account setup and key regeneration every 30 days.

## R Container Example

```bash
ml Apptainer
apptainer build r-base-latest.sif docker://r-base
apptainer exec r-base-latest.sif R
apptainer exec r-base-latest.sif Rscript script.R
```

## Definition Files (Custom Containers)

Create `my.r.apptainer.build.def`:
```
BootStrap: docker
From: r-base

%post
R --no-echo -e 'install.packages("devtools", repos="https://cloud.r-project.org/")'
mkdir -p /mnt/data
```

Build:
```bash
apptainer build --remote my_r_container.sif my.r.apptainer.build.def
```

## Bind Mounts (Storage Access)

Command-line binding:
```bash
apptainer exec --bind /shared/biodata:/mnt/data my_r_container.sif R
```

Environment variable binding:
```bash
export APPTAINER_BIND=/shared/biodata:/mnt/data
apptainer exec my_r_container.sif R
```

Default mounts include current working directory and home directory.

## Cache and Temp Directory Configuration

```bash
# Set cache directory
export APPTAINER_CACHEDIR=${HOME}/.my_cachedir

# Set temp build directory (command-line, highest priority)
apptainer build --tmpdir=${HOME}/tmp my.r.apptainer.build.def

# Or via environment variables
export APPTAINER_TMPDIR=/path/to/tmp
export TMPDIR=/path/to/tmp
```

## Important Notes

- Build on gizmo compute nodes, not rhino (resource-intensive)
- Containers can run interactively (grabnode) or in batch (sbatch)
- Avoid scratch filesystem for temp build dirs (permission issues with hard links)
- HutchNet ID must have appropriate storage permissions for bound paths
