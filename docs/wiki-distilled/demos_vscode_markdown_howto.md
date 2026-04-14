# VS Code Markdown Editing

Source: https://sciwiki.fredhutch.org/compdemos/vscode_markdown_howto/

## Features

- **Live Preview**: Split-window magnifying glass icon for rendered Markdown alongside source
- **Git Integration**: Built-in staging, commits, and remote management

## Recommended Plugins

### Paste Image (mushan)
```json
{
    "pasteImage.path": "${projectRoot}/assets/${currentFileNameWithoutExt}/",
    "pasteImage.basePath": "${projectRoot}/assets",
    "pasteImage.forceUnixStyleSeparator": true,
    "pasteImage.prefix": "/assets/"
}
```
Shortcuts: Ctrl+Alt+V (Windows/Linux), Command+Alt+V (macOS). Linux requires `sudo apt install xclip`.

### Code Spell Checker (Street Side Software)
Real-time spell checking with suggestions via yellow lightbulb context menu.

### MarkdownLint (David Anson)
Formatting compliance testing with hover-to-reveal warnings.

## Setup

Open the folder (File > Open Folder) for plugin features to work correctly.
