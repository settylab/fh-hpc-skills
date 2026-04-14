---
description: "Computational reproducibility for scientific work: environment pinning (uv, renv, Lmod, Homebrew), container digests, parallel RNG, agent-generated code risks, and the five pillars framework"
---

# Computational Reproducibility

TRIGGER when: user asks about reproducibility, environment pinning, lockfiles, container digests, random seeds in parallel jobs, agent-generated code reliability, or making scientific analyses reproducible on Gizmo.

## Context

Computational reproducibility means that a given analysis produces the same results when re-executed. This requires controlling five dimensions: code, environment, data, parameters, and execution. On shared HPC infrastructure like Fred Hutch's Gizmo cluster, reproducibility also means your work can survive module updates, node reassignments, and the passage of time.

AI coding agents (Claude Code, Cursor, Codex) accelerate development but introduce specific reproducibility risks: undeclared dependencies, non-deterministic code generation, and opaque provenance. Research shows only 68.3% of agent-generated projects execute without errors in clean environments, and runtime dependencies expand ~13.5x beyond what models declare (Vangala et al., 2026).

## Instructions

### The Five Pillars of Computational Reproducibility

The framework from Ziemann, Poulain, and Bora (Briefings in Bioinformatics, 2023) identifies five pillars:

1. **Literate programming** — Combine code, results, and narrative in a single document (Jupyter notebooks, R Markdown, Quarto). Re-execute regularly to prevent staleness.
2. **Code version control** — Git with meaningful commits. Tag releases that produce published results. Code alone is insufficient; data, parameters, and environments must be versioned together.
3. **Compute environment control** — Pin every dependency. Use containers or lockfiles to capture the full software stack.
4. **Persistent data sharing** — Deposit data in repositories with persistent identifiers (DOIs). Use domain repositories (GEO, SRA, PRIDE) or general repositories (Zenodo, Dryad).
5. **Documentation** — README with installation, execution, expected inputs/outputs. Parameter files in version control. Run logs capturing exact commands, versions, and resource usage.

### Environment Pinning

Loose specs are for development. Locked specs are for reproducibility.

**On Fred Hutch Gizmo, access to anaconda.org is blocked due to Anaconda licensing restrictions.** The preferred environment mechanisms are: **uv** (Python), **renv** (R), **Lmod modules** (cluster software), and **Homebrew/Linuxbrew** (user-managed CLI tools). If you need conda/mamba, configure a project-local `.condarc` with `channel_alias: https://conda-forge.fredhutch.org` and use only conda-forge and bioconda channels (see the Mamba section below or the `fh.python` skill for the full recipe).

#### Lmod Version Pinning on Gizmo (Preferred for Cluster Software)

Lmod modules are the primary way to access pre-built software on Gizmo. Always pin the full version including toolchain:

```bash
# BAD: relies on default version (changes without notice)
module load R

# GOOD: pin to exact version
module load R/4.4.1-foss-2023b

# List available versions
module spider R

# Record the full module tree for reproducibility
module list 2>&1 | tee modules_loaded.txt
```

Default module versions change when SciComp updates the cluster. Scripts that worked last month may silently use different software versions today unless pinned.

#### Python (uv — Recommended)

uv is a fast Python package manager that handles virtual environments, dependency resolution, and lockfiles in one tool. It works entirely from PyPI, requires no conda channels, and generates a `uv.lock` file with exact versions and hashes.

```bash
# Initialize a project (creates pyproject.toml + .python-version)
uv init myproject && cd myproject

# Add dependencies (updates pyproject.toml and uv.lock automatically)
uv add numpy scanpy

# Reproduce the exact environment from lockfile
uv sync

# Run a script in the project environment (no manual activation needed)
uv run python my_analysis.py

# Pin the Python version itself
uv python pin 3.11.9
```

For one-off scripts or exploratory work, uv can create ephemeral environments:

```bash
# Run a script with dependencies declared inline (PEP 723)
uv run --with numpy --with pandas my_script.py

# Or use uvx for CLI tools without polluting your project
uvx ruff check .
```

Commit both `pyproject.toml` and `uv.lock` to version control. The lockfile pins every transitive dependency with hashes, closing the dependency gap that plagues agent-generated code.

#### Python (pip-compile — Alternative)

If you cannot use uv (e.g., existing projects with requirements.txt workflows):

```bash
# Development: loose spec in requirements.in
# numpy>=1.24
# scanpy

# Lock with hashes
pip-compile --generate-hashes requirements.in -o requirements.txt

# Install locked
pip install -r requirements.txt
```

#### R (renv)

```r
# Initialize renv in your project
renv::init()

# Snapshot current package state (records exact package versions)
renv::snapshot()

# Restore on another machine
renv::restore()
```

Commit `renv.lock` to version control. renv installs from CRAN/Bioconductor and does not depend on conda channels.

#### Homebrew / Linuxbrew (User-Managed Tools)

For CLI tools not available as Lmod modules (e.g., developer tools, linters, custom builds):

```bash
# Install Linuxbrew if not already available
# (follow Fred Hutch SciComp guidance for setup)

# Install and pin a tool
brew install samtools
brew pin samtools

# Record installed versions
brew list --versions > brew_versions.txt
```

Homebrew formulae track upstream versions. Pin tools you depend on to avoid surprise upgrades.

#### Mamba (When Necessary)

Always use **mamba** (not conda — conda is very slow). **Anaconda.org access is blocked on Gizmo.** If your project requires conda packages (e.g., bioconda tools not available elsewhere), configure mamba with a project-local `.condarc` pointing to the Fred Hutch mirror:

```yaml
# .condarc (in project directory — avoid user-wide ~/.mambarc in sandboxes)
channel_alias: https://conda-forge.fredhutch.org
channels:
  - conda-forge
  - bioconda
```

```bash
# Point mamba at the project-local config
export CONDARC="$(pwd)/.condarc"

# Create an environment with --prefix to keep it in the project
mamba create --prefix ./envs/myenv python=3.11 samtools

# Lock for reproducibility
conda-lock lock -f environment.yml -p linux-64 -c conda-forge -c bioconda
```

Do not use the Anaconda `defaults` channel. If a package fails to resolve without `defaults`, consider whether a PyPI equivalent (via uv) or an Lmod module can substitute.

**PATH ordering with Lmod:** If a mamba env is active when `module load` runs, the module takes PATH precedence. To have the mamba env shadow a module, deactivate all envs first, then `module load`, then `mamba activate`. See the `fh.python` skill for the full pattern.

When mixing conda and pip: install all conda packages first, then pip packages. If you later need to add a conda package, recreate the environment from scratch rather than mixing install orders.

### Container Digest Pinning

Tags are mutable. A `:latest` or even `:v1.2.3` tag can point to different images over time. Digests are immutable.

```dockerfile
# BAD: tag can change
FROM ubuntu:22.04

# GOOD: pinned to exact image
FROM ubuntu:22.04@sha256:a6d2b38300ce017add71440577d5b0a90460d87e0fd24b834c54e4bba2cefc0d
```

Find the digest:

```bash
# For Docker Hub images
docker inspect --format='{{index .RepoDigests 0}}' ubuntu:22.04

# For images already pulled as SIF
apptainer inspect my_image.sif
```

For Apptainer on Gizmo:

```bash
# Pull by digest (immutable)
apptainer pull docker://ubuntu@sha256:a6d2b38300ce...

# Record the digest in your workflow
echo "container_digest: $(sha256sum my_image.sif | cut -d' ' -f1)" >> run_metadata.yml
```

Pin every stage in multi-stage builds. Pin OS packages to specific versions using snapshot repositories (snapshot.debian.org, snapshot.ubuntu.com).

### Parallel RNG Best Practices

Simply calling `set.seed()` or `np.random.seed()` once is insufficient in parallel contexts because execution order is not guaranteed.

#### Python: SeedSequence

```python
import numpy as np

# Create a root seed
root_seed = 42
ss = np.random.SeedSequence(root_seed)

# Spawn independent streams for each worker
n_workers = 10
child_seeds = ss.spawn(n_workers)
rngs = [np.random.default_rng(s) for s in child_seeds]

# Each worker uses its own RNG
# Results are reproducible regardless of execution order
```

#### Python: Slurm array jobs

```python
import numpy as np
import os

root_seed = 42
task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])

ss = np.random.SeedSequence(root_seed)
child_seeds = ss.spawn(max_task_id + 1)  # pre-spawn all
rng = np.random.default_rng(child_seeds[task_id])
```

#### R: L'Ecuyer-CMRG

```r
# Set the parallel-safe generator
RNGkind("L'Ecuyer-CMRG")
set.seed(42)

# With the future framework (automatic parallel seed handling)
library(future)
library(future.apply)
plan(multisession, workers = 4)
results <- future_lapply(1:100, function(i) rnorm(1), future.seed = TRUE)

# For Slurm array jobs
task_id <- as.integer(Sys.getenv("SLURM_ARRAY_TASK_ID"))
RNGkind("L'Ecuyer-CMRG")
set.seed(42 + task_id)  # Simple but effective for independent tasks
```

Always record: the root seed, the number of workers, the PRNG algorithm, and the spawning method.

### Agent-Generated Code: Reproducibility Risks

AI coding agents introduce specific reproducibility hazards:

**The dependency gap.** Agent-generated code declares a fraction of its actual dependencies. A project that imports scikit-learn actually requires ~52 runtime packages. When agents generate `requirements.txt` or `environment.yml`, they list direct imports, not the full dependency graph. Research shows a ~13.5x expansion from declared to actual runtime dependencies.

**The clean-environment test.** Only 68.3% of agent-generated projects execute without errors in a clean environment (Vangala et al., 2026). Python projects fare best (89.2%), but even that means 1 in 10 fails. Always test agent-generated code in a fresh environment before trusting it for scientific work.

**Non-deterministic generation.** The same prompt to an agent produces different code across runs. This makes the generated code itself a source of non-reproducibility unless the exact code is captured in version control.

**Opaque provenance.** When an agent writes code, there is no automatic record of what was requested, what was generated, and what was modified. Git commits should attribute agent involvement and reference the task.

### Reproducibility Checklist for Agent-Assisted Work

Use this checklist when an AI coding agent has contributed to your analysis:

- [ ] **Dependencies locked.** Run `uv lock` (Python), `renv::snapshot()` (R), or `pip-compile` after any agent modification. Do not trust the agent's dependency declarations.
- [ ] **Clean-environment test.** Create a fresh virtual environment or container, install from lockfile only, and run the analysis.
- [ ] **Container digests recorded.** If using containers, pin by SHA256 digest, not tag.
- [ ] **Module versions pinned.** All `module load` commands specify full version + toolchain.
- [ ] **Random seeds documented.** Root seed, PRNG algorithm, and spawning method recorded.
- [ ] **Git commit attributed.** Commits for agent-generated code note the agent and task.
- [ ] **Outputs validated.** Compare outputs against expected results or a previous known-good run.
- [ ] **Resource requests explicit.** Slurm scripts specify memory, CPUs, GPUs, and walltime (agents tend to omit these).
- [ ] **Parameter files versioned.** All parameters in version-controlled config files, not just CLI arguments.
- [ ] **No floating versions.** No `>=`, no `latest`, no bare module names in any production script or workflow definition.

### Slurm Job Logging for Reproducibility

Record everything needed to reproduce a batch job:

```bash
#!/bin/bash
#SBATCH --job-name=my_analysis
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=8:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# Record execution environment
echo "=== Reproducibility metadata ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Date: $(date -Iseconds)"
echo "Git commit: $(git rev-parse HEAD)"
echo "Git status: $(git status --porcelain | head -5)"
module list 2>&1
uv pip list 2>/dev/null || pip list 2>/dev/null | head -5
echo "================================"

# Your analysis
python my_analysis.py --config params.yml
```

### Workflow Managers

Declarative workflow managers (Snakemake, Nextflow, CWL/WDL) provide reproducibility by design:

- **Provenance recording.** Every step records what ran, with what inputs, and what was produced.
- **Per-step environments.** Snakemake supports conda environments per rule, optionally inside containers. Nextflow pins containers per process.
- **Partial reruns.** Only re-execute steps where inputs changed, avoiding redundant computation.
- **Resource declarations.** Resource requests are part of the workflow definition, not ad-hoc sbatch flags.

Prefer workflow managers over shell script pipelines for any multi-step analysis.

## Principles

- Loose specs for development, locked specs for production and publication
- Pin everything: module versions, package versions, container digests, random seeds
- Test in clean environments before trusting results
- Record provenance: what ran, when, with what, on what hardware
- Treat agent-generated code with extra scrutiny on dependency completeness
- Use workflow managers for multi-step analyses
- Version code, data, parameters, and environments together

## References

- Ziemann, Poulain, Bora (2023). "The five pillars of computational reproducibility." Briefings in Bioinformatics, 24(6). https://pmc.ncbi.nlm.nih.gov/articles/PMC10591307/
- Vangala et al. (2026). "AI-Generated Code Is Not Reproducible (Yet)." arXiv:2512.22387.
- Sandve et al. (2013). "Ten Simple Rules for Reproducible Computational Research." PLOS Computational Biology. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285
- NumPy parallel RNG: https://numpy.org/doc/2.2/reference/random/parallel.html
- uv: https://docs.astral.sh/uv/
- renv: https://rstudio.github.io/renv/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_environments/
- Apptainer docs: https://apptainer.org/docs/user/latest/
