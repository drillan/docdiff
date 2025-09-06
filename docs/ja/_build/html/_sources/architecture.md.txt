(architecture)=
# Architecture

(architecture-overview)=
## Overview

docdiff is a multilingual translation management tool for MyST/reStructuredText documents. It analyzes documents by structural units and tracks translation states to support internationalization of technical documentation.

(architecture-core-design)=
## Core Design Philosophy

The system adopts the following design principles:

- **Layered Architecture**: Clear separation of concerns between layers
- **Structural Unit Separation**: Documents are separated by logical structural units (sections, code blocks, figures, tables, etc.)
- **No Mechanical Character-based Splitting**: Preserves document context and meaning
- **Translation State Management**: Tracks status for each structural element (pending/translated/reviewed/outdated)

(architecture-system)=
## System Architecture

The system follows a modular architecture with specialized components for each aspect of translation management:

```{code-block} text
:name: architecture-diagram-layers
:caption: System Architecture Diagram

┌───────────────────────────────────────────────────┐
│                   CLI Layer (Typer)               │
│     Commands: compare, export, import, parse      │
├───────────────────────────────────────────────────┤
│              Comparison & Analysis Layer           │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │ComparisonEngine │  │ MetadataView   │          │
│  └─────────────────┘  └────────────────┘          │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │MarkdownReporter │  │ NodeMapping    │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│               Translation Workflow Layer           │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │   Exporter     │  │   Importer     │          │
│  │ (JSON/CSV/     │  │ (Multi-format  │          │
│  │  XLSX/XLIFF)   │  │   support)     │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│                  Parser Layer                      │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │  MySTParser    │  │ DocumentNode   │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│              Cache Management Layer                │
│  ┌──────────────────────────────────────────┐     │
│  │         CacheManager (.docdiff/)         │     │
│  │    - cache/: SQLite databases            │     │
│  │    - reports/: Generated reports         │     │
│  └──────────────────────────────────────────┘     │
└───────────────────────────────────────────────────┘
```

(architecture-core-components)=
## Core Components

(architecture-document-node)=
### DocumentNode
The basic unit of document structure, implemented as a Pydantic model. Represents individual elements like sections, paragraphs, code blocks, etc. with full metadata preservation including labels, names, and captions.

(architecture-myst-parser)=
### MySTParser
Advanced parser for MyST (Markedly Structured Text) and standard Markdown formats. Extracts document structure while preserving all metadata attributes and cross-references.

(architecture-comparison-engine)=
### ComparisonEngine
Sophisticated multi-pass comparison system that:
- **Exact Matching**: First pass matches nodes by label and name attributes
- **Fuzzy Matching**: Second pass uses content similarity for approximate matches
- **Missing Detection**: Identifies untranslated content
- **Performance**: Processes 14,000+ nodes per second

(architecture-metadata-view)=
### MetadataView
Rich terminal visualization component providing multiple display modes:
- **Tree View**: Hierarchical document structure with status indicators
- **Metadata Groups**: Coverage statistics grouped by labels and names
- **Side-by-Side**: Parallel source/target content comparison
- **Statistics**: Detailed type distribution and coverage metrics

(architecture-markdown-reporter)=
### MarkdownReporter
Generates Git-friendly Markdown reports with three styles:
- **Detailed**: Comprehensive report with all sections and visualizations
- **GitHub**: Collapsible sections, mermaid diagrams, and task lists
- **Compact**: Minimal format focusing on critical missing translations

(architecture-exporter)=
### Exporter
Multi-format export system supporting:
- **JSON**: Complete structural data with metadata
- **CSV**: Universal spreadsheet format for easy editing
- **XLSX**: Excel workbooks with multiple sheets
- **XLIFF 2.1**: Industry-standard CAT tool format

(architecture-importer)=
### Importer
Intelligent import system that:
- Validates translations against source structure
- Preserves document formatting and metadata
- Supports dry-run mode for preview
- Handles all export formats seamlessly

(architecture-cache-manager)=
### CacheManager
Centralized cache management system:
- **Location**: Project-root `.docdiff/` directory
- **Structure**: Organized cache/ and reports/ subdirectories
- **Persistence**: SQLite databases for parsed structures
- **Performance**: Eliminates redundant parsing operations

(architecture-cli)=
### CLI
Command-line interface built with Typer, providing intuitive commands:
- `compare`: Advanced comparison with multiple view modes
- `export`: Multi-format translation task export
- `import`: Translation import with validation
- `parse`: Document structure extraction
- `status`: Quick coverage summary

(architecture-key-features)=
## Key Features

(architecture-structure-analysis)=
### Document Structure Analysis
- **Section Identification**: Recognizes heading levels, titles, and labels
- **Attribute Extraction**: Preserves `:name:` and `:caption:` attributes
- **Cross-reference Tracking**: Maintains JupyterBook/Sphinx reference system
- **Logical Separation**: Separates by structural units (code blocks, tables, figures)
- **Context Preservation**: No mechanical character-count based splitting

(architecture-translation-management)=
### Translation Management
- **State Tracking**: Monitors translation status for each structural element
- **Change Detection**: Hash-based content change detection
- **Incremental Updates**: Supports efficient updates of changed content only
- **Version History**: Maintains translation history and timestamps

(architecture-sphinx-support)=
### Sphinx Project Support
- **Configuration Reading**: Automatic `conf.py` configuration loading
- **Batch Analysis**: Processes entire projects in one operation
- **Toctree Understanding**: Comprehends document hierarchy and relationships

(architecture-database-design)=
## Database Design

The system uses SQLite for data persistence with the following main tables:

(architecture-nodes-table)=
### Nodes Table
Stores document structural elements with full metadata including type, content, hierarchy, and references.

(architecture-references-table)=
### References Table
Maintains relationships between document elements for cross-reference resolution.

(architecture-translation-units-table)=
### Translation Units Table
Tracks translation status and content for each document element across language pairs.

The database includes strategic indexing on labels, names, parent IDs, file paths, and status fields for optimal query performance.

(architecture-technology-stack)=
## Technology Stack

```{list-table} Technology Stack
:name: architecture-table-tech-stack
:header-rows: 1
:widths: 30 70

* - Technology
  - Purpose
* - Python 3.12+
  - Modern type hints, improved performance
* - Pydantic
  - Data validation, serialization, type safety
* - Typer
  - Type-hint based CLI with automatic help generation
* - SQLite
  - Lightweight, embedded database with transaction support
* - myst-parser
  - Advanced MyST/Markdown parsing with metadata extraction
* - Rich
  - Beautiful terminal output, tables, and progress indicators
* - difflib
  - Fuzzy string matching for content comparison
* - csv/openpyxl/lxml
  - Multi-format export/import support
* - pytest
  - Comprehensive testing framework with fixtures
* - ruff
  - Fast Python linter and formatter
* - mypy
  - Static type checking for code quality
```

(architecture-future-extensibility)=
## Future Extensibility

The architecture is designed with the following extension points:

- **JupyterBook JSON Format Support**: For modern documentation workflows
- **Translation API Integration**: OpenAI, Claude, and other AI translation services
- **Web UI**: Browser-based interface for non-technical users
- **Multi-language Pair Support**: Simultaneous translation to multiple languages
- **Plugin System**: Custom processors and integrations

(architecture-design-considerations)=
## Design Considerations

(architecture-interface-separation)=
### Interface Separation
Components communicate through well-defined interfaces, ensuring loose coupling and maintainability.

(architecture-flexible-data-models)=
### Flexible Data Models
Pydantic models allow for easy extension and validation of data structures.

(architecture-data-persistence)=
### Data Persistence
SQLite provides reliable storage with ACID compliance while remaining lightweight.

(architecture-extensibility-abstraction)=
### Extensibility Through Abstraction
Abstract base classes allow for new parser implementations and processing strategies.