(sphinx-integration)=
# Sphinx Integration Guide

Comprehensive guide to docdiff's Sphinx documentation system integration features.

(sphinx-integration-overview)=
## Overview

docdiff provides deep integration with Sphinx documentation projects, automatically detecting and leveraging Sphinx-specific features for improved translation management.

(sphinx-integration-features)=
## Key Features

- **Automatic Project Detection**: Identifies Sphinx projects via conf.py
- **Glossary Extraction**: Parses Sphinx glossary directives
- **Reference Tracking**: Maintains cross-references and links
- **Metadata Preservation**: Keeps directives and roles intact
- **i18n Support**: Compatible with Sphinx internationalization

(sphinx-integration-detection)=
## Project Detection

(sphinx-detection-automatic)=
### Automatic Detection

docdiff automatically detects Sphinx projects:

```{code-block} python
:name: sphinx-code-project-detection
:caption: Sphinx Project Detection

class ProjectDetector:
    """Detects and analyzes Sphinx projects."""
    
    def detect_sphinx_project(self, path: Path) -> bool:
        """Check if directory is a Sphinx project."""
        indicators = [
            path / "conf.py",
            path / "source" / "conf.py",
            path / "_build",
            path / "Makefile"  # Sphinx makefile
        ]
        return any(indicator.exists() for indicator in indicators)
    
    def get_project_config(self, path: Path) -> Dict:
        """Extract Sphinx configuration."""
        conf_path = self.find_conf_py(path)
        if conf_path:
            return self.parse_conf_py(conf_path)
        return {}
```

(sphinx-detection-configuration)=
### Configuration Extraction

docdiff reads key Sphinx settings:

```{code-block} python
:name: sphinx-code-config-extraction
:caption: conf.py Configuration Extraction

# Extracted settings
config = {
    "project": "docdiff",
    "language": "en",
    "extensions": ["myst_parser", "sphinx.ext.autodoc"],
    "source_suffix": {".rst": None, ".md": "myst"},
    "master_doc": "index",
    "exclude_patterns": ["_build", "**.ipynb_checkpoints"]
}
```

(sphinx-integration-glossary)=
## Glossary Management

(sphinx-glossary-extraction)=
### Extracting Glossary Terms

docdiff parses Sphinx glossary directives:

```{code-block} rst
:name: sphinx-code-glossary-rst
:caption: Sphinx Glossary Example

.. glossary::

   API
      Application Programming Interface. A set of protocols
      and tools for building software applications.
   
   REST
      Representational State Transfer. An architectural style
      for distributed hypermedia systems.
   
   JSON
      JavaScript Object Notation. A lightweight data format.
```

Extract with:

```{code-block} bash
:name: sphinx-code-extract-glossary
:caption: Extract Glossary Command

# Extract from reStructuredText
docdiff extract-glossary docs/ --format rst --output glossary.yml

# Extract from MyST Markdown
docdiff extract-glossary docs/ --format myst --output glossary.yml
```

(sphinx-glossary-myst)=
### MyST Glossary Support

MyST-Parser glossary format:

````{code-block} markdown
:name: sphinx-code-glossary-myst
:caption: MyST Glossary Example

```{glossary}
API
  Application Programming Interface. A set of protocols
  and tools for building software applications.

REST
  Representational State Transfer. An architectural style
  for distributed hypermedia systems.

JSON
  JavaScript Object Notation. A lightweight data format.
```
````

(sphinx-glossary-output)=
### Glossary Output Format

Extracted glossary in YAML:

```{code-block} yaml
:name: sphinx-code-glossary-output
:caption: Extracted Glossary YAML

glossary:
  - term: API
    definition: Application Programming Interface. A set of protocols and tools for building software applications.
    source_file: docs/glossary.rst
    line_number: 4
    references: ["api-reference.rst:12", "user-guide.rst:45"]
    
  - term: REST
    definition: Representational State Transfer. An architectural style for distributed hypermedia systems.
    source_file: docs/glossary.rst
    line_number: 8
    references: ["architecture.rst:67"]
    
  - term: JSON
    definition: JavaScript Object Notation. A lightweight data format.
    source_file: docs/glossary.rst
    line_number: 12
    references: ["api-reference.rst:89", "developer-guide.rst:123"]
```

(sphinx-integration-references)=
## Cross-Reference Management

(sphinx-references-tracking)=
### Reference Tracking

docdiff tracks all Sphinx cross-references:

```{code-block} python
:name: sphinx-code-reference-tracking
:caption: Reference Tracking Implementation

class ReferenceTracker:
    """Tracks Sphinx cross-references."""
    
    def track_references(self, content: str) -> Dict[str, List[str]]:
        """Extract all references from content."""
        references = {
            "doc": [],      # :doc: references
            "ref": [],      # :ref: references
            "term": [],     # :term: glossary references
            "class": [],    # :class: API references
            "func": [],     # :func: function references
            "mod": [],      # :mod: module references
        }
        
        # Parse reStructuredText roles
        for match in re.finditer(r':(\w+):`([^`]+)`', content):
            role_type = match.group(1)
            target = match.group(2)
            if role_type in references:
                references[role_type].append(target)
        
        return references
```

(sphinx-references-preservation)=
### Reference Preservation

During translation, references are preserved:

```{code-block} text
:name: sphinx-code-reference-preservation
:caption: Reference Preservation Example

Source (English):
  See :doc:`user-guide` for details and :term:`API` reference.

Translation (Japanese):
  詳細は :doc:`user-guide` を参照し、:term:`API` リファレンスを確認してください。

Note: References remain unchanged, only surrounding text is translated
```

(sphinx-integration-directives)=
## Directive Handling

(sphinx-directives-preservation)=
### Directive Structure Preservation

docdiff maintains Sphinx directive structure:

```{code-block} rst
:name: sphinx-code-directive-preservation
:caption: Directive Preservation

.. note::
   This is an important note.
   
   It can span multiple lines.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,3
   
   def hello():
       print("Hello")
       return True

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   introduction
   user-guide
   api-reference
```

(sphinx-directives-myst)=
### MyST Directive Support

MyST-Parser directive format:

````{code-block} markdown
:name: sphinx-code-myst-directives
:caption: MyST Directives

```{note}
This is an important note.

It can span multiple lines.
```

```{code-block} python
:linenos:
:emphasize-lines: 2,3

def hello():
    print("Hello")
    return True
```

```{toctree}
:maxdepth: 2
:caption: Contents:

introduction
user-guide
api-reference
```
````

(sphinx-integration-i18n)=
## Internationalization (i18n)

(sphinx-i18n-workflow)=
### Sphinx i18n Workflow

Integration with Sphinx's built-in i18n:

```{code-block} bash
:name: sphinx-code-i18n-workflow
:caption: Sphinx i18n Integration

# Step 1: Extract translatable strings (Sphinx)
sphinx-build -b gettext docs/source docs/locale/pot

# Step 2: Export with docdiff for AI translation
docdiff export docs/source docs/locale/ja translation.json \
  --include-context --glossary glossary.yml

# Step 3: Translate with AI
python translate_with_ai.py translation.json

# Step 4: Import back
docdiff import translation_complete.json docs/locale/ja

# Step 5: Build localized docs
sphinx-build -D language=ja docs/source docs/build/ja
```

(sphinx-i18n-po-support)=
### PO/POT File Support (Planned)

Future support for gettext formats:

```{code-block} bash
:name: sphinx-code-po-support
:caption: PO/POT File Support (Coming Soon)

# Export to POT format
docdiff export docs/source translation.pot --format pot

# Import from PO files
docdiff import translated.po docs/locale/ja --format po

# Merge with existing translations
docdiff merge existing.po new.po --output merged.po
```

(sphinx-integration-metadata)=
## Metadata Management

(sphinx-metadata-extraction)=
### Metadata Extraction

docdiff extracts Sphinx-specific metadata:

```{code-block} python
:name: sphinx-code-metadata-extraction
:caption: Metadata Extraction

metadata = {
    "labels": {},      # Reference labels
    "names": {},       # Named blocks
    "captions": {},    # Figure/table captions
    "toctree": [],     # Table of contents
    "index": [],       # Index entries
    "domains": {       # Sphinx domains
        "py": [],      # Python domain
        "c": [],       # C domain
        "js": [],      # JavaScript domain
    }
}
```

(sphinx-metadata-example)=
### Metadata Example

```{code-block} rst
:name: sphinx-code-metadata-example
:caption: Rich Metadata Example

.. _installation-guide:
.. index:: installation, setup, configuration

Installation Guide
==================

.. figure:: images/architecture.png
   :name: fig-architecture
   :caption: System Architecture Diagram
   :alt: Architecture diagram showing components
   
   This diagram illustrates the system components.

.. code-block:: python
   :name: code-example-hello
   :caption: Hello World Example
   :linenos:
   
   def hello_world():
       """Simple greeting function."""
       print("Hello, World!")
```

(sphinx-integration-automation)=
## Automation Features

(sphinx-automation-hooks)=
### Build Hooks

Integrate docdiff with Sphinx build process:

```{code-block} python
:name: sphinx-code-build-hooks
:caption: conf.py Build Hooks

# In conf.py
def setup(app):
    """Setup Sphinx application hooks."""
    
    # Before build: check translation status
    app.connect("builder-inited", check_translation_status)
    
    # After build: generate translation report
    app.connect("build-finished", generate_translation_report)
    
def check_translation_status(app):
    """Check translation coverage before build."""
    import subprocess
    result = subprocess.run(
        ["docdiff", "status", "source", "locale/ja"],
        capture_output=True
    )
    print(f"Translation coverage: {result.stdout}")

def generate_translation_report(app, exception):
    """Generate translation report after build."""
    if not exception:
        subprocess.run([
            "docdiff", "compare", 
            "source", "locale/ja",
            "--output", "_build/translation-report.md"
        ])
```

(sphinx-automation-makefile)=
### Makefile Integration

Add docdiff commands to Sphinx Makefile:

```{code-block} makefile
:name: sphinx-code-makefile
:caption: Makefile Integration

# Sphinx Makefile additions

.PHONY: translation-status
translation-status:
	@docdiff status source locale/$(LANG)

.PHONY: export-translation
export-translation:
	@docdiff export source locale/$(LANG) translation.json \
		--include-context --glossary glossary.yml

.PHONY: import-translation
import-translation:
	@docdiff import translation_complete.json locale/$(LANG)

.PHONY: translation-report
translation-report:
	@docdiff compare source locale/$(LANG) \
		--output _build/translation-report.md --html
```

(sphinx-integration-best-practices)=
## Best Practices

(sphinx-practices-structure)=
### Project Structure

Recommended Sphinx project layout:

```{code-block} text
:name: sphinx-code-project-structure
:caption: Recommended Project Structure

docs/
├── source/                 # Source documentation
│   ├── conf.py            # Sphinx configuration
│   ├── index.rst          # Master document
│   ├── _static/           # Static files
│   ├── _templates/        # Custom templates
│   └── *.rst/*.md         # Documentation files
├── locale/                # Translations
│   ├── pot/              # POT templates
│   ├── ja/               # Japanese translations
│   └── zh/               # Chinese translations
├── _build/               # Build output
└── .docdiff/            # docdiff cache
    ├── glossary.yml     # Extracted glossary
    └── cache/           # Parsed structure cache
```

(sphinx-practices-workflow)=
### Translation Workflow

1. **Setup Project Structure**: Organize source and locale directories
2. **Extract Glossary**: Build terminology database
3. **Initial Export**: Create translation tasks with context
4. **AI Translation**: Process with optimized batching
5. **Import & Review**: Apply translations and review
6. **Build & Verify**: Generate localized documentation
7. **Continuous Updates**: Track changes and update incrementally

(sphinx-integration-troubleshooting)=
## Troubleshooting

(sphinx-troubleshooting-common)=
### Common Issues

| Issue | Solution |
|-------|----------|
| conf.py not detected | Check path or use `--sphinx-conf` option |
| Glossary not extracted | Verify glossary directive format |
| References broken | Ensure target documents exist |
| Directives lost | Check parser (rst vs myst) |
| Metadata missing | Update to latest docdiff version |

(sphinx-troubleshooting-validation)=
### Validation Commands

```{code-block} bash
:name: sphinx-code-validation
:caption: Validation Commands

# Validate Sphinx project
docdiff validate-sphinx docs/source

# Check references
docdiff check-references docs/source

# Verify glossary
docdiff verify-glossary docs/source glossary.yml

# Test build with translation
sphinx-build -D language=ja -W docs/source docs/test
```

(sphinx-integration-summary)=
## Summary

docdiff's Sphinx integration provides:

- **Seamless compatibility** with existing Sphinx projects
- **Automatic feature detection** and configuration
- **Glossary and reference management** for consistency
- **Metadata preservation** throughout translation
- **Build process integration** for automation
- **Future-proof** design for upcoming Sphinx features

Leverage docdiff to manage your Sphinx documentation translations efficiently!