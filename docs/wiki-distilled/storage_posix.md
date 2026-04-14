# POSIX File Storage

Source: https://sciwiki.fredhutch.org/scicomputing/store_posix/

## Storage Resources

| Resource | Path | Limit | Backed Up | Shareable |
|----------|------|-------|-----------|-----------|
| Home | `~/` or `/home/HUTCHID` | 1TB | Yes | No |
| Fast | `/fh/fast` | 5TB free/PI | Yes (daily + offsite) | Yes |
| Working | `/fh/working` | 20TB default | Snapshots only | Yes |
| Temp | `/hpc/temp` | N/A | No | Yes |
| Regulated | `/fh/regulated` | TBD | Snapshots | Yes |
| Secure | `/fh/secure` | 750GB/PI | Yes | Yes (audited) |

## Home Storage

- Personal file storage, 1TB max
- Default location for shell login files and private config
- Not suitable for large datasets
- Homelink (links from home into fast/secure via SMB) should be avoided; use fast/secure directly

## Fast Storage Structure

```
/fh/fast/(level-of-charge)/(level-of-access-control)/actual/data
```

PI directories follow naming: `lastname_f` (e.g., `smith_s`).

### Default Folder Layout

| Folder | Purpose | Access Group |
|--------|---------|--------------|
| `/pub` | Publicly readable, hutch-wide sharing | Everyone |
| `/SR` | Shared Resource data (genomics, compbio) | SR + PI group |
| `/app` | Group software/binaries | Lab group |
| `/grp` | Lab folder | `lastname_f_grp` |
| `/project1` | Project-specific | `lastname_f_project1_grp` |
| `/user` | Individual user workspaces | Individual users |

## Genomics Shared Resource

- Data deposited automatically to `/fh/fast/lastname_f/SR/ngs` for sequencing
- Do NOT alter permissions on this folder tree or SR cores cannot deliver data

## Collaboration Folders

- Email scicomp with: Hutchnet IDs, folder path, permission level (read-only or read/write)
- Collaboration folders only in Fast and Working
- "Blind" parent directories: you may have access to a subfolder but not the parent listing

```bash
# This fails (no listing permission on parent):
ls -l /fh/fast/pi_a

# This works (direct path to collaboration folder):
ls -l /fh/fast/pi_a/collaboration
```

SMB mount: `smb://center.fhcrc.org/fh/fast/pi_a/collaboration`

## Secure Storage

- Access auditing enabled
- 750GB per PI limit
- Contact OCDO for data housecall to confirm data classification appropriateness

## Access Paths by Platform

### Linux (CLI / HPC nodes)

| Location | Path |
|----------|------|
| Home | `~/` or `/home/HUTCHID` |
| Fast | `/fh/fast` |
| Temp | `/hpc/temp` |
| Working | `/fh/working` |
| Regulated | `/fh/regulated` |
| Secure | `/fh/secure` |

### Windows (mapped drives)

| Location | Mapped | UNC Path |
|----------|--------|----------|
| Fast | `X:\fast` | `\\center.fhcrc.org\fh\fast` |
| Secure | `X:\secure` | `\\center.fhcrc.org\fh\secure` |
| Working | `X:\working` | `\\center.fhcrc.org\fh\working` |
| HPC Temp | N/A | `\\hpc.chromium.fhcrc.org\temp.chromium` |
| Homes | `H:\` | `\\home.fhcrc.org\homes` |

### Mac (SMB)

```
smb://fhcrc.org;HUTCHID@center.fhcrc.org/fh/fast
smb://fhcrc.org;HUTCHID@center.fhcrc.org/fh/secure
smb://fhcrc.org;HUTCHID@center.fhcrc.org/fh/working
smb://fhcrc.org;HUTCHID@hpc.chromium.fhcrc.org/temp.chromium
smb://fhcrc.org;HUTCHID@home.fhcrc.org/homes
```

Disable volume indexing for performance:
```bash
sudo mdutil -a -i off
sudo mdutil -i on /Volumes/mac-name
```

## Access Requirements

- On-campus: wired network or Marconi wireless
- Off-campus: VPN required
- Regulated storage not accessible from desktop workstations

## Data Transfer

- Motuz: facilitates transfers between Fred Hutch storage and cloud (AWS S3)
