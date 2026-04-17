---
description: "Essential Linux and shell commands for Fred Hutch HPC users"
---

# Essential Linux/Shell for HPC Users

TRIGGER when: user asks about Linux commands on Rhino/Gizmo, shell scripting for HPC, Bash basics for the cluster, navigating the filesystem, or getting started with the command line at Fred Hutch.

## Context

The Fred Hutch HPC cluster (Rhino login nodes, Gizmo compute nodes) runs Linux. All cluster interaction beyond Open OnDemand requires basic shell proficiency. The default shell is Bash. Understanding core Linux commands is essential for file management, job submission, and software usage on the cluster.

## Instructions

### Available Shells

- **Bash** (Bourne Again SHell): Standard on Rhino/Gizmo and most Linux systems
- **zsh**: Default on macOS, Bash-compatible, available on the cluster
- **PowerShell**: Windows only, not available on the cluster

### Essential Navigation

```bash
# Where am I?
pwd

# List files
ls -la

# Change directory
cd /fh/fast/lastname_f/
cd ~          # Home directory
cd -          # Previous directory

# File operations
cp source dest
mv source dest
rm file
mkdir -p path/to/dir
```

### File Viewing and Searching

```bash
# View file contents
cat file.txt
less file.txt       # Paginated viewing (q to quit)
head -n 20 file.txt # First 20 lines
tail -n 20 file.txt # Last 20 lines

# Search within files
grep "pattern" file.txt
grep -r "pattern" directory/

# Find files
find /path -name "*.txt"
```

### Permissions and Ownership

```bash
# View permissions
ls -la

# Change permissions
chmod 755 script.sh   # rwxr-xr-x
chmod u+x script.sh   # Add execute for owner

# Change group (for shared directories)
chgrp groupname file
```

### Pipes and Redirection

```bash
# Pipe output to another command
cat file.txt | grep "pattern" | sort | uniq

# Redirect output
command > output.txt      # Overwrite
command >> output.txt     # Append
command 2> errors.txt     # Stderr only
command > out.txt 2>&1    # Both stdout and stderr
```

### Shell Scripting Basics

```bash
#!/bin/bash
# A simple script

INPUT_DIR="/fh/fast/lastname_f/data"
OUTPUT_DIR="/fh/fast/lastname_f/results"

for file in "$INPUT_DIR"/*.fastq; do
    echo "Processing $file"
    # your processing command here
done
```

Make scripts executable: `chmod +x script.sh`

### Process Management

```bash
# View your running processes
ps aux | grep $USER

# Kill a process
kill PID
kill -9 PID   # Force kill

# Run in background
command &

# Check disk usage
df -h /fh/fast/
du -sh directory/
```

### Useful Cluster-Specific Paths

| Path | Purpose |
|------|---------|
| `~` or `/home/username` | Home directory (small, backed up) |
| `/fh/fast/lastname_f/` | Lab fast storage (large, primary workspace) |
| `/hpc/temp/setty_m/$USER/` | Temporary scratch (NFSv4.1, 30-day auto-delete from creation date) |

### Learning Resources

- Software Carpentry's Unix Shell course (recommended starting point)
- The Linux Documentation Project's Introduction to Linux
- The Linux Documentation Project's Bash Beginner's Guide
- explainshell.com: paste any command to get an explanation

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_linux101/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_overview/
