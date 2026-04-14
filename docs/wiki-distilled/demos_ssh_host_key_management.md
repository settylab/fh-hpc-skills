# SSH Host Key Management

Source: https://sciwiki.fredhutch.org/compdemos/ssh_host_key_management/

## Overview

When hosts are reinstalled, SSH keys change, triggering "DNS spoofing" or "host identification changed" errors.

## Removing Old Keys (Linux/macOS)

```bash
ssh-keygen -R <hostname>
ssh-keygen -R <hostname>.fhcrc.org

# Example for rhino
ssh-keygen -R rhino.fhcrc.org
```

After removal, the next login prompts to add the refreshed key.

## Windows (PuTTY)

PuTTY displays a prompt when key mismatches occur. Click "Yes" to accept and replace the outdated key.

## Validating Host Identity

Contact SciComp with the host's key fingerprint (including key type: rsa2, ecdsa) to verify the connecting host is genuine.
