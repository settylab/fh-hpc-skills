# Shiny Applications at Fred Hutch

Source: https://sciwiki.fredhutch.org/compdemos/shiny/

## Deployment Options

### Shinyapps.io
- Free plan: 25 hours/month, limited to 5 apps
- Paid plans offer password protection and custom domains
- Integrates directly with RStudio

### SciComp Pipeline (Recommended)
- Supports containerized applications in multiple languages
- Integrates with campus databases without internet exposure
- CI/CD-based updates via GitHub
- Custom fredhutch.org domain URLs
- Free service with optional authorization and firewall settings

## Local Testing

Navigate to app's `app` subfolder, launch R, run `source('start.r')`. Access at `http://localhost:7777`.

## GitHub Setup

### From Template
```bash
git clone https://github.com/FredHutch/shiny-app-template.git <your_app_folder>
cd <your_app_folder>
rm -rf .git
git init
echo "# <your_app_folder>" > README.md
git add .
git commit -m 'initial commit'
```

## App File Requirements

- Place `app.R` or `ui.R`/`server.R` in the `app` directory
- Include `library(shiny)` in both `ui.R` and `server.R`
- Remove `shinyApp(ui, server)` from `server.R`
- Store all dependencies and data files in `app` or its subdirectories

## Deployment Request

Submit at `https://getshiny.fredhutch.org` (campus access required) with:
1. GitHub repository (Fred Hutch organization)
2. Desired DNS name (.fredhutch.org domain)
3. Internal or external facing
4. Authorization requirements
5. PHI removal confirmation
6. Complete R package dependency list
