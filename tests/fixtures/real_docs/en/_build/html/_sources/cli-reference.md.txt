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

(cli-command-parse)=
### `docdiff parse`

Parse a Sphinx documentation project and extract its structure.

```{code-block} bash
:name: cli-code-parse-usage
:caption: Parse Command Usage

docdiff parse <project-dir>
```

**Arguments:**
- `project-dir`: Path to the Sphinx project directory

**Options:**
- `--config`: Path to custom configuration file
- `--output`: Output database location (default: `.docdiff/structure.db`)
- `--force`: Overwrite existing database

**Example:**
```{code-block} bash
:name: cli-code-parse-examples
:caption: Parse Command Examples
:linenos:

docdiff parse docs/
docdiff parse /path/to/sphinx/project --output my-db.sqlite
```

**Output:**
- Creates SQLite database with parsed document structure
- Reports number of files processed and nodes extracted
- Shows parsing errors if any

(cli-command-status)=
### `docdiff status`

Check translation status for a project.

```{code-block} bash
:name: cli-code-status-usage
:caption: Status Command Usage

docdiff status <project-dir>
```

**Arguments:**
- `project-dir`: Path to the Sphinx project directory

**Options:**
- `--source-lang`: Source language code (default: from config)
- `--target-lang`: Target language code
- `--format`: Output format (`table`, `json`, `csv`)
- `--filter`: Filter by status (`pending`, `translated`, `reviewed`, `outdated`)

**Example:**
```{code-block} bash
:name: cli-code-status-examples
:caption: Status Command Examples
:linenos:

docdiff status docs/ --target-lang ja
docdiff status docs/ --filter pending --format json
```

**Output:**
```{code-block} text
:name: cli-code-status-output
:caption: Status Command Output Example

Translation Status Report
========================
Source Language: en
Target Language: ja

Summary:
- Total nodes: 245
- Translated: 120 (49%)
- Pending: 100 (41%)
- Outdated: 25 (10%)

Files with pending translations:
- docs/api/index.md (15 nodes)
- docs/guide/installation.md (8 nodes)
```

(cli-command-export)=
### `docdiff export`

Export parsed structure and translation units.

```{code-block} bash
:name: cli-code-export-usage
:caption: Export Command Usage

docdiff export <project-dir>
```

**Arguments:**
- `project-dir`: Path to the Sphinx project directory

**Options:**
- `--format`: Export format (`json`, `csv`, `xlsx`)
- `--output`: Output file path
- `--include-translated`: Include already translated content
- `--lang-pair`: Language pair to export (e.g., `en-ja`)

**Example:**
```{code-block} bash
:name: cli-code-export-examples
:caption: Export Command Examples
:linenos:

docdiff export docs/ --format json --output structure.json
docdiff export docs/ --format csv --lang-pair en-ja
```

**Output Formats:**

**JSON Format:**
```{code-block} json
:name: cli-code-export-json-format
:caption: JSON Export Format

{
  "project": "docs/",
  "timestamp": "2025-01-06T10:00:00",
  "nodes": [
    {
      "id": "abc123",
      "type": "section",
      "content": "Installation Guide",
      "file_path": "docs/guide/installation.md",
      "translations": {
        "ja": {
          "status": "pending",
          "content": null
        }
      }
    }
  ]
}
```

**CSV Format:**
```{code-block} text
:name: cli-code-export-csv-format
:caption: CSV Export Format

node_id,type,file_path,source_content,target_lang,translated_content,status
abc123,section,docs/guide/installation.md,"Installation Guide",ja,,pending
```

(cli-command-validate)=
### `docdiff validate`

Validate document structure and references.

```{code-block} bash
:name: cli-code-validate-usage
:caption: Validate Command Usage

docdiff validate <project-dir>
```

**Arguments:**
- `project-dir`: Path to the Sphinx project directory

**Options:**
- `--check-refs`: Validate cross-references
- `--check-structure`: Validate document structure
- `--fix`: Attempt to fix issues automatically

**Example:**
```{code-block} bash
:name: cli-code-validate-examples
:caption: Validate Command Examples
:linenos:

docdiff validate docs/
docdiff validate docs/ --check-refs --fix
```

**Output:**
```{code-block} text
:name: cli-code-validate-output
:caption: Validation Report Example

Validation Report
=================

Structure Issues:
✓ All documents have valid structure

Reference Issues:
⚠ 3 unresolved references found:
  - docs/api/index.md:45 -> ref:nonexistent-label
  - docs/guide/setup.md:12 -> doc:missing-file
  
✓ 142 references resolved successfully
```

(cli-configuration)=
## Configuration

docdiff can be configured using a `.docdiff.yml` file in the project root:

```{code-block} yaml
:name: cli-code-configuration
:caption: Configuration File Example

# .docdiff.yml
source_language: en
target_languages:
  - ja
  - zh
  - ko

database:
  path: .docdiff/structure.db
  
parsing:
  ignore_patterns:
    - "_build/**"
    - "**/.git/**"
  
translation:
  chunk_size: 1000  # Max characters per translation unit
  preserve_formatting: true
```

(cli-environment-variables)=
## Environment Variables

- `DOCDIFF_DB_PATH`: Override default database location
- `DOCDIFF_CONFIG`: Path to configuration file
- `DOCDIFF_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

(cli-common-workflows)=
## Common Workflows

(cli-workflow-initial-setup)=
### Initial Project Setup

```{code-block} bash
:name: cli-code-workflow-initial
:caption: Initial Project Setup
:linenos:

# Parse the project structure
docdiff parse docs/

# Check initial status
docdiff status docs/ --target-lang ja

# Export for translation
docdiff export docs/ --format json --output for-translation.json
```

(cli-workflow-updating)=
### Updating Translations

```{code-block} bash
:name: cli-code-workflow-updating
:caption: Updating Translations Workflow
:linenos:

# Re-parse to detect changes
docdiff parse docs/ --force

# Check for outdated translations
docdiff status docs/ --filter outdated

# Export only changed content
docdiff export docs/ --filter outdated --output updates.json
```

(cli-workflow-validation)=
### Validation and Quality Check

```{code-block} bash
:name: cli-code-workflow-validation
:caption: Validation Workflow
:linenos:

# Validate structure and references
docdiff validate docs/

# Check translation completeness
docdiff status docs/ --target-lang ja --format json | jq '.summary'
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