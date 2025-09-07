(api-documentation)=

# API Documentation

Complete API reference for all modules, classes, and functions.

```{toctree}
:caption: API Modules
:maxdepth: 2

reference
```

(api-overview)=

## Overview

The DocDiff API is organized into several core modules:

```{eval-rst}
.. list-table:: Core Modules
   :widths: 25 75
   :header-rows: 1

   * - Module
     - Description
   * - ``docdiff.parsers``
     - Document parsing functionality
   * - ``docdiff.analyzers``
     - Content analysis tools
   * - ``docdiff.reporters``
     - Report generation utilities
   * - ``docdiff.models``
     - Data models and structures
   * - ``docdiff.utils``
     - Helper functions and utilities
```

(api-quick-start)=

## Quick Start

Basic usage example:

```{code-block} python
:linenos: true

from docdiff import parse, analyze, report

# Parse documents
source_nodes = parse('source.rst')
target_nodes = parse('target.rst')

# Analyze differences
diff_result = analyze(source_nodes, target_nodes)

# Generate report
report_text = report(diff_result, format='markdown')
print(report_text)
```

(api-core-classes)=

## Core Classes

(api-parser-classes)=

### Parser Classes

```{eval-rst}
.. class:: BaseParser

   Abstract base class for all parsers.

   .. method:: parse(content: str) -> List[DocumentNode]

      Parse document content and return nodes.

      :param content: Document content as string
      :returns: List of document nodes
      :raises ParseError: If parsing fails
```

```{eval-rst}
.. class:: ReSTParser(BaseParser)

   Parser for reStructuredText documents.

   .. attribute:: strict_mode
      :type: bool

      Enable strict parsing mode (default: False)

   .. method:: configure(**options)

      Configure parser options.
```

```{eval-rst}
.. class:: MarkdownParser(BaseParser)

   Parser for Markdown documents.

   .. attribute:: flavor
      :type: str

      Markdown flavor ('github', 'commonmark', 'extra')
```

(api-model-classes)=

### Model Classes

```{eval-rst}
.. class:: DocumentNode

   Represents a document structure element.

   .. attribute:: type
      :type: NodeType

      Type of the node (section, paragraph, code_block, etc.)

   .. attribute:: content
      :type: str

      Text content of the node

   .. attribute:: metadata
      :type: dict

      Additional metadata (language, caption, etc.)

   .. attribute:: children
      :type: List[DocumentNode]

      Child nodes

   .. method:: traverse() -> Iterator[DocumentNode]

      Recursively traverse all nodes.
```

(api-analyzer-classes)=

### Analyzer Classes

```{eval-rst}
.. class:: DiffAnalyzer

   Analyzes differences between document structures.

   .. method:: compare(source: List[DocumentNode], target: List[DocumentNode]) -> DiffResult

      Compare two sets of document nodes.

      :param source: Source document nodes
      :param target: Target document nodes
      :returns: Difference analysis result
```

```{eval-rst}
.. class:: QualityAnalyzer

   Analyzes document quality metrics.

   .. method:: analyze(nodes: List[DocumentNode]) -> QualityMetrics

      Calculate quality metrics.

      :returns: Quality metrics including readability, completeness, etc.
```

(api-enumerations)=

## Enumerations

```{eval-rst}
.. class:: NodeType(Enum)

   Node type enumeration.

   .. attribute:: SECTION

      Section heading

   .. attribute:: PARAGRAPH

      Text paragraph

   .. attribute:: CODE_BLOCK

      Code block

   .. attribute:: FIGURE

      Figure or image

   .. attribute:: TABLE

      Table structure

   .. attribute:: ADMONITION

      Note, warning, or other admonition
```

```{eval-rst}
.. class:: DiffType(Enum)

   Difference type enumeration.

   .. attribute:: ADDED

      Content added

   .. attribute:: REMOVED

      Content removed

   .. attribute:: MODIFIED

      Content modified

   .. attribute:: MOVED

      Content relocated
```

(api-exceptions)=

## Exceptions

```{eval-rst}
.. exception:: DocDiffError

   Base exception for all DocDiff errors.
```

```{eval-rst}
.. exception:: ParseError(DocDiffError)

   Raised when document parsing fails.

   .. attribute:: line_number
      :type: int

      Line number where error occurred

   .. attribute:: column
      :type: int

      Column position of error
```

```{eval-rst}
.. exception:: AnalysisError(DocDiffError)

   Raised when analysis fails.
```

```{eval-rst}
.. exception:: ConfigurationError(DocDiffError)

   Raised for configuration issues.
```

(api-utility-functions)=

## Utility Functions

(api-file-operations)=

### File Operations

```{eval-rst}
.. function:: read_document(path: Path, encoding: str = 'utf-8') -> str

   Read document from file.

   :param path: File path
   :param encoding: Text encoding
   :returns: Document content
   :raises IOError: If file cannot be read
```

```{eval-rst}
.. function:: write_report(content: str, path: Path, format: str = 'text')

   Write report to file.

   :param content: Report content
   :param path: Output path
   :param format: Output format
```

(api-path-utilities)=

### Path Utilities

```{eval-rst}
.. function:: find_documents(root: Path, patterns: List[str] = None) -> List[Path]

   Find all documents in directory tree.

   :param root: Root directory
   :param patterns: File patterns (default: ['*.rst', '*.md'])
   :returns: List of document paths
```

```{eval-rst}
.. function:: resolve_references(base: Path, ref: str) -> Path

   Resolve document references.

   :param base: Base path for resolution
   :param ref: Reference to resolve
   :returns: Resolved path
```

(api-configuration)=

## Configuration

```{eval-rst}
.. data:: DEFAULT_CONFIG

   Default configuration dictionary::

      {
          'parser': {
              'strict': False,
              'max_depth': 10,
              'timeout': 30
          },
          'analyzer': {
              'algorithm': 'myers',
              'threshold': 0.8
          },
          'reporter': {
              'format': 'text',
              'verbose': False
          }
      }
```

```{eval-rst}
.. function:: load_config(path: Path = None) -> dict

   Load configuration from file.

   :param path: Configuration file path
   :returns: Configuration dictionary
```

```{eval-rst}
.. function:: merge_configs(*configs) -> dict

   Merge multiple configuration dictionaries.

   :param configs: Configuration dictionaries to merge
   :returns: Merged configuration
```

(api-type-hints)=

## Type Hints

The API uses Python type hints throughout:

```python
from typing import List, Dict, Optional, Union
from pathlib import Path

def process_documents(
    paths: List[Path],
    options: Optional[Dict[str, Any]] = None,
    output: Union[str, Path] = 'output.json'
) -> Dict[str, Any]:
    """Process multiple documents."""
    pass
```

(api-context-managers)=

## Context Managers

```{eval-rst}
.. class:: DatabaseContext

   Context manager for database operations.

   Example::

      with DatabaseContext('docs.db') as db:
          db.store_nodes(nodes)
          results = db.query_nodes(filter_expr)
```

```{eval-rst}
.. class:: CacheContext

   Context manager for caching.

   Example::

      with CacheContext(ttl=3600) as cache:
          result = cache.get_or_compute(key, expensive_function)
```

(api-decorators)=

## Decorators

```{eval-rst}
.. decorator:: @cached(ttl: int = 3600)

   Cache function results.

   :param ttl: Time to live in seconds
```

```{eval-rst}
.. decorator:: @profile(metrics: List[str] = ['time'])

   Profile function execution.

   :param metrics: Metrics to collect
```

```{eval-rst}
.. decorator:: @retry(max_attempts: int = 3, delay: float = 1.0)

   Retry on failure.

   :param max_attempts: Maximum retry attempts
   :param delay: Delay between attempts
```

(api-version-information)=

## Version Information

```{eval-rst}
.. data:: __version__

   Current version string (e.g., '1.0.0')
```

```{eval-rst}
.. data:: __api_version__

   API version for compatibility (e.g., 'v1')
```

```{eval-rst}
.. function:: check_version(required: str) -> bool

   Check if current version meets requirement.

   :param required: Required version string
   :returns: True if requirement is met
```

(api-see-also)=

## See Also

- {doc}`reference` - Detailed API reference
- {doc}`../quickstart` - Getting started guide
- {doc}`../advanced` - Advanced features

______________________________________________________________________

```{eval-rst}
.. meta::
   :description: API documentation for DocDiff
   :keywords: API, reference, documentation
```

