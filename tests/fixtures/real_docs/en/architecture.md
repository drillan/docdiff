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

The system follows a layered architecture pattern:

```{code-block} text
:name: architecture-diagram-layers
:caption: Layered Architecture Diagram

┌─────────────────────────────────────────────────┐
│                  CLI Layer (Typer)              │
├─────────────────────────────────────────────────┤
│                 Core Components                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │DocumentParser│  │StructureDB   │           │
│  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ReferenceTracker│ │TranslationState│        │
│  └──────────────┘  └──────────────┘           │
├─────────────────────────────────────────────────┤
│                Parser Layer                      │
│  ┌──────────────┐  ┌──────────────┐           │
│  │MySTParser    │  │ReSTParser    │           │
│  └──────────────┘  └──────────────┘           │
├─────────────────────────────────────────────────┤
│                Storage Layer                     │
│  ┌──────────────────────────────────┐          │
│  │         SQLite Database          │          │
│  └──────────────────────────────────┘          │
└─────────────────────────────────────────────────┘
```

(architecture-core-components)=
## Core Components

(architecture-document-node)=
### DocumentNode
The basic unit of document structure, implemented as a Pydantic model. Represents individual elements like sections, paragraphs, code blocks, etc.

(architecture-document-parser)=
### DocumentParser
Abstract base class for all parsers. Defines the interface for document parsing operations.

(architecture-myst-parser)=
### MySTParser
Parser implementation for MyST (Markedly Structured Text) format. Handles MyST-specific syntax and directives.

(architecture-rest-parser)=
### ReSTParser
Parser implementation for reStructuredText format. Processes standard Sphinx documentation format.

(architecture-structure-db)=
### StructureDB
Manages SQLite database operations for storing and querying parsed document structures. Provides persistence and efficient retrieval of document elements.

(architecture-reference-tracker)=
### ReferenceTracker
Tracks and manages cross-references within and between documents. Essential for maintaining documentation integrity.

(architecture-translation-state)=
### TranslationState
Manages the translation status of each document element, tracking changes and maintaining version history.

(architecture-project-analyzer)=
### ProjectAnalyzer
Analyzes entire Sphinx projects, understanding project structure, configuration, and toctree relationships.

(architecture-cli)=
### CLI
Command-line interface built with Typer, providing user-friendly commands for all operations.

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
* - docutils/myst-parser
  - Sphinx standard parsers for AST generation
* - Rich
  - Beautiful CLI output and progress indicators
* - pytest
  - Comprehensive testing framework
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