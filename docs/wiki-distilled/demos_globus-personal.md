# Globus Connect Personal

Source: https://sciwiki.fredhutch.org/compdemos/globus-personal/

## Overview

Globus Connect Personal enables file transfers between systems using Globus infrastructure. Free, lightweight client. Data does not pass through Globus control system.

## Setup on Rhino

### Step 1: Authenticate
Go to https://app.globus.org/ and select "Fred Hutchinson Cancer Research Center" for HutchNet login.

### Step 2: Create Endpoint
```bash
ml GlobusConnectPersonal
globusconnect -setup --no-gui
```
Copy the generated OAuth URL to your browser, get auth code, enter it in terminal with a distinctive endpoint name.

### Step 3: Start Endpoint
```bash
ml GlobusConnectPersonal
nohup globusconnect -start &
```
Run in tmux/screen or with nohup. Verify status in Web UI under Collections > "Administered By You."

### Step 4: Configure Paths
Edit `~/.globusonline/lta/config-paths`:
```
~/,0,1
/hpc/temp/_ADM/SciComp,0,1
```
Format: `<path>,<sharing>,<read|write>` (0=read-only, 1=read-write)

Restart after changes:
```bash
globusconnect -stop
globusconnect -start
```

## Key Notes

- Only one endpoint should run at a time
- Home directory available by default
- Manage transfers via browser at https://app.globus.org/
