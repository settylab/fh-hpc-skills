# VS Code with LMOD Modules

Source: https://sciwiki.fredhutch.org/compdemos/VS-Code_lmod/

## Overview

Configure VS Code for remote HPC development with LMOD modules, specifically for Python virtual environments.

## Setup Steps

1. Save the `lmod_venv.sh` script to your Linux home directory

2. Create project structure:
```bash
mkdir -p ~/projects/scGPT
cd projects/scGPT
```

3. Create virtual environment:
```bash
python3 -m venv venv-name
```

4. Activate with LMOD support:
```bash
source ~/lmod_venv.sh
create_lmod_venv venv-name
```

5. In VS Code: Use Remote SSH connection, then select "Python: Create Environment" from command palette, pointing to venv/bin/activate

## What lmod_venv.sh Does

- Preserves the current LMOD module list to a `module_list` file
- Captures `LD_LIBRARY_PATH` environment variable
- Modifies the virtual environment's activate script to reload modules and library paths on activation
- Custom deactivate function handles cleanup (resets env vars, purges modules, restores Python path)
