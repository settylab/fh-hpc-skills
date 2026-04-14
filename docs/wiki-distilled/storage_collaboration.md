# Collaboration and Data Transfer

Source: https://sciwiki.fredhutch.org/scicomputing/store_collaboration/

## Data Transfer Tools

### HutchGO (Globus)

- Globus-based infrastructure maintained by SciComp
- Secure, high-performance transfers internally and externally
- Transfers directly from Hutch storage (fast, working, temp) without preliminary copies

### Aspera

**Faspex**: Web-based tool for rapid large-file transfers. Users upload data to Aspera server, generate shareable email links. Storage is temporary and unbackedup; data deleted after a short period.

**Shares**: Similar to Faspex with CLI capabilities, though Fred Hutch's instance does not support CLI directly.

## Collaborative Storage Options

### Collaboration Folders (POSIX)

- Available in Fast and Working storage only
- Request via email to scicomp with: Hutchnet IDs, folder path, permission level
- See POSIX storage docs for details

### AWS S3

- Supports secure data sharing with collaborators
- Multiple sharing methods: direct access, pre-signed URLs, public access, cross-account

### OneDrive

- Office 365 cloud storage
- 2TB per user allocation
- Real-time collaboration and version control
- Sharing links do NOT expire

**Best practices for OneDrive:**
- Do not sync with non-Hutch devices
- Use "Specific people" sharing rather than broad access
- Contact dataprotection@fredhutch.org for data protection questions
