# Python Virtual Environments on Fred Hutch HPC

Source: https://sciwiki.fredhutch.org/compdemos/python_virtual_environments/

## Overview

Guide for creating isolated Python installations with independent libraries. Fred Hutch provides fhPython environment modules with pre-installed libraries; use virtual environments when you need packages not available in those modules.

## Python venv Method

### Workflow

```bash
# 1. Load a Python module (always specify version)
ml Python/3.10.8-GCCcore-12.2.0
which python
python --version

# 2. Create virtual environment
python -m venv testenv

# 3. Activate it
. ./testenv/bin/activate
```

### Critical Detail

The virtual environment uses symbolic links to the base Python interpreter. You MUST load the identical module version BEFORE activation, or unpredictable behavior will occur. Loading modules after environment activation produces unsafe results.

## Conda / Miniforge

Fred Hutch recommends **Miniforge** (not Anaconda, which requires paid licensing at Fred Hutch).

### Installation

1. Download appropriate Miniforge version
2. Run installer (`-h` flag for help)
3. Configure channels per Fred Hutch documentation (VPN required)

### Shell Integration

```bash
enable_conda(){
  eval "$(/home/username/bin/miniforge3/bin/conda shell.bash hook)"
}
```

### Build Tools

```bash
conda install gcc_linux-64 gxx_linux-64 gfortran_linux-64
conda install gcc_linux-64==11.2.0 gxx_linux-64==11.2.0 gfortran_linux-64==11.2.0
```

## Best Practices

- Always specify full module versions for reproducibility
- Prefer venv when only Python packages are needed
- Prefer Miniforge/conda when non-Python dependencies are required
- Do not install packages directly to home directories
