# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A minimalist personal portfolio/resume website. Plain static HTML with no build tools, frameworks, or dependencies.

## Structure

```
index.html          # Homepage (single page with embedded CSS)
resume.pdf          # Resume PDF linked from nav
projects.html       # Planned (not yet created)
photography.html    # Planned (not yet created)
```

## Development

Serve locally with any static file server, e.g.:

```bash
python3 -m http.server
```

No build step, no package manager, no linting tools.

## Design Conventions

- **Font**: `courier new, monospace`
- **Background**: `#f7f7f2` (cream), **Text**: `#222725` (near-black)
- **Accent/links**: `#899878` (sage green) with white text, pill-shaped (`border-radius: 4px`)
- **Layout**: centered, `max-width: 600px`, `margin: 2em auto`
- All CSS is embedded in `<style>` tags within each HTML file — no external stylesheets
