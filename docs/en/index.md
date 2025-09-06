(docdiff-docs)=
# docdiff Documentation

(docdiff-overview)=
## Overview

docdiff is a powerful multilingual translation management tool specifically designed for MyST and reStructuredText documentation. It provides intelligent document structure analysis and translation state tracking to streamline the internationalization of technical documentation.

(docdiff-key-features)=
## Key Features

- **Intelligent Structure Analysis**: Parses documents into logical structural units (sections, code blocks, tables, figures) rather than mechanical text chunks
- **Advanced Comparison Engine**: Multi-pass matching algorithm with exact, fuzzy, and missing node detection
- **Rich Visualization**: Multiple view modes including tree view, metadata grouping, side-by-side comparison, and statistics
- **Flexible Export/Import**: Supports JSON, CSV, XLSX, XLIFF 2.1, and Markdown formats for seamless translation workflows
- **Metadata-Aware Processing**: Preserves and tracks labels, names, captions, and other structural metadata
- **Git-Friendly Reports**: Markdown output with multiple styles (detailed, GitHub-flavored, compact) for version control integration
- **Incremental Updates**: Efficiently handles document changes through hash-based content detection
- **Cache Management**: Centralized project cache in `.docdiff/` directory for persistence and performance

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

# Export translation tasks to CSV
docdiff export docs/en docs/ja --format csv --output tasks.csv

# Import completed translations
docdiff import tasks_completed.csv --source-dir docs/en --target-dir docs/ja
```

(docdiff-documentation-contents)=
## Documentation Contents

```{toctree}
:caption: 'User Documentation:'
:maxdepth: 2

user-guide
cli-reference
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
- **✅ Translation Coverage Analysis**: Comprehensive comparison engine with fuzzy matching
- **✅ Multiple Export Formats**: JSON, CSV, XLSX, XLIFF 2.1, and Markdown reports
- **✅ Rich Visualization**: Terminal-based and file-based reporting with multiple view modes
- **✅ Translation Workflow**: Complete export/import cycle for translation management

### Upcoming Features
- **Machine Translation Integration**: Support for AI-powered translation services
- **Web Interface**: Browser-based UI for non-technical users
- **Translation Memory**: Reuse of previously translated content

(docdiff-getting-help)=
## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/docdiff/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)
- **Contributing**: See our {doc}`developer-guide` for contribution guidelines

(docdiff-license)=
## License

docdiff is open source software licensed under the MIT License.
