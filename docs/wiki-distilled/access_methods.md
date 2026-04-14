# Access Methods (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/access_methods/

## Key Facts

- **rhino**: Three locally managed servers functioning as data and compute hubs. Primary SSH target.
- **Open OnDemand**: Web-based interface for file management, terminal, RStudio, Jupyter.
- **SSH**: Primary protocol for remote CLI access.
- **NoMachine NX**: Remote desktop software for graphical access. Allows disconnect/resume. Requires campus network or VPN.
- **VPN**: Required for off-campus access. Only available on Hutch-managed devices. Contact IT Service Desk.

### SSH Clients by OS

- **Windows**: PuTTY (via Software Center), cmd.exe (needs OpenSSH Client), Windows Terminal (Microsoft Store + OpenSSH Client).
- **macOS**: Default terminal or iTerm2. XQuartz needed for X11/graphical apps. Connect: `ssh -Y HutchID@rhino`
- **Linux**: OpenSSH pre-installed. Terminator recommended for split-window.

## Commands & Examples

### SSH Connection

```bash
# macOS/Linux
ssh HutchID@rhino

# With X11 forwarding (graphical apps)
ssh -Y HutchID@rhino
```

### SSH Config (macOS/Linux) — `~/.ssh/config`

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

### SSH Config (Windows) — `C:\Users\<HUTCHID>\.ssh\config`

```
Host rhino
  User <HUTCHID>
  MACs hmac-sha2-512
```

### SSH Key Generation & Distribution

```bash
# Generate key (macOS/Linux)
ssh-keygen

# Copy key to remote host
ssh-copy-id HutchID@rhino

# Windows: use puttygen for key generation
```

### Passphrase Management

```bash
# macOS 12+
ssh-add --apple-use-keychain <keypath>

# macOS 11 and earlier
ssh-add -K <keypath>

# Linux
eval $(ssh-agent)
ssh-add [keyfile]

# Windows: use pageant.exe (PuTTY suite)
```

### tmux (Session Persistence)

```bash
module load tmux   # or: ml tmux
tmux               # start new session
tmux attach        # or: tmux a — reattach
# ctrl-b d         — detach
# exit or ctrl-d   — end session
```

### X11 Verification

```bash
echo $DISPLAY   # should show a value if X11 is forwarded
xeyes           # visual test of X11 forwarding
```

## SSH Config Parameters Reference

| Config Parameter    | CLI Flag          | Values  | Purpose                                |
|---------------------|-------------------|---------|----------------------------------------|
| ForwardAgent        | -o ForwardAgent   | yes/no  | Forward agent requests to client       |
| ProxyJump           | -J                | hostname| Use intermediate host for connection   |
| ForwardX11          | -X                | yes/no  | Tunnel X11 server connection           |
| ForwardTrustedX11   | -Y                | yes/no  | Bypass X11 security extensions         |

## Common Pitfalls

- Passphrase-less SSH keys are a security violation at Fred Hutch.
- GNU Screen instances are NOT shared across rhino servers (rhino01/02/03). Use tmux instead.
- Closing SSH terminates running child processes (TCP connection tied). Use tmux/screen for persistence.
- X Window System operates in reverse: local device runs X server, remote program is client.
- VPN only works on Hutch-managed devices. Personal devices cannot use VPN.
- Desktop computing support is handled by Center IT divisions (ADM, CRD, VIDD, BSD, HB, PHS), not SciComp.

## Cross-references

- /scicomputing/access_overview/ (parent)
- /scicomputing/access_credentials/ (HutchNet ID needed for SSH)
