# Git Tips and Tricks

Source: https://sciwiki.fredhutch.org/compdemos/git_tips/

## Changing Default Branch (master to main)

```bash
git pull
git push
git branch -m master main
git push -u origin main
git push -u origin :master  # delete old remote branch
```

Warning: Understand impacts on CI/CD, automation, and Wiki pages before renaming.

Contributors must update:
```bash
git pull
git checkout main
git merge master
git branch -d master
```

GitHub Pages sites cannot change from "master" unless building from 'gh-pages'.

## Rebasing

Adding a collection of commits to another branch, commonly used before merging PRs to resolve conflicts from parallel development.

## Git Interface Options

- **GitHub Desktop**: GUI without CLI requirements
- **GitHub.com**: Browser-based editing and PRs
- **GitKraken**: Feature-rich GUI for complex workflows
- **IDEs**: RStudio, VS Code, PyCharm, JupyterLab have integrated Git

## Forking vs Branching

- **Fork**: Independent copies, flavored versions, contributing to repos that restrict branching
- **Branch**: When repo permissions allow and collaborative editing is the focus
