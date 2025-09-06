(docdiff-docs)=
# docdiff Documentation

(docdiff-overview)=
## Overview

docdiff is a powerful multilingual translation management tool specifically designed for MyST and reStructuredText documentation. It provides intelligent document structure analysis and translation state tracking to streamline the internationalization of technical documentation.

(docdiff-key-features)=
## Key Features

- **Intelligent Structure Analysis**: Parses documents into logical structural units (sections, code blocks, tables, figures) rather than mechanical text chunks
- **Translation State Management**: Tracks translation status (pending, translated, reviewed, outdated) for each document element
- **Sphinx Integration**: Seamlessly works with Sphinx documentation projects
- **Cross-reference Preservation**: Maintains document integrity by tracking and preserving cross-references
- **Incremental Updates**: Efficiently handles document changes through hash-based content detection
- **Flexible Export**: Supports multiple export formats for integration with translation workflows

(docdiff-quick-start)=
## Quick Start

```{code-block} bash
:name: docdiff-code-quick-start
:caption: Quick Start Commands
:linenos:

# Install docdiff
uv sync
uv pip install -e .

# Parse your documentation project
docdiff parse docs/

# Check translation status
docdiff status docs/ --target-lang ja

# Export for translation
docdiff export docs/ --format json --output translation.json
```

(docdiff-documentation-contents)=
## Documentation Contents

```{toctree}
:caption: 'User Documentation:'
:maxdepth: 2

architecture
cli-reference
```

```{toctree}
:caption: 'Developer Documentation:'
:maxdepth: 2

api-reference
developer-guide
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

docdiff is actively under development. The core architecture is defined and implementation is proceeding in phases:

- **Phase 1 (Current)**: Core parsing and structure analysis
- **Phase 2**: Advanced translation management features
- **Phase 3**: AI translation service integration and web UI

(docdiff-getting-help)=
## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/docdiff/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)
- **Contributing**: See our {doc}`developer-guide` for contribution guidelines

(docdiff-license)=
## License

docdiff is open source software licensed under the MIT License.
