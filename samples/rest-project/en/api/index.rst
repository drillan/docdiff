.. _api-documentation:

===================
API Documentation
===================

Complete API reference for all modules, classes, and functions.

.. toctree::
   :maxdepth: 2
   :caption: API Modules
   
   reference

.. _api-overview:

Overview
========

The DocDiff API is organized into several core modules:

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

.. _api-quick-start:

Quick Start
===========

Basic usage example:

.. code-block:: python
   :linenos:

   from docdiff import parse, analyze, report
   
   # Parse documents
   source_nodes = parse('source.rst')
   target_nodes = parse('target.rst')
   
   # Analyze differences
   diff_result = analyze(source_nodes, target_nodes)
   
   # Generate report
   report_text = report(diff_result, format='markdown')
   print(report_text)

.. _api-core-classes:

Core Classes
============

.. _api-parser-classes:

Parser Classes
--------------

.. class:: BaseParser

   Abstract base class for all parsers.
   
   .. method:: parse(content: str) -> List[DocumentNode]
   
      Parse document content and return nodes.
      
      :param content: Document content as string
      :returns: List of document nodes
      :raises ParseError: If parsing fails

.. class:: ReSTParser(BaseParser)

   Parser for reStructuredText documents.
   
   .. attribute:: strict_mode
      :type: bool
      
      Enable strict parsing mode (default: False)
   
   .. method:: configure(**options)
   
      Configure parser options.

.. class:: MarkdownParser(BaseParser)

   Parser for Markdown documents.
   
   .. attribute:: flavor
      :type: str
      
      Markdown flavor ('github', 'commonmark', 'extra')

.. _api-model-classes:

Model Classes
-------------

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

.. _api-analyzer-classes:

Analyzer Classes
----------------

.. class:: DiffAnalyzer

   Analyzes differences between document structures.
   
   .. method:: compare(source: List[DocumentNode], target: List[DocumentNode]) -> DiffResult
   
      Compare two sets of document nodes.
      
      :param source: Source document nodes
      :param target: Target document nodes
      :returns: Difference analysis result

.. class:: QualityAnalyzer

   Analyzes document quality metrics.
   
   .. method:: analyze(nodes: List[DocumentNode]) -> QualityMetrics
   
      Calculate quality metrics.
      
      :returns: Quality metrics including readability, completeness, etc.

.. _api-enumerations:

Enumerations
============

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

.. _api-exceptions:

Exceptions
==========

.. exception:: DocDiffError

   Base exception for all DocDiff errors.

.. exception:: ParseError(DocDiffError)

   Raised when document parsing fails.
   
   .. attribute:: line_number
      :type: int
      
      Line number where error occurred
   
   .. attribute:: column
      :type: int
      
      Column position of error

.. exception:: AnalysisError(DocDiffError)

   Raised when analysis fails.

.. exception:: ConfigurationError(DocDiffError)

   Raised for configuration issues.

.. _api-utility-functions:

Utility Functions
=================

.. _api-file-operations:

File Operations
---------------

.. function:: read_document(path: Path, encoding: str = 'utf-8') -> str

   Read document from file.
   
   :param path: File path
   :param encoding: Text encoding
   :returns: Document content
   :raises IOError: If file cannot be read

.. function:: write_report(content: str, path: Path, format: str = 'text')

   Write report to file.
   
   :param content: Report content
   :param path: Output path
   :param format: Output format

.. _api-path-utilities:

Path Utilities
--------------

.. function:: find_documents(root: Path, patterns: List[str] = None) -> List[Path]

   Find all documents in directory tree.
   
   :param root: Root directory
   :param patterns: File patterns (default: ['*.rst', '*.md'])
   :returns: List of document paths

.. function:: resolve_references(base: Path, ref: str) -> Path

   Resolve document references.
   
   :param base: Base path for resolution
   :param ref: Reference to resolve
   :returns: Resolved path

.. _api-configuration:

Configuration
=============

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

.. function:: load_config(path: Path = None) -> dict

   Load configuration from file.
   
   :param path: Configuration file path
   :returns: Configuration dictionary

.. function:: merge_configs(*configs) -> dict

   Merge multiple configuration dictionaries.
   
   :param configs: Configuration dictionaries to merge
   :returns: Merged configuration

.. _api-type-hints:

Type Hints
==========

The API uses Python type hints throughout:

.. code-block:: python

   from typing import List, Dict, Optional, Union
   from pathlib import Path
   
   def process_documents(
       paths: List[Path],
       options: Optional[Dict[str, Any]] = None,
       output: Union[str, Path] = 'output.json'
   ) -> Dict[str, Any]:
       """Process multiple documents."""
       pass

.. _api-context-managers:

Context Managers
================

.. class:: DatabaseContext

   Context manager for database operations.
   
   Example::
   
      with DatabaseContext('docs.db') as db:
          db.store_nodes(nodes)
          results = db.query_nodes(filter_expr)

.. class:: CacheContext

   Context manager for caching.
   
   Example::
   
      with CacheContext(ttl=3600) as cache:
          result = cache.get_or_compute(key, expensive_function)

.. _api-decorators:

Decorators
==========

.. decorator:: @cached(ttl: int = 3600)

   Cache function results.
   
   :param ttl: Time to live in seconds

.. decorator:: @profile(metrics: List[str] = ['time'])

   Profile function execution.
   
   :param metrics: Metrics to collect

.. decorator:: @retry(max_attempts: int = 3, delay: float = 1.0)

   Retry on failure.
   
   :param max_attempts: Maximum retry attempts
   :param delay: Delay between attempts

.. _api-version-information:

Version Information
===================

.. data:: __version__
   
   Current version string (e.g., '1.0.0')

.. data:: __api_version__
   
   API version for compatibility (e.g., 'v1')

.. function:: check_version(required: str) -> bool

   Check if current version meets requirement.
   
   :param required: Required version string
   :returns: True if requirement is met

.. _api-see-also:

See Also
========

* :doc:`reference` - Detailed API reference
* :doc:`../quickstart` - Getting started guide
* :doc:`../advanced` - Advanced features

----

.. meta::
   :description: API documentation for DocDiff
   :keywords: API, reference, documentation