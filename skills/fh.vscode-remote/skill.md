---
description: "VS Code remote development on Fred Hutch HPC cluster with LMOD modules"
---

# VS Code Remote Development on Fred Hutch HPC

TRIGGER when: user mentions VS Code, VSCode, remote development, or IDE on the cluster

## Context

VS Code can connect to Fred Hutch rhino/gizmo nodes via Remote SSH for development. Special configuration is needed to make LMOD environment modules work correctly with VS Code Python environments.

## Instructions

### Basic Remote SSH Setup

1. Install VS Code locally with the "Remote - SSH" extension
2. Connect to `rhino` or a `grabnode` allocation via Remote SSH
3. Open your project folder on the remote filesystem

### Python with LMOD Modules

LMOD modules must be loaded BEFORE activating virtual environments because venvs use symlinks to the base Python interpreter.

#### Setup Script (lmod_venv.sh)

Save to your Linux home directory. This script:
- Preserves the current LMOD module list to a `module_list` file
- Captures `LD_LIBRARY_PATH`
- Modifies the venv activate script to reload modules and library paths

#### Workflow

```bash
# 1. Load your modules first
ml Python/3.10.8-GCCcore-12.2.0

# 2. Create project and venv
mkdir -p ~/projects/myproject
cd ~/projects/myproject
python3 -m venv myenv

# 3. Activate with LMOD support
source ~/lmod_venv.sh
create_lmod_venv myenv
```

In VS Code: Command Palette > "Python: Create Environment" > point to venv/bin/activate.

### Critical Rules

- ALWAYS load the exact same module version before activating a venv
- NEVER load modules after environment activation
- NEVER load modules in shell startup files (~/.bashrc) -- causes unexpected results and slow logins

### Module Version Management

Always specify full versions:
```bash
ml Python/3.10.8-GCCcore-12.2.0   # Good
ml Python                           # Bad (default may change)
```

Save module collections for reproducibility:
```bash
module load Python/3.10.8-GCCcore-12.2.0 SciPy-bundle/2022.05-foss-2022a
module save myproject_modules
# Later:
ml restore myproject_modules
```

### Recommended VS Code Extensions

- **Paste Image** (mushan): Ctrl+Alt+V for image insertion
- **Code Spell Checker** (Street Side Software): Real-time spell checking
- **MarkdownLint** (David Anson): Markdown formatting compliance

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki VS Code LMOD: https://sciwiki.fredhutch.org/compdemos/VS-Code_lmod/
- SciComp Wiki Module Versions: https://sciwiki.fredhutch.org/compdemos/managing-module-versions/
- SciComp Wiki Python Environments: https://sciwiki.fredhutch.org/compdemos/python_virtual_environments/
