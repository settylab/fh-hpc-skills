---
description: "Python on Fred Hutch HPC: modules, virtual envs, conda, Jupyter, package management"
---

# Python on Fred Hutch HPC

TRIGGER when: user asks about Python on Gizmo/Rhino, virtual environments on the cluster, installing Python packages on HPC, running Jupyter notebooks, or using conda/mamba/uv at Fred Hutch.

## Context

Fred Hutch provides Python through Lmod environment modules on the Rhino login nodes and Gizmo compute cluster. The `fhPython` module is a curated Python distribution with scientific libraries (numpy, scipy, pandas, etc. via the foss toolchain, plus additional packages like rich, Pygments, and plotsr). Users can also create virtual environments or use conda (Miniforge) for isolated package management. JupyterLab is available via modules or Open OnDemand.

## Instructions

### Loading Python on the Cluster

```bash
# See available Python versions
module avail Python/3
module avail fhPython

# Load the Fred Hutch curated Python (1,000+ scientific packages)
ml fhPython/3.11.3-foss-2023a
```

Always load Python via `ml` rather than calling a bare `python3`. This ensures reproducibility and access to the correct version.

### Creating a Virtual Environment

```bash
# Load the base Python module first
ml fhPython/3.11.3-foss-2023a

# Create a venv in your home directory
python3 -m venv ~/mypython
source ~/mypython/bin/activate

# Install packages inside the venv
pip install some-package
```

### Installing Packages Without a Venv

```bash
pip3 install --upgrade --user mypkg
```

This installs to `~/.local/lib/python3.X/site-packages/`. Be aware that `--user` installs persist across module loads and can cause version conflicts. Virtual environments are preferred.

### Local Installation (Laptop/Workstation)

For local Python, Fred Hutch recommends **Miniforge** or **uv**:
- Miniforge: conda-forge based distribution, follow conda-forge project instructions
- uv: fast Python package installer and resolver

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

- Request only the resources you need (CPUs, memory, time)
- Use virtual environments for project isolation and reproducibility
- Load modules explicitly with version numbers for reproducible analyses
- Respect shared infrastructure and other users
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_python/
- EasyBuild Python inventory: https://fredhutch.github.io/easybuild-life-sciences/python/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_running/
