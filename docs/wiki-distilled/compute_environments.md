# Computing Environments (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_environments/

## Key Facts

### Environment Modules (Lmod)

Fred Hutch uses Lmod for modular software access. Over 1,000 pre-compiled packages are available, optimized for reproducibility and performance.

**Essential Commands:**

| Command | Purpose |
|---------|---------|
| `module avail` | List all available modules |
| `module avail <pattern>` | Filter modules by name (e.g., `module avail SAMtools`) |
| `module load <pkg>/<version>` | Load specific version |
| `module load <pkg>` | Load default version |
| `module list` | Show loaded modules |
| `module unload <pkg>` | Remove a module |
| `module purge` | Unload all modules |
| `ml` | Shorthand for `module` |

### Scripting Best Practices

Initialize the module system in bash scripts:
```bash
#!/bin/bash
source /app/lmod/lmod/init/profile
```

Always specify versions in scripts for reproducibility:
```bash
module load Python/3.5.1-foss-2016b-fh1
```

Never use generic `module load Python` in scripts because the default version changes over time.

### Docker & Containers

- Docker requires root access and cannot run on shared environments (Rhino/Gizmo).
- Use **Apptainer** (formerly Singularity) to run Docker containers on the cluster without admin privileges.
- Container sources: WILDS Docker Library (GitHub/DockerHub), Fred Hutch DockerHub, Docker Hub, Quay, BioContainers.

### Custom Software Installation

Python packages after loading module:
```bash
pip install --user <package>
```

R packages:
```r
install.packages("<pkgname>")
```

Load a toolchain module before building standalone software:
```bash
module load foss/2019b
```

### Workflow Management

Fred Hutch supports Nextflow and WDL workflows with integrated environment management through Docker/modules.
Resources: WILDS WDL Library, Fred Hutch Nextflow Catalog.

## Common Pitfalls

- Not initializing module system in scripts (missing `source /app/lmod/lmod/init/profile`).
- Using generic module references in scripts instead of pinned versions.
- Attempting to run Docker directly on the cluster (use Apptainer instead).
- Not running `module purge` before loading modules for chorus partition jobs.

## Cross-references

- /scicomputing/compute_scientificSoftware/ (available modules)
- /scicomputing/compute_platforms/ (node specifications)
