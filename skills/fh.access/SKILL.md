---
description: "How to access Fred Hutch HPC resources: SSH, NoMachine, VPN, Open OnDemand, and session persistence"
---

# Accessing Fred Hutch HPC Resources

## Quick Start

The primary compute hosts are the **rhino** servers (rhino01, rhino02, rhino03). Connect via SSH using your HutchNet ID.

```bash
ssh HutchID@rhino
```

For graphical/X11 applications, use `-Y`:

```bash
ssh -Y HutchID@rhino
```

## Access Methods

### 1. SSH (Primary Method)

**macOS/Linux**: Use the built-in terminal. iTerm2 recommended on macOS. Terminator recommended on Linux.

**Windows**: PuTTY (install via Software Center), Windows Terminal (Microsoft Store), or cmd.exe with OpenSSH Client enabled.

### 2. Open OnDemand (Web-Based)

Browser-based interface providing file management, terminal access, and interactive apps (RStudio, Jupyter). No SSH client needed.

### 3. NoMachine NX (Remote Desktop)

Graphical remote desktop with session persistence (disconnect and resume later). Requires campus network or VPN.

### 4. VPN (Off-Campus Access)

Required for accessing Fred Hutch resources from outside campus. Only works on Hutch-managed devices. Contact IT Service Desk for setup.

## SSH Configuration

### macOS/Linux (`~/.ssh/config`)

```
Host *.fhcrc.org
    UseKeychain yes
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_rsa
    ForwardX11 yes
    ForwardX11Trusted yes
    ForwardAgent yes
    User <username>
```

### Windows (`C:\Users\<HUTCHID>\.ssh\config`)

```
Host rhino
  User <HUTCHID>
  MACs hmac-sha2-512
```

## SSH Key Setup

```bash
# Generate a key pair (use a strong passphrase — passphrase-less keys are a security violation)
ssh-keygen

# Copy public key to rhino
ssh-copy-id HutchID@rhino
```

### Passphrase Caching

```bash
# macOS 12+
ssh-add --apple-use-keychain ~/.ssh/id_rsa

# macOS 11 and earlier
ssh-add -K ~/.ssh/id_rsa

# Linux
eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa
```

On Windows, use `pageant.exe` from the PuTTY suite.

## Session Persistence with tmux

SSH sessions terminate running processes when disconnected. Use tmux to keep sessions alive.

```bash
ml tmux          # load tmux module
tmux             # start new session
tmux attach      # reattach to existing session (or: tmux a)
```

Key bindings: `Ctrl-b d` to detach, `exit` or `Ctrl-d` to end session.

**Note**: GNU Screen is also available but instances are NOT shared across rhino servers. Prefer tmux.

## X11 Forwarding (Graphical Apps)

Requires XQuartz on macOS. Verify it works:

```bash
echo $DISPLAY    # should show a value
xeyes            # visual test
```

## SSH Config Parameters

| Parameter         | CLI Flag | Purpose                              |
|-------------------|----------|--------------------------------------|
| ForwardAgent      | -A       | Forward SSH agent to remote host     |
| ProxyJump         | -J       | Jump through intermediate host       |
| ForwardX11        | -X       | Enable X11 forwarding                |
| ForwardX11Trusted | -Y       | Trusted X11 (bypass security checks) |

## Common Pitfalls

- **Passphrase-less SSH keys are a security violation.** Always use a strong passphrase.
- **VPN only works on Hutch-managed devices.** Personal laptops cannot use the VPN.
- **Closing SSH kills child processes.** Always use tmux for long-running work.
- **Screen sessions don't transfer across rhino nodes.** If you connected to rhino01 but your screen is on rhino03, you must SSH to rhino03 specifically.
- **X11 is reversed**: Your local machine runs the X server; the remote program is the client.
- **Desktop computing support** is handled by Center IT (ADM, CRD, VIDD, BSD, HB, PHS), not SciComp.

## Getting Help

- SciComp email: scicomp@fredhutch.org
- Slack: FHData Slack workspace
- Wiki: https://sciwiki.fredhutch.org/scicomputing/access_methods/
