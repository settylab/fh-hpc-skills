# File System Snapshots

Source: https://sciwiki.fredhutch.org/compdemos/snapshots/

## Overview

Snapshots are point-in-time copies of files on Fred Hutch Linux filesystems. They are preserved blocks (not actual copies) that are automatically aged.

## Access

Every directory has a virtual `.snapshot` subdirectory (read-only).

```bash
# List available snapshots
ls .snapshot

# Recover a deleted directory
cp -avr .snapshot/daily.2018_12_09_0010/deleted_dir .
```

The `-a` flag preserves ownership, timestamps, and permissions. The `-v` flag shows verbose output. The `-r` flag copies recursively.

## Key Points

- `.snapshot` is read-only; you cannot alter files there
- Available in home directories and shared folders
- Shared folder restoration may require the original file owner
- Snapshots are automatically created and aged by the system
