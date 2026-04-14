---
description: "Python on Fred Hutch HPC: uv, modules, virtual envs, mamba, Jupyter, package management"
---

# Python on Fred Hutch HPC

TRIGGER when: user asks about Python on Gizmo/Rhino, virtual environments on the cluster, installing Python packages on HPC, running Jupyter notebooks, or using conda/mamba/uv at Fred Hutch.

## Context

Fred Hutch provides Python through Lmod environment modules on the Rhino login nodes and Gizmo compute cluster. The `fhPython` module is a curated Python distribution with scientific libraries (numpy, scipy, pandas, etc. via the foss toolchain). For project-specific dependency management, **uv** is the recommended tool: it handles virtual environments, dependency resolution, and lockfiles in one fast binary. For mixed-language projects (Python + R + C libraries), mamba with conda-forge/bioconda channels is available as a fallback.

**Important:** Anaconda.org is blocked on Gizmo due to licensing restrictions. If you need conda/mamba, you must use only conda-forge and bioconda channels via the Fred Hutch mirror (see Mamba section below). Never reference the `defaults` channel or anaconda.org.

## Instructions

### Dependency Management Hierarchy

Choose the right tool for the job:

| Tool | Best For | Lockfile |
|---|---|---|
| **uv** (recommended) | Pure Python projects, most scientific work | `uv.lock` |
| **Lmod modules** | Pre-built cluster software (fhPython, numpy, etc.) | `module list` snapshot |
| **mamba** (fallback) | Mixed Python + R + system deps, bioconda tools | `conda-lock` |

### Using uv (Recommended for Python Projects)

uv is a fast Python package manager that handles virtual environments, dependency resolution, and lockfiles. It works entirely from PyPI and requires no conda channels.

```bash
# Initialize a new project (creates pyproject.toml + .python-version)
uv init myproject && cd myproject

# Add dependencies (updates pyproject.toml and uv.lock automatically)
uv add numpy scanpy pandas

# Reproduce the exact environment from lockfile
uv sync

# Run a script in the project environment (no manual activation needed)
uv run python my_analysis.py

# Pin the Python version
uv python pin 3.11.9
```

For one-off scripts or exploratory work:

```bash
# Run with inline dependencies (PEP 723)
uv run --with numpy --with pandas my_script.py

# Use CLI tools without polluting your project
uvx ruff check .
```

Commit both `pyproject.toml` and `uv.lock` to version control. The lockfile pins every transitive dependency with hashes, ensuring reproducibility.

### Loading Python via Lmod Modules

When you need the pre-built cluster Python (e.g., for compatibility with other Lmod-built software or when uv is not appropriate):

```bash
# See available Python versions
module spider Python
module spider fhPython

# Load the Fred Hutch curated Python (1,000+ scientific packages)
ml fhPython/3.11.3-foss-2023a
```

Always load Python via `ml` rather than calling a bare `python3`. This ensures reproducibility and access to the correct version.

### Creating a Virtual Environment (Module-Based)

If using Lmod Python (not uv), create a venv for project isolation:

```bash
# Load the base Python module first
ml fhPython/3.11.3-foss-2023a

# Create a venv in your fast directory (not home — venvs can be large)
python3 -m venv /fh/fast/pi_name/user/myuser/envs/myproject
source /fh/fast/pi_name/user/myuser/envs/myproject/bin/activate

# Install packages inside the venv
pip install some-package
```

Avoid `pip install --user` — it installs to `~/.local/lib/python3.X/site-packages/`, persists across module loads, and causes version conflicts. Use project-specific environments instead.

### Using Mamba (Mixed-Language Fallback)

Use mamba only when your project needs a single environment spanning Python, R, and system-level C libraries (e.g., bioconda tools not available via PyPI). For pure Python work, prefer uv. Always use **mamba**, not conda — conda's resolver is very slow.

**Anaconda.org is blocked.** Configure mamba to use the Fred Hutch conda-forge mirror. Use a project-local `.condarc` (not `~/.mambarc`) so the config stays with the project and does not leak across environments or get lost in ephemeral sandboxes:

```yaml
# .condarc (in your project directory)
channel_alias: https://conda-forge.fredhutch.org
channels:
  - conda-forge
  - bioconda
```

```bash
# Point mamba at the project-local config
export CONDARC="$(pwd)/.condarc"

# Create an environment with --prefix to keep it in the project
mamba create --prefix ./envs/myenv python=3.11 samtools bioconductor-deseq2

# Activate
mamba activate ./envs/myenv

# Lock for reproducibility
conda-lock lock -f environment.yml -p linux-64 -c conda-forge -c bioconda
```

Never use the `defaults` channel. If a package fails to resolve without `defaults`, check whether a PyPI equivalent (via uv) or an Lmod module can substitute.

#### PATH Ordering: Mamba + Lmod Modules

When mixing mamba environments with Lmod modules, activation order determines which binary wins. If a conda env (even base) is active when `module load` runs, the module's PATH entries land *before* the conda portion. Subsequent `mamba activate` only replaces the conda segment, so the module keeps precedence.

To ensure the mamba environment's binaries take priority:

```bash
# 1. Deactivate all conda/mamba envs first
mamba deactivate  # repeat until no env is active

# 2. Load modules
ml fhPython/3.11.3-foss-2023a

# 3. Activate mamba env LAST (its PATH entries go before modules)
mamba activate ./envs/myenv
```

If you do not need both — prefer one or the other rather than mixing.

### Running JupyterLab

**Easiest method:** Use Open OnDemand (web-based, no SSH needed).

**Manual launch on Rhino:**

```bash
ml purge
ml JupyterLab/4.0.3-GCCcore-12.2.0 Seaborn/0.12.2-foss-2022b scikit-learn/1.2.1-gfbf-2022b
jupyter lab --ip=$(hostname) --port=$(fhfreeport) --no-browser
```

Copy the generated URL (e.g., `http://rhino01:16053/...`) into your browser. You must be on the Fred Hutch network or VPN.

Use `ml avail JupyterLab` to see all available JupyterLab versions.

### Requesting New Software

Email scicomp@fredhutch.org or file an issue on the `easybuild-life-sciences` GitHub repository.

### Scientific Software Inventory

Browse available Python modules at: https://fredhutch.github.io/easybuild-life-sciences/python/

## Principles

- Use uv for Python dependency management by default; fall back to mamba only for mixed-language projects
- Never reference anaconda.org or the defaults channel; use only conda-forge and bioconda via the Fred Hutch mirror
- Pin all dependencies with lockfiles (uv.lock or conda-lock) for reproducibility
- Load modules explicitly with version numbers for reproducible analyses
- Request only the resources you need (CPUs, memory, time)
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies

## References

- uv documentation: https://docs.astral.sh/uv/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_python/
- EasyBuild Python inventory: https://fredhutch.github.io/easybuild-life-sciences/python/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_running/
