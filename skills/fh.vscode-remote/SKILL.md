---
description: "VS Code remote development on Fred Hutch HPC cluster with LMOD modules"
---

# VS Code Remote Development on Fred Hutch HPC

TRIGGER when: user mentions VS Code, VSCode, remote development, or IDE on the cluster

## Context

VS Code can connect to Fred Hutch rhino/gizmo nodes via Remote SSH for development. Special configuration is needed to make LMOD environment modules work correctly with VS Code Python environments.

## Instructions

### Login Node Warning

**Do not run VS Code Remote-SSH on rhino login nodes for extended development sessions.** VS Code's language servers, file watchers, and extensions consume significant CPU and memory. On shared login nodes, this degrades the experience for all users and may result in your processes being killed without warning.

Instead, connect VS Code to a compute node:

```bash
# 1. SSH into rhino and grab a compute node
ssh rhino
grabnode   # request resources, note the node name (e.g., gizmok123)

# 2. In VS Code on your local machine, connect to the compute node directly
#    Add to ~/.ssh/config:
Host gizmo-dev
    HostName gizmok123       # replace with your allocated node
    ProxyJump rhino          # tunnel through rhino
    User your_username

# 3. Connect VS Code Remote-SSH to "gizmo-dev"
```

Alternatively, use the `short` partition with a time limit so forgotten sessions don't occupy resources indefinitely:
```bash
srun --partition=short --time=4:00:00 --cpus-per-task=4 --pty bash
# Note the hostname, then connect VS Code to it
```

Short-lived, light editing on rhino (quick file edits, git operations) is fine. Sustained development with active language servers and debugging belongs on a compute node.

### Basic Remote SSH Setup

1. Install VS Code locally with the "Remote - SSH" extension
2. Connect to a `grabnode` allocation via Remote SSH (not the rhino login node for sustained work)
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
