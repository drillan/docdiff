(docdiff-docs)=
# docdiff Documentation

(docdiff-overview)=
## Overview

docdiff is a powerful multilingual translation management tool specifically designed for MyST and reStructuredText documentation. It provides intelligent document structure analysis and translation state tracking to streamline the internationalization of technical documentation.

(docdiff-key-features)=
## Key Features

- **Intelligent Structure Analysis**: Parses documents into logical structural units (sections, code blocks, tables, figures) rather than mechanical text chunks
- **AI Translation Optimization**: Adaptive batch optimization achieving 81% efficiency with 69% API call reduction
- **Advanced Comparison Engine**: Multi-pass matching algorithm with exact, fuzzy, and missing node detection
- **Sphinx Integration**: Automatic glossary extraction and cross-reference tracking for consistent translations
- **Rich Visualization**: Multiple view modes including tree view, metadata grouping, side-by-side comparison, and statistics
- **Flexible Export/Import**: Supports hierarchical JSON (schema v1.0), CSV, XLSX, XLIFF 2.1 for seamless workflows
- **Context-Aware Translation**: Preserves document hierarchy and includes surrounding context for better AI translations
- **Metadata-Aware Processing**: Preserves and tracks labels, names, captions, and other structural metadata
- **Git-Friendly Reports**: Markdown output with multiple styles (detailed, GitHub-flavored, compact) for version control integration
- **Incremental Updates**: Efficiently handles document changes through hash-based content detection
- **Performance Optimized**: Processes 14,000+ nodes/second with intelligent token estimation and batching

(docdiff-quick-start)=
## Quick Start

```{code-block} bash
:name: docdiff-code-quick-start
:caption: Quick Start Commands
:linenos:

# Install docdiff
uv sync
uv pip install -e .

# Compare documentation between languages
docdiff compare docs/en docs/ja

# Generate detailed Markdown report
docdiff compare docs/en docs/ja --output report.md

# Export for AI translation (optimized batching)
docdiff export docs/en docs/ja translation.json \
  --include-context --batch-size 1500 \
  --glossary glossary.yml

# Export translation tasks to CSV
docdiff export docs/en docs/ja tasks.csv --format csv

# Import completed translations
docdiff import translation_complete.json docs/ja
```

(docdiff-documentation-contents)=
## Documentation Contents

```{toctree}
:caption: 'User Documentation:'
:maxdepth: 2

user-guide
cli-reference
ai-translation
sphinx-integration
architecture
```

```{toctree}
:caption: 'Developer Documentation:'
:maxdepth: 2

developer-guide
api-reference
```

(docdiff-why)=
## Why docdiff?

Traditional translation tools often break documents into fragments that are too small, losing important context. docdiff solves this by:

1. **Preserving Document Structure**: Maintains the logical organization of your documentation
2. **Context-Aware Translation Units**: Groups related content together for better translation quality
3. **Efficient Change Management**: Only retranslates what has actually changed
4. **Reference Integrity**: Ensures cross-references remain valid across languages

(docdiff-project-status)=
## Project Status

docdiff is actively maintained with the following features available:

- **✅ Document Structure Analysis**: Advanced MyST/reStructuredText parsing with metadata preservation
- **✅ AI Translation Optimization**: Adaptive batching with 81% efficiency and 69% API call reduction
- **✅ Sphinx Integration**: Automatic glossary extraction and cross-reference tracking
- **✅ Translation Coverage Analysis**: Comprehensive comparison engine with fuzzy matching
- **✅ Multiple Export Formats**: Hierarchical JSON (v1.0), CSV, XLSX, XLIFF 2.1, and Markdown reports
- **✅ Context-Aware Export**: Preserves document hierarchy with configurable context windows
- **✅ Rich Visualization**: Terminal-based and file-based reporting with multiple view modes
- **✅ Translation Workflow**: Complete export/import cycle for translation management
- **✅ Performance Optimized**: Processes 14,000+ nodes/second with minimal memory footprint

### Upcoming Features
- **Parallel Batch Processing**: Concurrent API calls for faster translation
- **Web Interface**: Browser-based UI for non-technical users
- **Translation Memory**: Reuse of previously translated content
- **POT/PO Format Support**: Full Sphinx i18n integration

(docdiff-getting-help)=
## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/docdiff/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)
- **Contributing**: See our {doc}`developer-guide` for contribution guidelines

(docdiff-license)=
## License

docdiff is open source software licensed under the MIT License.
