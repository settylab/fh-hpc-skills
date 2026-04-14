# Python at Fred Hutch

Source: https://sciwiki.fredhutch.org/scicomputing/software_python/

## Common Python Packages (in fhPython module)

- `numpy` and `scipy` -- scientific computing
- `pandas` -- data analysis and dataframes
- `biopython` -- genetic and genomic data

Package discovery: PyPI.org, GitHub, custom development

## Accessing Python

### Local Installation

Recommended tools: **Miniforge** or **uv** for new users. Conda-forge installation per conda-forge project docs.

### On Rhino Cluster

**View available modules:**
```bash
module avail Python/3
module avail fhPython
```

**Load fhPython (custom version with 1,000+ libraries):**
```bash
ml fhPython/3.8.6-foss-2020b-Python-3.8.6
```

**Create virtual environment:**
```bash
ml fhPython/3.8.6-foss-2020b-Python-3.8.6
python3 -m venv ~/mypython
source ~/mypython/bin/activate
```

**Install packages locally:**
```bash
pip3 install --upgrade --user mypkg
```

**Request software:** Email scicomp or file GitHub issue in easybuild-life-sciences repository.

### Jupyter on Rhino

**Recommended:** Use Open OnDemand for easiest launch.

**JupyterLab launch:**
```bash
ml purge
ml JupyterLab/4.0.3-GCCcore-12.2.0 Seaborn/0.12.2-foss-2022b scikit-learn/1.2.1-gfbf-2022b
jupyter lab --ip=$(hostname) --port=$(fhfreeport) --no-browser
```

Access via generated HTTP URL (e.g., `http://rhino01:16053/...`).

Use `ml avail JupyterLab` to see available versions.

## IDEs

### Visual Studio Code

- Install VS Code + extensions: Code Runner, Python, R, markdownlint
- Requires Python >= 3.6
- Key shortcuts: `Alt+Cmd+C` (copy path), `Ctrl+Cmd+N` (run code), `fn+F9` (breakpoints)
- SSH extension for remote development
- WSL integration for Windows
- Git integration with merge conflict resolution

### PyCharm

- Free community edition and paid subscription
- Key shortcuts: `Cmd+K` (commit), `Cmd+B` (go to definition), `Alt+Shift+E` (execute in IPython)
- pytest recommended for test runner
- Refactoring tools, Find Usages
- Customizable PEP-8 lint hints

### JupyterLab

- `.ipynb` files with executable code chunks and markdown
- Key shortcuts: `Shift+Enter` (run cell), `A`/`B` (cell above/below), `DD` (delete), `M`/`Y` (markdown/code)
- Extensions: flake8 linter, debugger, git, variable inspector, R kernel

## Scientific Software Inventory

Detailed module info: fredhutch.github.io/easybuild-life-sciences/python/

## Training

- "Intro to Python" class (pandas)
- "Intermediate Python: Programming" class (numpy, scipy)
- Office hours for Scientific Computing support
