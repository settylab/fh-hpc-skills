# Managing and Sharing Code at Fred Hutch

Source: https://sciwiki.fredhutch.org/scicomputing/software_managecode/

## Git and GitHub Basics

- **Git**: Free, open source version control software
- **GitHub**: Web-based hosting service for Git-managed projects

### Core Terminology

- **Repository**: Project folder with files and tracked history (local or remote)
- **Commit**: Documented change to file(s)
- **Branch**: Parallel version for testing without affecting main
- **Fork**: Copy of someone else's repository for modifications

## Getting Started at Fred Hutch

### Account Setup

1. Create a free GitHub account at github.com/join
2. Join the Fred Hutch GitHub Organization by emailing SciComp with your GitHub user ID

### Repository Types

- **Public**: Default, supports open science
- **Private**: Available through Fred Hutch GitHub Organization for sensitive work

## Interaction Methods

1. **GitHub Desktop Client** -- Recommended for beginners, free GUI at desktop.github.com
2. **Command Line Git** -- For advanced users and cluster work, download at git-scm.com
3. **GitHub Web Interface** -- Browser-based, supports wikis and project management
4. **Git Kraken** -- Advanced desktop client, free for academics (Mac, PC, Linux)
5. **RStudio Integration** -- Built-in version control support
6. **GitHub API** -- developer.github.com/v3

## Security Considerations (CRITICAL)

**Git does NOT provide HIPAA-compliant access controls, audit logging, or encryption.**

### Prohibited Content in Repos

- Protected health information (PHI)
- Database/storage credentials (usernames, passwords, tokens, access keys)
- Server names, IP addresses, network names
- API tokens, AWS credentials

### Security Best Practices

- Structure code to load secrets from external files or environment variables
- Never commit sensitive data to GitHub repositories
- Preprocess and sanitize sensitive data in secure backend systems
- Use Vault secrets management system for credentials
- Reference Security page and Computing Credentials page

**Contact:** Email SciComp for code structure guidance regarding security.

## Resources

- GitHub Glossary, GitHub Guides
- fredhutch.io software recommendations
- Fred Hutch GitHub Organization: github.com/fredhutch
