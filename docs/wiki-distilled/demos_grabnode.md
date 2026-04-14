# Using grabnode for Interactive Compute

Source: https://sciwiki.fredhutch.org/compdemos/grabnode/

## Overview

`grabnode` moves users from the shared rhino node to a dedicated gizmo cluster node for compute-intensive tasks.

## Usage

```bash
grabnode
```

The command asks four configuration questions:
1. **CPU/cores** (range 1-36): Number of cores needed
2. **Memory** (default 20 GB): RAM allocation
3. **Duration** (1-7 days): How long the node is reserved
4. **GPU** (yes/no): Whether a GPU is needed

## Expected Outcome

Upon allocation, the prompt changes to show the gizmo node:
```
username@gizmof127:~$
```

## Best Practices

- Request only resources matching actual task requirements
- Multiple CPUs are rarely necessary unless specifically needed
- Uses the `interactive` partition with per-user limits (36 cores, 1 GPU)

## Troubleshooting

"Invalid Account" error indicates incomplete PI account setup. Contact `scicomp` for resolution.
