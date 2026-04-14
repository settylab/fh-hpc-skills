# Docker and Containers at Fred Hutch

Source: https://sciwiki.fredhutch.org/compdemos/Docker/

## Overview

Docker creates isolated, self-contained environments with their own file systems, software, and settings. On the Fred Hutch HPC cluster, containers are run via Apptainer (not Docker directly) since Docker requires admin privileges.

## Docker vs Apptainer

- **Docker**: Requires administrator privileges. Use on personal laptops for development.
- **Apptainer** (formerly Singularity): Runs without admin on shared HPC systems. Use on rhino/gizmo.
- Typical workflow: build with Docker locally, run with Apptainer on cluster.

## Docker Commands (Local Development)

```bash
# List local images
docker images

# Pull image
docker pull getwilds/samtools:1.19

# Run command in container (auto-remove on exit)
docker run --rm getwilds/samtools:1.19 samtools --version

# Interactive session
docker run -it getwilds/samtools:1.19

# Mount local folder
docker run -v /Users/yourname/data:/data getwilds/star:2.7.6a \
  STAR --runMode genomeGenerate \
       --genomeDir /data/genome_index \
       --genomeFastaFiles /data/genome.fa

# List containers
docker ps       # active only
docker ps -a    # all including stopped
```

## Apptainer on Cluster

```bash
ml Apptainer

# Execute Docker image directly
apptainer exec docker://getwilds/samtools:1.19 samtools --version

# Pull and convert to SIF
apptainer pull docker://getwilds/samtools:1.19

# Run SIF file
apptainer exec samtools_1.19.sif samtools --version

# Interactive shell
apptainer shell samtools_1.19.sif

# Mount folder
apptainer exec --bind /fh/fast/mylab/data:/data \
  docker://getwilds/samtools:1.19 samtools --version
```

Build containers on gizmo compute nodes, not rhino.

## Cache Management

```bash
du -sh ~/.apptainer/cache
ml Apptainer
apptainer cache clean           # clear all
apptainer cache clean --days 30 # older than 30 days
```

## Creating Custom Images (Dockerfile)

```dockerfile
FROM ubuntu:22.04
LABEL maintainer="your.email@fredhutch.org"
LABEL description="Custom analysis environment"
LABEL version="1.0"

RUN apt-get update && apt-get install -y \
    python3 python3-pip wget \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install numpy pandas scipy

COPY analysis_pipeline.py /usr/local/bin/
WORKDIR /data
```

```bash
docker build -f Dockerfile_latest -t myanalysis:2.0 .
```

## Sharing Images (Docker Hub)

```bash
docker tag myanalysis:1.0 yourusername/myanalysis:1.0
docker login
docker push yourusername/myanalysis:1.0
```

## WDL Integration

```wdl
task runSTAR {
  runtime {
    docker: "getwilds/star:2.7.6a"
  }
}
```

Image format: `registry/namespace/repository:tag`

## Best Practices

- Use specific version tags (not `latest`) for reproducibility
- Keep images minimal with only necessary dependencies
- Mount large datasets rather than baking them into images
- Document with README and LABEL metadata
