.. _api-reference:

==================
API Reference
==================

Detailed reference for all public APIs, organized by module.

.. contents:: Module Index
   :local:
   :depth: 2

docdiff.parsers
===============

This module provides document parsing functionality.

Classes
-------

BaseParser
~~~~~~~~~~

.. py:class:: docdiff.parsers.BaseParser

   Abstract base class for document parsers.
   
   .. py:method:: __init__(config: Optional[Dict] = None)
   
      Initialize parser with configuration.
      
      :param config: Parser configuration dictionary
      :type config: dict or None
   
   .. py:method:: parse(content: str, path: Optional[Path] = None) -> List[DocumentNode]
      :abstractmethod:
      
      Parse document content.
      
      :param content: Document content
      :type content: str
      :param path: Optional file path for context
      :type path: pathlib.Path or None
      :returns: List of parsed document nodes
      :rtype: List[DocumentNode]
      :raises ParseError: When parsing fails
      
      Example::
      
         parser = ReSTParser()
         nodes = parser.parse(content)
   
   .. py:method:: validate(content: str) -> List[ValidationError]
   
      Validate document syntax.
      
      :param content: Content to validate
      :returns: List of validation errors
      :rtype: List[ValidationError]
   
   .. py:attribute:: supported_extensions
      :type: List[str]
      
      List of supported file extensions.

ReSTParser
~~~~~~~~~~

.. py:class:: docdiff.parsers.ReSTParser(BaseParser)

   Parser for reStructuredText documents.
   
   .. py:method:: parse_directive(line: str, lines: List[str], index: int) -> Optional[DirectiveNode]
   
      Parse a reStructuredText directive.
      
      :param line: Current line containing directive
      :param lines: All document lines
      :param index: Current line index
      :returns: Parsed directive node or None
      
   .. py:method:: parse_section(lines: List[str], index: int) -> Optional[SectionNode]
   
      Parse a section with heading.
      
      :returns: Section node with title and level

MySTParser
~~~~~~~~~~

.. py:class:: docdiff.parsers.MySTParser(BaseParser)

   Parser for MyST (Markedly Structured Text) documents.
   
   .. py:method:: enable_extension(name: str) -> None
   
      Enable a MyST extension.
      
      :param name: Extension name ('deflist', 'tasklist', etc.)
      
   .. py:attribute:: extensions
      :type: Set[str]
      
      Currently enabled extensions.

docdiff.models
==============

Data models and structures.

Classes
-------

.. _api-ref-documentnode:

DocumentNode
~~~~~~~~~~~~

.. py:class:: docdiff.models.DocumentNode

   Represents a document structure element.
   
   .. py:method:: __init__(type: NodeType, content: str = '', **kwargs)
   
      Create a document node.
      
      :param type: Node type
      :param content: Text content
      :param kwargs: Additional attributes
   
   .. py:method:: add_child(node: DocumentNode) -> None
   
      Add a child node.
      
      :param node: Child node to add
   
   .. py:method:: find_all(type: NodeType) -> List[DocumentNode]
   
      Find all descendant nodes of given type.
      
      :param type: Node type to search for
      :returns: List of matching nodes
   
   .. py:method:: get_text() -> str
   
      Get all text content recursively.
      
      :returns: Combined text content
   
   .. py:property:: depth
      :type: int
      
      Depth in document tree.
   
   .. py:property:: path
      :type: str
      
      Path from root (e.g., "section[0]/paragraph[2]").

.. _api-ref-sectionnode:

SectionNode
~~~~~~~~~~~

.. py:class:: docdiff.models.SectionNode(DocumentNode)

   Section node with heading.
   
   .. py:attribute:: title
      :type: str
      
      Section title text.
   
   .. py:attribute:: level
      :type: int
      
      Section level (1-6).
   
   .. py:attribute:: label
      :type: Optional[str]
      
      Optional reference label.

.. _api-ref-codeblocknode:

CodeBlockNode
~~~~~~~~~~~~~

.. py:class:: docdiff.models.CodeBlockNode(DocumentNode)

   Code block node.
   
   .. py:attribute:: language
      :type: Optional[str]
      
      Programming language.
   
   .. py:attribute:: caption
      :type: Optional[str]
      
      Optional caption.
   
   .. py:attribute:: linenos
      :type: bool
      
      Show line numbers.
   
   .. py:attribute:: emphasize_lines
      :type: List[int]
      
      Lines to emphasize.

docdiff.analyzers
=================

Document analysis functionality.

Classes
-------

.. _api-ref-structureanalyzer:

StructureAnalyzer
~~~~~~~~~~~~~~~~~

.. py:class:: docdiff.analyzers.StructureAnalyzer

   Analyze document structure.
   
   .. py:method:: analyze(nodes: List[DocumentNode]) -> StructureReport
   
      Analyze document structure.
      
      :param nodes: Document nodes
      :returns: Structure analysis report
      
      Example::
      
         analyzer = StructureAnalyzer()
         report = analyzer.analyze(nodes)
         print(f"Sections: {report.section_count}")
         print(f"Max depth: {report.max_depth}")
   
   .. py:method:: build_toc(nodes: List[DocumentNode]) -> TableOfContents
   
      Build table of contents.
      
      :returns: Table of contents structure

.. _api-ref-diffanalyzer:

DiffAnalyzer
~~~~~~~~~~~~

.. py:class:: docdiff.analyzers.DiffAnalyzer

   Compare document structures.
   
   .. py:method:: compare(source: List[DocumentNode], target: List[DocumentNode], **options) -> DiffResult
   
      Compare two documents.
      
      :param source: Source document nodes
      :param target: Target document nodes
      :param options: Comparison options
      :returns: Difference analysis
      
      Options:
      
      * ``algorithm`` (str): Diff algorithm ('myers', 'patience')
      * ``threshold`` (float): Similarity threshold (0.0-1.0)
      * ``ignore_whitespace`` (bool): Ignore whitespace changes
   
   .. py:method:: calculate_similarity(node1: DocumentNode, node2: DocumentNode) -> float
   
      Calculate similarity between nodes.
      
      :returns: Similarity score (0.0-1.0)

.. _api-ref-translationanalyzer:

TranslationAnalyzer
~~~~~~~~~~~~~~~~~~~

.. py:class:: docdiff.analyzers.TranslationAnalyzer(DiffAnalyzer)

   Analyze translation status.
   
   .. py:method:: analyze_translation(source: List[DocumentNode], translation: List[DocumentNode]) -> TranslationReport
   
      Analyze translation completeness.
      
      :returns: Translation analysis report
   
   .. py:attribute:: coverage
      :type: float
      
      Translation coverage percentage.

docdiff.reporters
=================

Report generation utilities.

Classes
-------

.. _api-ref-basereporter:

BaseReporter
~~~~~~~~~~~~

.. py:class:: docdiff.reporters.BaseReporter

   Abstract base class for reporters.
   
   .. py:method:: generate(data: Any, **options) -> str
      :abstractmethod:
      
      Generate report from data.
      
      :param data: Data to report
      :param options: Generation options
      :returns: Generated report

.. _api-ref-markdownreporter:

MarkdownReporter
~~~~~~~~~~~~~~~~

.. py:class:: docdiff.reporters.MarkdownReporter(BaseReporter)

   Generate Markdown reports.
   
   .. py:method:: set_template(template: str) -> None
   
      Set custom template.
      
      :param template: Jinja2 template string
   
   .. py:attribute:: include_toc
      :type: bool
      
      Include table of contents.

.. _api-ref-jsonreporter:

JSONReporter
~~~~~~~~~~~~

.. py:class:: docdiff.reporters.JSONReporter(BaseReporter)

   Generate JSON reports.
   
   .. py:attribute:: indent
      :type: int
      
      JSON indentation level.
   
   .. py:attribute:: sort_keys
      :type: bool
      
      Sort dictionary keys.

.. _api-ref-htmlreporter:

HTMLReporter
~~~~~~~~~~~~

.. py:class:: docdiff.reporters.HTMLReporter(BaseReporter)

   Generate HTML reports with styling.
   
   .. py:method:: add_css(css: str) -> None
   
      Add custom CSS styles.
   
   .. py:method:: add_javascript(js: str) -> None
   
      Add custom JavaScript.
   
   .. py:attribute:: theme
      :type: str
      
      Color theme ('light', 'dark', 'auto').

docdiff.utils
=============

Utility functions and helpers.

Functions
---------

.. _api-ref-file-operations:

File Operations
~~~~~~~~~~~~~~~

.. py:function:: docdiff.utils.read_file(path: Path, encoding: str = 'utf-8') -> str

   Read file contents.
   
   :param path: File path
   :param encoding: Text encoding
   :returns: File contents
   :raises: FileNotFoundError, UnicodeDecodeError

.. py:function:: docdiff.utils.write_file(path: Path, content: str, encoding: str = 'utf-8') -> None

   Write content to file.
   
   :param path: Output path
   :param content: Content to write
   :param encoding: Text encoding

.. py:function:: docdiff.utils.find_files(root: Path, pattern: str = '**/*.rst', recursive: bool = True) -> List[Path]

   Find files matching pattern.
   
   :param root: Root directory
   :param pattern: Glob pattern
   :param recursive: Search recursively
   :returns: List of matching paths

.. _api-ref-text-processing:

Text Processing
~~~~~~~~~~~~~~~

.. py:function:: docdiff.utils.normalize_whitespace(text: str) -> str

   Normalize whitespace in text.
   
   :param text: Input text
   :returns: Normalized text

.. py:function:: docdiff.utils.calculate_hash(content: str, algorithm: str = 'sha256') -> str

   Calculate content hash.
   
   :param content: Content to hash
   :param algorithm: Hash algorithm
   :returns: Hex digest

.. py:function:: docdiff.utils.extract_words(text: str, language: str = 'en') -> List[str]

   Extract words from text.
   
   :param text: Input text
   :param language: Language code
   :returns: List of words

.. _api-ref-logging:

Logging
~~~~~~~

.. py:function:: docdiff.utils.setup_logging(level: str = 'INFO', format: str = 'text') -> None

   Configure logging.
   
   :param level: Log level
   :param format: Output format ('text', 'json')

.. py:function:: docdiff.utils.get_logger(name: str) -> logging.Logger

   Get logger instance.
   
   :param name: Logger name
   :returns: Logger instance

docdiff.exceptions
==================

Exception classes.

.. _api-ref-exception-hierarchy:

Exception Hierarchy
-------------------

::

   DocDiffError
   ├── ParseError
   │   ├── SyntaxError
   │   └── StructureError
   ├── AnalysisError
   │   ├── ComparisonError
   │   └── MetricsError
   └── ConfigurationError
       ├── InvalidConfigError
       └── MissingConfigError

Classes
-------

.. py:exception:: docdiff.exceptions.DocDiffError

   Base exception class.
   
   .. py:attribute:: message
      :type: str
      
      Error message.
   
   .. py:attribute:: context
      :type: Dict[str, Any]
      
      Error context information.

.. py:exception:: docdiff.exceptions.ParseError(DocDiffError)

   Parsing error.
   
   .. py:attribute:: line
      :type: Optional[int]
      
      Line number where error occurred.
   
   .. py:attribute:: column
      :type: Optional[int]
      
      Column position.

.. py:exception:: docdiff.exceptions.AnalysisError(DocDiffError)

   Analysis error.
   
   .. py:attribute:: phase
      :type: str
      
      Analysis phase where error occurred.

Constants
=========

.. py:data:: docdiff.VERSION
   :type: str
   
   Library version string.

.. py:data:: docdiff.DEFAULT_ENCODING
   :type: str
   :value: 'utf-8'
   
   Default text encoding.

.. py:data:: docdiff.SUPPORTED_FORMATS
   :type: List[str]
   :value: ['restructuredtext', 'markdown', 'myst']
   
   Supported document formats.

.. py:data:: docdiff.MAX_FILE_SIZE
   :type: int
   :value: 104857600
   
   Maximum file size in bytes (100MB).

Type Aliases
============

.. py:data:: NodeList
   :type: Type[List[DocumentNode]]
   
   List of document nodes.

.. py:data:: ConfigDict
   :type: Type[Dict[str, Any]]
   
   Configuration dictionary.

.. py:data:: PathLike
   :type: Type[Union[str, Path]]
   
   Path-like object.

Examples
========

Basic Usage
-----------

.. code-block:: python
   :caption: Complete workflow example

   from docdiff import (
       ReSTParser, 
       DiffAnalyzer,
       MarkdownReporter
   )
   from pathlib import Path
   
   # Parse documents
   parser = ReSTParser()
   source = parser.parse(Path('v1/doc.rst').read_text())
   target = parser.parse(Path('v2/doc.rst').read_text())
   
   # Analyze differences
   analyzer = DiffAnalyzer()
   diff = analyzer.compare(source, target)
   
   # Generate report
   reporter = MarkdownReporter()
   report = reporter.generate(diff)
   
   # Save report
   Path('diff_report.md').write_text(report)

Advanced Usage
--------------

.. code-block:: python
   :caption: Custom analyzer example

   from docdiff.analyzers import BaseAnalyzer
   from docdiff.models import DocumentNode
   
   class CustomAnalyzer(BaseAnalyzer):
       """Custom analyzer implementation."""
       
       def analyze(self, nodes: List[DocumentNode]) -> Dict:
           """Perform custom analysis."""
           results = {
               'total_nodes': len(nodes),
               'node_types': {},
               'max_depth': 0
           }
           
           for node in self.traverse_all(nodes):
               # Count node types
               node_type = node.type.value
               results['node_types'][node_type] = \
                   results['node_types'].get(node_type, 0) + 1
               
               # Track max depth
               results['max_depth'] = max(
                   results['max_depth'],
                   node.depth
               )
           
           return results

----

.. meta::
   :description: Complete API reference for DocDiff
   :keywords: API, reference, documentation, parsers, analyzers