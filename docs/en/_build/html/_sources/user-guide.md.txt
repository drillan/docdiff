(user-guide)=
# User Guide

This guide provides practical instructions for using docdiff to manage multilingual documentation translations.

(user-guide-overview)=
## Overview

docdiff helps you track and manage translations of technical documentation by:
- Analyzing document structure rather than raw text
- Tracking translation coverage with detailed metrics
- Providing multiple export formats for translation workflows
- Generating reports for project management

(user-guide-getting-started)=
## Getting Started

(user-guide-installation)=
### Installation

Install docdiff using uv package manager:

```{code-block} bash
:name: user-code-installation
:caption: Installation Steps

# Clone the repository
git clone https://github.com/yourusername/docdiff.git
cd docdiff

# Install dependencies
uv sync

# Install docdiff
uv pip install -e .

# Verify installation
uv run docdiff --version
```

(user-guide-basic-workflow)=
## Basic Translation Workflow

The typical workflow for managing translations consists of four main steps:

```{code-block} text
:name: user-workflow-diagram
:caption: Translation Workflow

1. Compare → 2. Export → 3. Translate → 4. Import
     ↑                                         ↓
     └─────────────── 5. Verify ←─────────────┘
```

(user-guide-step1-compare)=
### Step 1: Compare Documents

First, analyze the current translation status:

```{code-block} bash
:name: user-code-compare
:caption: Compare Source and Target Documentation

# Basic comparison
uv run docdiff compare docs/en docs/ja

# With detailed view
uv run docdiff compare docs/en docs/ja --view metadata

# Generate markdown report
uv run docdiff compare docs/en docs/ja --output status.md
```

The comparison will show:
- Overall translation coverage percentage
- Number of translated, missing, and fuzzy-matched nodes
- Structure differences between source and target

(user-guide-step2-export)=
### Step 2: Export for Translation

Export missing translations to a format suitable for your translation workflow:

```{code-block} bash
:name: user-code-export
:caption: Export Translation Tasks

# Export to CSV (recommended for spreadsheet tools)
uv run docdiff export docs/en docs/ja --format csv --output tasks.csv

# Export to Excel with metadata
uv run docdiff export docs/en docs/ja --format xlsx --output tasks.xlsx

# Export to XLIFF for CAT tools
uv run docdiff export docs/en docs/ja --format xliff --output tasks.xlf
```

**CSV Format** is recommended for:
- Simple spreadsheet editing
- Version control (Git-friendly)
- Universal compatibility

**Excel Format** provides:
- Multiple sheets for organization
- Rich formatting options
- Comments and notes support

**XLIFF Format** is best for:
- Professional CAT tools
- Translation memory systems
- Industry-standard workflows

(user-guide-step3-translate)=
### Step 3: Translate Content

Open the exported file in your preferred tool:
- **CSV**: Excel, Google Sheets, LibreOffice Calc
- **XLSX**: Microsoft Excel
- **XLIFF**: SDL Trados, MemoQ, OmegaT

Translation tips:
- Preserve formatting markers (like `**bold**` in Markdown)
- Keep technical terms consistent
- Don't modify the ID, File, or Type columns
- Fill in the Target column with translations

(user-guide-step4-import)=
### Step 4: Import Translations

After translation, import the completed file:

```{code-block} bash
:name: user-code-import
:caption: Import Completed Translations

# Preview changes first (dry run)
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run

# If preview looks good, import for real
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja
```

The import process will:
- Validate translations against source structure
- Create or update target files
- Preserve document formatting
- Report any issues found

(user-guide-step5-verify)=
### Step 5: Verify Results

After import, verify the translation update:

```{code-block} bash
:name: user-code-verify
:caption: Verify Translation Updates

# Check new coverage
uv run docdiff compare docs/en docs/ja

# Generate detailed report
uv run docdiff compare docs/en docs/ja --output final-report.md
```

(user-guide-reports)=
## Understanding Reports

(user-guide-markdown-reports)=
### Markdown Reports

docdiff generates Markdown reports in three styles:

**Detailed Report** (default):
```bash
uv run docdiff compare docs/en docs/ja --output report.md
```
- Comprehensive coverage statistics
- Metadata-based grouping
- Side-by-side comparisons
- Missing translation details

**GitHub-Flavored Report**:
```bash
uv run docdiff compare docs/en docs/ja --output report.github.md
```
- Collapsible sections
- Mermaid diagrams
- Task lists for tracking
- Badges and alerts

**Compact Report**:
```bash
uv run docdiff compare docs/en docs/ja --output report.compact.md
```
- Minimal format
- Top missing items only
- Quick status overview

(user-guide-terminal-views)=
### Terminal View Modes

Different views help you understand translation status:

```{code-block} bash
:name: user-code-views
:caption: Terminal View Options

# Summary view (default)
uv run docdiff compare docs/en docs/ja --view summary

# Tree view - hierarchical structure
uv run docdiff compare docs/en docs/ja --view tree

# Metadata view - grouped by labels/names
uv run docdiff compare docs/en docs/ja --view metadata

# Side-by-side - parallel comparison
uv run docdiff compare docs/en docs/ja --view side-by-side

# Statistics - detailed metrics
uv run docdiff compare docs/en docs/ja --view stats
```

(user-guide-team-workflow)=
## Team Translation Workflow

For teams working on translations:

(user-guide-team-setup)=
### Initial Setup

1. **Project Manager**: Export all translation tasks
```bash
uv run docdiff export docs/en docs/ja \
  --format xlsx \
  --output team-tasks-week1.xlsx
```

2. **Assign** sections to different translators using Excel sheets

3. **Share** via cloud storage or version control

(user-guide-team-process)=
### Translation Process

1. **Translators** work on assigned sections
2. **Save** progress regularly
3. **Mark** completed items in a Status column

(user-guide-team-integration)=
### Integration Process

1. **Collect** completed files from translators

2. **Import** each file sequentially:
```bash
# Import translator A's work
uv run docdiff import translator-a.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# Import translator B's work  
uv run docdiff import translator-b.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja
```

3. **Generate** progress report:
```bash
uv run docdiff compare docs/en docs/ja \
  --output weekly-progress.github.md
```

(user-guide-continuous-updates)=
## Managing Continuous Updates

When source documentation changes:

1. **Detect Changes**:
```bash
# Compare current status
uv run docdiff compare docs/en docs/ja --view summary
```

2. **Export Only New/Changed Content**:
```bash
# Export missing translations
uv run docdiff export docs/en docs/ja \
  --format csv \
  --output updates-$(date +%Y%m%d).csv
```

3. **Track Progress** with Git:
```bash
# Commit translation updates
git add docs/ja/
git commit -m "docs: update Japanese translations"

# Track reports
git add *.md
git commit -m "docs: add translation status report"
```

(user-guide-tips)=
## Tips and Best Practices

(user-guide-tips-performance)=
### Performance Optimization

- Use `.docdiff/` cache to avoid re-parsing
- Run compare before export to check status
- Process large projects in sections if needed

(user-guide-tips-quality)=
### Translation Quality

- Maintain consistent terminology
- Preserve code blocks exactly
- Keep cross-references intact
- Review fuzzy matches carefully

(user-guide-tips-organization)=
### Project Organization

```{code-block} text
:name: user-project-structure
:caption: Recommended Project Structure

project/
├── docs/
│   ├── en/          # Source documentation
│   ├── ja/          # Japanese translation
│   ├── zh/          # Chinese translation
│   └── ko/          # Korean translation
├── translations/    # Translation work files
│   ├── exports/     # Exported task files
│   ├── completed/   # Completed translations
│   └── reports/     # Status reports
└── .docdiff/        # Cache (gitignored)
```

(user-guide-troubleshooting)=
## Troubleshooting

(user-guide-common-issues)=
### Common Issues

**Issue**: Import fails with "structure mismatch"
- **Solution**: Ensure source directory matches the one used for export

**Issue**: Low fuzzy match accuracy
- **Solution**: Check if content has minor formatting differences

**Issue**: Missing translations not detected
- **Solution**: Verify target files exist in the correct location

**Issue**: Cache seems outdated
- **Solution**: Delete `.docdiff/cache/` and re-run comparison

(user-guide-getting-help)=
### Getting Help

- Check the {doc}`cli-reference` for command details
- Review the {doc}`api-reference` for programmatic usage
- Report issues on [GitHub Issues](https://github.com/yourusername/docdiff/issues)
- Join discussions on [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)