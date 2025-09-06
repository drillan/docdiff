(cli-reference)=
# CLI Reference

The docdiff command-line interface provides tools for analyzing and managing document translations.

(cli-installation)=
## Installation

Install docdiff using uv:

```{code-block} bash
:name: cli-code-installation
:caption: Installation Commands
:linenos:

uv sync
uv pip install -e .
```

(cli-available-commands)=
## Available Commands

(cli-command-compare)=
### `docdiff compare`

Advanced document comparison with translation coverage analysis.

```{code-block} bash
:name: cli-code-compare-usage
:caption: Compare Command Usage

docdiff compare <source-dir> <target-dir> [OPTIONS]
```

**Arguments:**
- `source-dir`: Source documentation directory (e.g., docs/en)
- `target-dir`: Target documentation directory (e.g., docs/ja)

**Options:**
- `--source-lang, -s`: Source language code (default: en)
- `--target-lang, -t`: Target language code (default: ja)
- `--output, -o`: Output path for report (supports .json, .md extensions)
- `--html`: Generate HTML report in .docdiff/reports/
- `--view`: Display view mode:
  - `summary`: Coverage statistics overview (default)
  - `tree`: Hierarchical tree view of documents
  - `metadata`: Group by metadata (labels, names)
  - `side-by-side`: Side-by-side content comparison
  - `stats`: Detailed statistics view
- `--verbose, -v`: Show detailed output

**Example:**
```{code-block} bash
:name: cli-code-compare-examples
:caption: Compare Command Examples
:linenos:

# Basic comparison with summary view
docdiff compare docs/en docs/ja

# Generate Markdown report (style auto-detected from filename)
docdiff compare docs/en docs/ja --output report.md          # detailed style
docdiff compare docs/en docs/ja --output report.github.md   # GitHub style
docdiff compare docs/en docs/ja --output report.compact.md  # compact style

# View metadata-based grouping
docdiff compare docs/en docs/ja --view metadata

# Generate HTML report
docdiff compare docs/en docs/ja --html
```

**Output Formats:**

**Markdown Report Styles:**
- **Detailed** (default): Comprehensive report with all sections
- **GitHub**: GitHub-flavored markdown with collapsible sections and mermaid diagrams
- **Compact**: Minimal report focusing on missing translations

**Terminal View Modes:**
- **Summary**: Overall coverage statistics and structure differences
- **Tree**: Document hierarchy with translation status indicators
- **Metadata**: Grouped by labels and name attributes with coverage bars
- **Side-by-side**: Source and target content comparison table
- **Stats**: Detailed statistics with type distribution

(cli-command-parse)=
### `docdiff parse`

Parse documentation and extract structure for analysis.

```{code-block} bash
:name: cli-code-parse-usage
:caption: Parse Command Usage

docdiff parse <project-dir> [OPTIONS]
```

**Arguments:**
- `project-dir`: Path to the documentation directory

**Options:**
- `--cache-dir`: Override default cache directory (default: .docdiff/cache)
- `--verbose, -v`: Show detailed parsing information

**Example:**
```{code-block} bash
:name: cli-code-parse-examples
:caption: Parse Command Examples
:linenos:

# Parse documentation
docdiff parse docs/en

# Parse with verbose output
docdiff parse docs/ja --verbose
```

(cli-command-status)=
### `docdiff status`

Show translation status summary.

```{code-block} bash
:name: cli-code-status-usage
:caption: Status Command Usage

docdiff status <source-dir> <target-dir> [OPTIONS]
```

**Arguments:**
- `source-dir`: Source documentation directory
- `target-dir`: Target documentation directory

**Options:**
- `--source-lang, -s`: Source language code (default: en)
- `--target-lang, -t`: Target language code (default: ja)
- `--format`: Output format (`summary`, `detailed`)

**Example:**
```{code-block} bash
:name: cli-code-status-examples
:caption: Status Command Examples
:linenos:

# Quick status check
docdiff status docs/en docs/ja

# Detailed status
docdiff status docs/en docs/ja --format detailed
```

(cli-command-export)=
### `docdiff export`

Export translation tasks to various formats.

```{code-block} bash
:name: cli-code-export-usage
:caption: Export Command Usage

docdiff export <source-dir> <target-dir> [OPTIONS]
```

**Arguments:**
- `source-dir`: Source documentation directory
- `target-dir`: Target documentation directory

**Options:**
- `--format, -f`: Export format:
  - `json`: JSON format (default)
  - `csv`: CSV spreadsheet format
  - `xlsx`: Excel workbook format
  - `xliff`: XLIFF 2.1 translation format
- `--output, -o`: Output file path (required)
- `--source-lang, -s`: Source language code (default: en)
- `--target-lang, -t`: Target language code (default: ja)
- `--include-translated`: Include already translated content
- `--metadata-only`: Export only metadata without content

**Example:**
```{code-block} bash
:name: cli-code-export-examples
:caption: Export Command Examples
:linenos:

# Export to CSV for spreadsheet translation
docdiff export docs/en docs/ja --format csv --output tasks.csv

# Export to XLIFF for CAT tools
docdiff export docs/en docs/ja --format xliff --output translation.xlf

# Export to Excel with multiple sheets
docdiff export docs/en docs/ja --format xlsx --output tasks.xlsx

# Include already translated content for review
docdiff export docs/en docs/ja --format json --output all.json --include-translated
```

**Output Formats:**

**CSV Format:**
```{code-block} text
:name: cli-code-export-csv-format
:caption: CSV Export Format

ID,File,Line,Type,Status,Similarity,Source,Target,Label,Name,Notes
7f3a2b,index.md,7,paragraph,missing,0.0,"docdiff is a powerful...",,,,,
8c4d5e,index.md,11,list,fuzzy,100.0,"- **Intelligent Structure...","- **Intelligent Structure...",,,
```

**XLIFF Format:**
```{code-block} xml
:name: cli-code-export-xliff-format
:caption: XLIFF 2.1 Export Format

<?xml version="1.0" encoding="UTF-8"?>
<xliff version="2.1" srcLang="en" trgLang="ja">
  <file id="index.md">
    <unit id="7f3a2b">
      <segment>
        <source>docdiff is a powerful multilingual...</source>
        <target state="initial"></target>
      </segment>
    </unit>
  </file>
</xliff>
```

(cli-command-import)=
### `docdiff import`

Import translations from exported files.

```{code-block} bash
:name: cli-code-import-usage
:caption: Import Command Usage

docdiff import <input-file> [OPTIONS]
```

**Arguments:**
- `input-file`: Path to the file containing translations (CSV, JSON, XLSX, or XLIFF)

**Options:**
- `--source-dir`: Source documentation directory (for validation)
- `--target-dir`: Target documentation directory (where to write translations)
- `--source-lang, -s`: Source language code (default: en)
- `--target-lang, -t`: Target language code (default: ja)
- `--dry-run`: Preview changes without writing files
- `--verbose, -v`: Show detailed import progress

**Example:**
```{code-block} bash
:name: cli-code-import-examples
:caption: Import Command Examples
:linenos:

# Import translations from CSV
docdiff import translated.csv --source-dir docs/en --target-dir docs/ja

# Dry run to preview changes
docdiff import translated.xlsx --source-dir docs/en --target-dir docs/ja --dry-run

# Import from XLIFF with verbose output
docdiff import translation.xlf --target-dir docs/ja --verbose
```

(cli-command-simple-compare)=
### `docdiff simple-compare`

Basic structure comparison between directories.

```{code-block} bash
:name: cli-code-simple-compare-usage
:caption: Simple Compare Command Usage

docdiff simple-compare <source-dir> <target-dir> [OPTIONS]
```

**Arguments:**
- `source-dir`: Source documentation directory
- `target-dir`: Target documentation directory

**Options:**
- `--verbose, -v`: Show detailed comparison

**Example:**
```{code-block} bash
:name: cli-code-simple-compare-examples
:caption: Simple Compare Command Examples
:linenos:

# Quick structure comparison
docdiff simple-compare docs/en docs/ja

# Detailed comparison
docdiff simple-compare docs/en docs/ja --verbose
```

(cli-configuration)=
## Configuration

docdiff uses a `.docdiff/` directory in your project root for cache and reports:

```{code-block} text
:name: cli-code-cache-structure
:caption: Cache Directory Structure

.docdiff/
├── cache/           # Parsed document cache
│   ├── nodes.db     # Document structure database
│   └── mappings.db  # Translation mappings
└── reports/         # Generated reports
    ├── comparison_en_ja.html
    └── *.md         # Markdown reports
```

**Note:** Add `.docdiff/` to your `.gitignore` file to exclude cache from version control.

(cli-environment-variables)=
## Environment Variables

- `DOCDIFF_DB_PATH`: Override default database location
- `DOCDIFF_CONFIG`: Path to configuration file
- `DOCDIFF_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

(cli-common-workflows)=
## Common Workflows

(cli-workflow-initial-setup)=
### Initial Translation Setup

```{code-block} bash
:name: cli-code-workflow-initial
:caption: Initial Translation Setup
:linenos:

# 1. Compare source and target documentation
docdiff compare docs/en docs/ja

# 2. Generate detailed report for review
docdiff compare docs/en docs/ja --output initial-status.md

# 3. Export missing translations to CSV
docdiff export docs/en docs/ja --format csv --output translations-needed.csv

# 4. After translation, import the completed CSV
docdiff import translations-completed.csv --source-dir docs/en --target-dir docs/ja
```

(cli-workflow-continuous)=
### Continuous Translation Management

```{code-block} bash
:name: cli-code-workflow-continuous
:caption: Continuous Translation Workflow
:linenos:

# Daily workflow
# 1. Check current translation coverage
docdiff compare docs/en docs/ja --view summary

# 2. Generate GitHub-style report for PR
docdiff compare docs/en docs/ja --output report.github.md

# 3. Export only missing translations
docdiff export docs/en docs/ja --format xlsx --output weekly-tasks.xlsx

# 4. View metadata-based grouping for prioritization
docdiff compare docs/en docs/ja --view metadata
```

(cli-workflow-team)=
### Team Translation Workflow

```{code-block} bash
:name: cli-code-workflow-team
:caption: Team Translation Workflow
:linenos:

# Project manager: Export tasks
docdiff export docs/en docs/ja --format xlsx --output team-tasks.xlsx

# Translator: Work on Excel file
# ... translation work ...

# Project manager: Import completed translations
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run  # Preview first

# If preview looks good, import for real
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# Generate report for stakeholders
docdiff compare docs/en docs/ja --output status-report.md
```

(cli-exit-codes)=
## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Parse error
- `3`: Database error
- `4`: Validation error
- `5`: Configuration error

(cli-tips-best-practices)=
## Tips and Best Practices

1. **Regular Parsing**: Re-parse your documentation regularly to detect structural changes
2. **Version Control**: Include `.docdiff.yml` in version control, exclude `.docdiff/` directory
3. **Incremental Updates**: Use `--filter outdated` to focus on changed content
4. **Validation**: Run validation before major releases to ensure reference integrity
5. **Batch Operations**: Process multiple target languages in configuration rather than individual commands