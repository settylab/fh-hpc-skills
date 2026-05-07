---
description: "R and RStudio on Fred Hutch HPC: modules, packages, Bioconductor, Jupyter R kernel"
---

# R and RStudio on Fred Hutch HPC

TRIGGER when: user asks about R on Gizmo/Rhino, loading R modules, installing R packages on the cluster, using RStudio Server, Bioconductor, or running R in Jupyter at Fred Hutch.

## Context

Fred Hutch provides R through Lmod environment modules on Rhino/Gizmo. RStudio Server is available via Open OnDemand (recommended) or through EasyBuild modules and Apptainer containers. R packages come from three sources: CRAN, Bioconductor, and GitHub.

## Instructions

### Loading R on the Cluster

```bash
# Find available R versions
module spider R
module avail fhR

# Load the default Fred Hutch R (R 4.4.1 with 200+ extensions including Bioconductor)
ml fhR

# Load a specific version
ml fhR/4.4.1-foss-2023b
R
```

Available fhR versions: 4.0.2 through 4.4.1 (default). The `fhR` modules bundle a large set of Bioconductor and CRAN extensions (MAST, DiffBind, ArchR, tidymodels, paws, etc.).

Always use `ml R` rather than calling a bare `R` on Rhino. This ensures reproducibility and proper library paths.

### Using RStudio Server

**Recommended:** Open OnDemand provides a web-based RStudio interface with no SSH setup needed.

**Alternative launch options:**
- Fred Hutch RStudio Server via EasyBuild modules
- RStudio Server/Apptainer (containerized, access to newer versions)

**Graphics fix for low resolution:**
Tools -> Global Options -> General -> Graphics tab -> set Backend to AGG.

**RMarkdown plotting enhancement:**
```r
knitr::opts_chunk$set(dev="CairoPNG")
```

### Installing R Packages

**From CRAN:**
```r
install.packages("package_name")
```

**From Bioconductor** (curated bioinformatics packages):
```r
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("package_name")
```

**From GitHub** (experimental, not peer-reviewed):
```r
devtools::install_github("user/repo")
```

### Running R in JupyterLab

**Install IRkernel:**
```r
install.packages("IRkernel", repos="https://cran.r-project.org")
IRkernel::installspec()
```

**Configure .Rprofile for Jupyter graphics:**
```r
if (!is.na(Sys.getenv("JPY_PARENT_PID", unset = NA))) {
    options(bitmapType = 'cairo')
}
```

**Launch JupyterLab:**
```bash
jupyter lab --ip=$(hostname) --port=$(fhfreeport) --no-browser
```

### Project-Level Dependency Management with renv

For reproducible R projects, use **renv** to create project-local library snapshots. renv installs from CRAN and Bioconductor and does not depend on conda channels.

```r
# Initialize renv in your project (creates renv.lock + project library)
renv::init()

# Install packages as usual
install.packages("tidyverse")
BiocManager::install("DESeq2")

# Snapshot current state (records exact versions in renv.lock)
renv::snapshot()

# On another machine or after a fresh clone, restore the exact environment
renv::restore()
```

Commit `renv.lock` to version control. This ensures anyone can recreate your exact package versions. For parallel-safe RNG (`L'Ecuyer-CMRG`), Bioconductor pinning, and the broader reproducibility checklist (modules, containers, agent-code risks), see `fh.reproducibility`.

**When to use renv vs Lmod fhR:**
- **fhR modules**: Quick interactive work, teaching, when the bundled 200+ packages are sufficient
- **renv**: Research projects destined for publication, shared codebases, anything requiring exact version reproducibility

### Key Libraries

- **Tidyverse**: Coordinated set of packages for data manipulation (dplyr, ggplot2, tidyr, etc.)
- **Shiny**: Build interactive web applications, deployable via Shinyapps.io
- **RMarkdown/Quarto**: Reproducible documents combining code and narrative

### Requesting New Modules

Email scicomp@fredhutch.org to request additional R modules or package installations.

## Principles

- Use renv for project-level R dependency management and reproducibility
- Use versioned module loads (e.g., `ml R/4.3.1-gfbf-2022b`) for reproducibility
- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies

## References

- renv: https://rstudio.github.io/renv/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_R/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_running/
- Bioconductor: https://bioconductor.org/
