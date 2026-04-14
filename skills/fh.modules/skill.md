---
description: "Lmod environment modules on Gizmo: loading, searching, and managing software"
---

# Using Lmod Environment Modules on Gizmo

TRIGGER when: user asks about loading software on Rhino/Gizmo, using `module` or `ml` commands, finding available software versions, or understanding environment modules at Fred Hutch.

## Context

Fred Hutch uses the Lmod environment module system to manage software on the Rhino login nodes and Gizmo compute cluster. Modules configure your shell environment (PATH, library paths, etc.) so you can access specific software versions without conflicts. Always load software through modules rather than calling binaries directly to ensure reproducibility.

## Instructions

### Essential Module Commands

```bash
# List currently loaded modules
ml

# Load a module (short form)
ml R/4.3.1-gfbf-2022b

# Load a module (long form)
module load R/4.3.1-gfbf-2022b

# Unload a module
ml -R
module unload R

# Purge all loaded modules
ml purge

# Search for available modules by name
module spider R
module avail Python/3
module avail fhPython

# Get detailed info about a specific module
module spider R/4.3.1-gfbf-2022b
```

### Why Use Modules

Loading software via `ml` rather than calling bare commands (e.g., `ml R` instead of just `R`) ensures:
- **Reproducibility**: You get a specific, documented version
- **Correct dependencies**: Required libraries are loaded automatically
- **Latest software**: Access to the most recent versions maintained by SciComp

### Common Module Patterns

```bash
# Load the Fred Hutch curated Python (1,000+ scientific packages)
ml fhPython/3.8.6-foss-2020b-Python-3.8.6

# Load JupyterLab with scientific packages
ml purge
ml JupyterLab/4.0.3-GCCcore-12.2.0 Seaborn/0.12.2-foss-2022b

# Load R
ml R/4.3.1-gfbf-2022b
```

### Choosing Between Rhino and Gizmo

| Environment | Use Case | Key Trait |
|------------|----------|-----------|
| **Local** | Small tasks, development | Immediate access, limited resources |
| **Rhino** (shared login nodes) | Moderate work, testing | Shared with other users, no job scheduler |
| **Gizmo** (compute cluster) | Production runs, large jobs | Exclusive node access via Slurm, may queue |

On both Rhino and Gizmo, load software through modules.

### Requesting New Software

If the module you need is not available:
- Email scicomp@fredhutch.org
- File an issue on the `easybuild-life-sciences` GitHub repository

SciComp builds and maintains modules using the EasyBuild framework.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use explicit version numbers in module loads for reproducible analyses
- Use `ml purge` before loading a new set of modules to avoid conflicts
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_overview/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_running/
- EasyBuild inventory: https://fredhutch.github.io/easybuild-life-sciences/
