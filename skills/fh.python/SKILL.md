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

### Python in Slurm Jobs

Slurm jobs run on Gizmo compute nodes, which may have a different OS/glibc version than login nodes. Python that works on Rhino can fail on compute nodes. Choose the right interpreter:

#### Interpreter Selection

| Interpreter | Portability | Notes |
|---|---|---|
| **uv-managed** (recommended) | Works everywhere | Standalone build, no glibc dependency issues |
| **Lmod module** | Works on compute nodes | Must `module load` in sbatch script — never call the binary by direct path |
| **Other Python** (Homebrew, pyenv, system) | Unreliable | May be linked against a glibc newer than compute nodes provide |

**uv-managed Python** is the most portable option. Install a standalone Python into the project directory so it works on any node:

```bash
# In your project directory
export UV_PYTHON_INSTALL_DIR="$(pwd)/.python"
uv python install 3.12
uv venv --python 3.12
uv sync
```

**Module Python** works on compute nodes but MUST be loaded via `module load`, not by calling `/app/software/Python/.../bin/python3` directly. The module sets `LD_LIBRARY_PATH`, `PYTHONPATH`, and toolchain variables that the binary depends on.

**Other Python interpreters** (Homebrew/Linuxbrew, pyenv-built, manually compiled, etc.) may be linked against a glibc version newer than what compute nodes provide. The symptom is `error while loading shared libraries` when the job runs, sometimes referencing an unexpected Python version — the root cause is the glibc mismatch, not the version shown in the error. If you hit this, switch to uv-managed or module Python.

#### C Extension Conflicts with Lmod Libraries

When pip packages with C extensions (`python-igraph`, `h5py`, `netCDF4`, etc.) are installed alongside Lmod modules that provide the same C libraries, symbol conflicts cause `undefined symbol` or segfaults at import time. Solutions:

- **Pin versions that bundle their own C library.** Example: `igraph==0.11.8` bundles libigraph; `python-igraph==1.0.0` dynamically links to the system's `libigraph.so` and conflicts with the Lmod-provided version.
- **Purge conflicting modules** before running the job (`ml purge` then load only what you need).
- **Use uv-managed Python** to avoid Lmod entirely — no module means no conflicting shared libraries.

#### Example Sbatch Script

```bash
#!/bin/bash
#SBATCH --job-name=analysis
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00

# Option A: uv-managed (recommended)
export UV_PYTHON_INSTALL_DIR="/fh/fast/pi_name/user/myuser/myproject/.python"
export UV_CACHE_DIR="/hpc/temp/$USER/uv-cache"   # avoid slow NFS cache scans
cd /fh/fast/pi_name/user/myuser/myproject
uv run python my_analysis.py

# Option B: Lmod module
# ml purge
# ml fhPython/3.11.3-foss-2023a
# source /fh/fast/pi_name/user/myuser/envs/myproject/bin/activate
# python my_analysis.py
```

Key points:
- **Activate the venv in the script body**, not in `#SBATCH` directives (which are just comments to the shell).
- **Use absolute paths** for the venv and project directory. `$SLURM_SUBMIT_DIR` is the directory where `sbatch` was called, which may not be the project root.
- **Set `UV_CACHE_DIR`** to scratch (`/hpc/temp/$USER/...`) when using uv. The default cache location on NFS can cause slow startup as uv scans thousands of cached wheels.
- **Do not rely on `~/.bashrc`** being sourced — Slurm jobs use non-interactive shells by default.

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
