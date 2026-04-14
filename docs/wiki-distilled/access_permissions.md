# Access Permissions (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/access_permissions/

## Key Facts

- Fred Hutch SciComp-managed filesystems use UNIX traditional access control lists (ACLs).
- Storage is organized by Principal Investigator (PI).
- PI folders named `lastname_f`.
- Associated groups named `lastname_f_grp` containing lab members.
- Subfolders within PI directories can have distinct ACLs for collaborations and external access.

### Permission Model (standard UNIX)

Three role categories:
1. **User** (file owner)
2. **Group** (lab members in `lastname_f_grp`)
3. **Other** (everyone else)

Each role can have read (r), write (w), and/or execute (x) permissions.

## Commands & Examples

No specific commands listed on the page. Standard UNIX permission tools apply:

```bash
# Check permissions
ls -la /path/to/directory

# Check ACLs
getfacl /path/to/directory
```

## Common Pitfalls

- For access issues, email `scicomp` with: the folder path, error messages, and CC the PI or manager associated with that storage.
- Subfolders may have different ACLs than their parent PI directory. Do not assume inherited permissions.

## Cross-references

- /scicomputing/access_overview/ (parent)
- /scicomputing/access_credentials/ (how to get your HutchNet ID that determines your identity)
