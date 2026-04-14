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

# Search for all versions of a module (preferred)
module spider R

# Get detailed info and loading instructions for a specific version
module spider R/4.3.1-gfbf-2022b

# List modules currently visible (may be incomplete — see below)
module avail Python/3
module avail fhPython
```

### module spider vs. module avail

**Use `module spider` for discovery, not `module avail`.** Fred Hutch uses Lmod's hierarchical module system, where software compiled against a specific toolchain (compiler + MPI library) is only visible after that toolchain is loaded. `module avail` shows only what is currently visible given your loaded modules; `module spider` searches the entire module tree regardless of what is loaded.

```bash
# This may show nothing if the right toolchain is not loaded:
module avail SomePackage

# This always finds it if it is installed:
module spider SomePackage

# module spider also tells you what you need to load first:
module spider SomePackage/1.2.3
#   You will need to have the following modules loaded:
#     GCCcore/12.3.0
```

The pattern is: `module spider <name>` to find what exists, then `module spider <name/version>` to learn what prerequisites to load, then `module load` those prerequisites followed by your target module.

### Why Use Modules

Loading software via `ml` rather than calling bare commands (e.g., `ml R` instead of just `R`) ensures:
- **Reproducibility**: You get a specific, documented version
- **Correct dependencies**: Required libraries are loaded automatically
- **Latest software**: Access to the most recent versions maintained by SciComp

### Common Module Patterns

```bash
# Load the Fred Hutch curated Python (scientific packages via foss toolchain)
ml fhPython                            # default: fhPython/3.11.3-foss-2023a

# Load JupyterLab with scientific packages
ml purge
ml JupyterLab/4.0.3-GCCcore-12.2.0 Seaborn/0.12.2-foss-2022b

# Load the Fred Hutch curated R (200+ Bioconductor/CRAN extensions)
ml fhR                                 # default: fhR/4.4.1-foss-2023b
```

### Choosing Between Rhino and Gizmo

| Environment | Use Case | Key Trait |
|------------|----------|-----------|
| **Local** | Small tasks, development | Immediate access, limited resources |
| **Rhino** (shared login nodes) | Moderate work, testing | Shared with other users, no job scheduler |
| **Gizmo** (compute cluster) | Production runs, large jobs | Exclusive node access via Slurm, may queue |

On both Rhino and Gizmo, load software through modules.

### When Modules Are Enough vs When You Need More

**Modules are sufficient when:**
- The software you need is already available (`module spider <name>`)
- You are doing interactive exploration or quick analyses
- Your project uses only the packages bundled in fhPython or fhR
- You need tools built against specific compilers/MPI stacks (e.g., CUDA-linked libraries)

**Use uv (Python) or renv (R) when:**
- You need packages not available in modules
- Your project requires exact, lockfile-based reproducibility
- You are building a shared project that others must reproduce
- You are preparing an analysis for publication

**Use mamba (not conda — it is very slow) when:**
- Your project mixes Python + R + system-level C libraries in one environment
- You need bioconda tools not available via PyPI or Lmod
- Configure mamba with the Fred Hutch mirror via project-local `.condarc` (see `fh.python` skill); anaconda.org is blocked
- **PATH ordering matters:** if a mamba env is active when `module load` runs, the module takes precedence. Deactivate all envs, load modules, then `mamba activate` to give the env priority

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
