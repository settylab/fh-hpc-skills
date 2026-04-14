---
description: "GitHub at Fred Hutch: organization, repos, security policies, version control"
---

# GitHub at Fred Hutch

TRIGGER when: user asks about using GitHub at Fred Hutch, joining the Fred Hutch GitHub organization, Git on the cluster, version control for research code, or code sharing policies.

## Context

Fred Hutch maintains a GitHub Organization (github.com/fredhutch) for collaborative research code. Git is essential for version control on the cluster, and all researchers are encouraged to use it. Security is critical: Git repos must never contain protected health information, credentials, or infrastructure details.

## Instructions

### Getting Started

1. Create a free GitHub account at github.com/join
2. Join the Fred Hutch GitHub Organization by emailing SciComp with your GitHub user ID
3. You gain access to create private repositories under the organization

### Repository Types

- **Public**: Default, supports open science principles
- **Private**: Available through Fred Hutch GitHub Organization for sensitive (non-PHI) work

### Git on the Cluster

Git is available on Rhino/Gizmo. Use command-line Git for all cluster work:

```bash
git clone https://github.com/FredHutch/your-repo.git
git add .
git commit -m "description of changes"
git push origin main
```

### Recommended Git Clients

| Client | Best For | Notes |
|--------|----------|-------|
| **Command Line Git** | Cluster work, advanced users | Full feature access, required for Rhino/Gizmo |
| **GitHub Desktop** | Beginners | Free GUI, desktop.github.com |
| **GitKraken** | Advanced collaboration | Free for academics |
| **RStudio** | R developers | Built-in Git integration |
| **VS Code** | Python/general development | Git integration with merge conflict resolution |

### Security Policies (CRITICAL)

**Git does NOT provide HIPAA-compliant access controls, audit logging, or encryption.**

**NEVER commit to any repository:**
- Protected health information (PHI)
- Database/storage credentials (usernames, passwords, tokens, access keys)
- Server names, IP addresses, network names
- API tokens, AWS credentials

**Best practices:**
- Load secrets from environment variables or external config files (never hardcode)
- Use the Fred Hutch Vault secrets management system for credentials
- Preprocess and sanitize sensitive data in secure backend systems before committing
- Add `.gitignore` entries for `.env`, credential files, and data directories

### Code Organization Best Practices

1. Separate raw and processed data storage
2. Organize source code and results with clear labeling
3. Include a license and README with project overview
4. Document code thoroughly with inline comments and meaningful variable names
5. Reuse existing packages rather than reimplementing
6. Automate workflows to minimize manual errors

### Fred Hutch Templates

- Python data analysis template (Jupyter notebooks)
- Python tool development template (package creation)
- Flask Python template (web applications)
- Shiny app template (interactive R applications)
- SCHARP templates (R-based data analysis)

### Example Repositories

- Data Science Example Code
- Slurm examples (job management)
- Nextflow examples (multiple analysis types)
- WILDS WDL Library (pre-written workflows)
- WILDS Docker Library (pre-built Docker images)

## Principles

- Never commit sensitive data, credentials, or PHI to any repository
- Use versioned environments for reproducibility
- Prefer public repositories to support open science
- Follow Fred Hutch data security policies
- Email SciComp for code structure guidance regarding security

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_managecode/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/software_examples/
- Fred Hutch GitHub Org: https://github.com/FredHutch
