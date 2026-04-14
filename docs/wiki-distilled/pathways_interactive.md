# Getting and Using Interactive Sessions

Source: https://sciwiki.fredhutch.org/pathways/path-interactive/

## Key Facts

- Interactive sessions begin by connecting to a rhino login node
- Rhino nodes are shared login nodes; gizmo nodes are the compute cluster
- A HutchNet ID associated with a PI account is required for job submission
- Campus network connection (on-site or VPN) is mandatory
- Terminal options: Terminal/iTerm2 (Mac), Microsoft Terminal or PuTTY (Windows), native terminal (Linux)
- Home directory is personal storage; contact SciComp if access errors occur
- Common storage paths: /fh/fast/ (Fast File), /fh/temp/ (Temp, not backed up)
- The default shell is bash with GNU/Linux utilities

## Commands & Examples

```bash
# Connect to rhino from terminal
ssh HutchNetID@rhino

# Check your home directory
cd ~
pwd

# Common storage locations
ls /fh/fast/PI_LastName/
ls /fh/temp/
```

## Common Pitfalls

- Not connecting to VPN before attempting SSH from off-campus
- Running compute-intensive tasks directly on rhino (use grabnode instead)
- Confusing rhino (login node) with gizmo (compute nodes)
- Not having your HutchNet ID associated with a PI account

## Cross-references

- Getting a gizmo session: /pathways/path-grab/
- Batch computing: /pathways/path-batch-computing/
- Access methods: /scicomputing/access_methods/
