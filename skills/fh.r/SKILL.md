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

Commit `renv.lock` to version control. This ensures anyone can recreate your exact package versions.

**When to use renv vs Lmod fhR:**
- **fhR modules**: Quick interactive work, teaching, when the bundled 200+ packages are sufficient
- **renv**: Research projects destined for publication, shared codebases, anything requiring exact version reproducibility

### Key Libraries

- **Tidyverse**: Coordinated set of packages for data manipulation (dplyr, ggplot2, tidyr, etc.)
- **Shiny**: Build interactive web applications, deployable via Shinyapps.io
- **RMarkdown/Quarto**: Reproducible documents combining code and narrative

### Requesting New Modules

Email scicomp@fredhutch.org to request additional R modules or package installations.

### Single-cell R traps (Monocle 3, qs, anndataR)

Hard-won gotchas from running R single-cell tooling in Setty Lab conda/module envs:

- **Monocle 3 needs no install — it is an Lmod module** (`Monocle3/1.3.1-foss-2021b-R-4.2.2`; `library(monocle3)` works unmodified). Always `module avail <pkg>` before concluding a package is absent — testing `requireNamespace()` against the Bioconductor module and giving up is a common false negative.
- **`ml`/`module` is a shell function — piping it silently discards the env-changing eval.** `ml Monocle3/... | tail` loads nothing and leaves `Rscript` not-found. Run `ml` unpiped, on its own line.
- **Monocle 3 is non-deterministic across processes even at fixed `set.seed()`** — the stochasticity is in `cluster_cells → learn_graph → order_cells`, not the RNG. Same-seed runs correlate ρ≈0.79–0.95. Pinning all BLAS threads (`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=FLEXIBLAS_NUM_THREADS=1`) tightens ρ to ~0.98 but a residual remains. Never report a Monocle 3 composite as a point estimate — run ≥10 draws (build PCA/UMAP once, repeat only the graph stage) and report median/IQR/min/max/n. `preprocess/reduce/cluster/learn_graph` are root-independent; only `order_cells` consumes the root, so build the principal graph once and order it N times. `learn_graph(use_partition=TRUE)` (the default) strands off-partition cells at `Inf` — check the partition count first.
- **Reading classic `.qs` (Seurat/SCE) on R 4.2.3** (e.g. a conda `da2`-style env): magic `0b 0e 0a 0c` is the classic `qs` format (not `qs2`). `qs` is archived on CRAN — `remotes::install_version("qs","0.27.3")`, but **pin `stringfish==0.16.0` FIRST** (stringfish 0.19.0 removed `check_if_native_is_ascii`, which qs 0.27.3 still calls → compile failure). qs/stringfish need C++17 but many conda `Makeconf` bake `-std=gnu++14`; force it via `R_MAKEVARS_USER` (`CXX/CXX11/CXX14/CXX17 = <conda>-c++ -std=gnu++17`), and prepend the conda `bin` to PATH or compiles die `Error 127` (compiler not found).
- **`scverse/anndataR` is unusable below R 4.5.0** (1.3.0 requires R ≥ 4.5). For lossless R→AnnData on older R, do a controlled manual export (MatrixMarket for matrices, CSV for tables, plus embeddings/graphs/coords and a JSON manifest via `Matrix`+`jsonlite`; assemble in Python) rather than reaching for anndataR.
- **`renv::init` strict isolation hides base Seurat/SingleCellExperiment.** To load a project-installed `qs` *alongside* a base library, stack `.libPaths(c(<project-lib>, <base-lib>))` instead of activating renv.

Sandbox-specific Python-stack traps (squidpy, Palantir, scIB) are in `settylab.sandbox-gotchas`.

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
