---
substitutions:
  date: '{sub-ref}`today`'
  project: DocDiff
  version: 1.0.0
---

(quickstart-guide)=

# Quick Start Guide

This guide covers the essential features you need to get started quickly.
Follow along to learn the basics of our system.

```{contents} Table of Contents
:depth: 2
:local: true
```

(quickstart-installation)=

## Installation

(quickstart-prerequisites)=

### Prerequisites

Before installing, ensure you have:

- Python 3.8 or higher
- pip package manager
- Git (for development installation)

(quickstart-basic-installation)=

### Basic Installation

The simplest way to install is via pip:

```
pip install docdiff
```

To verify the installation:

```
docdiff --version
```

(quickstart-development-installation)=

### Development Installation

For development work, clone and install in editable mode:

```{code-block} bash
:caption: Development setup
:emphasize-lines: 3

git clone https://github.com/example/docdiff.git
cd docdiff
pip install -e .  # This is the important line
```

(quickstart-configuration)=

## Configuration

````{tab-set}

```{tab-item} YAML Configuration
:sync: yaml

Create a `config.yaml` file:

```yaml
parser:
  format: restructuredtext
  strict: false
output:
  format: json
  pretty: true
```

```

```{tab-item} JSON Configuration
:sync: json

Or use `config.json`:

```json
{
  "parser": {
    "format": "restructuredtext",
    "strict": false
  },
  "output": {
    "format": "json",
    "pretty": true
  }
}
```

```

```{tab-item} Python Configuration
:sync: python

Or configure in Python:

```python
config = {
    "parser": {
        "format": "restructuredtext",
        "strict": False
    },
    "output": {
        "format": "json",
        "pretty": True
    }
}
```

```

````

(quickstart-initial-setup)=

### Initial Setup

Create a configuration file:

```{code-block} yaml
:caption: config.yaml
:name: basic-config

# Basic configuration
parser:
  format: restructuredtext
  strict: false

output:
  format: json
  pretty: true

cache:
  enabled: true
  directory: ~/.docdiff/cache
```

(quickstart-environment-variables)=

### Environment Variables

You can also use environment variables:

```{eval-rst}
.. list-table:: Environment Variables
   :widths: 25 25 50
   :header-rows: 1

   * - Variable
     - Default
     - Description
   * - DOCDIFF_CONFIG
     - ./config.yaml
     - Path to configuration file
   * - DOCDIFF_CACHE
     - ~/.docdiff
     - Cache directory location
   * - DOCDIFF_LOG_LEVEL
     - INFO
     - Logging level (DEBUG, INFO, WARNING, ERROR)
```

(quickstart-basic-usage)=

## Basic Usage

(quickstart-parsing-documents)=

### Parsing Documents

Parse a single document:

```
docdiff parse document.rst
```

Parse a directory:

```
docdiff parse /path/to/docs/
```

:::{note}
The parser automatically detects the document format based on
file extension (.rst for reStructuredText, .md for Markdown).
:::

(quickstart-comparing-documents)=

### Comparing Documents

Compare two versions:

```bash
docdiff compare old.rst new.rst
```

Compare directories:

```bash
docdiff compare docs/v1/ docs/v2/
```

(quickstart-working-with-lists)=

## Working with Lists

(quickstart-bullet-lists)=

### Bullet Lists

Simple bullet list:

- First item
- Second item
- Third item with a longer description
  that spans multiple lines
- Fourth item

Nested bullet list:

- Main item 1

  - Sub-item 1.1
  - Sub-item 1.2

- Main item 2

  - Sub-item 2.1

    - Sub-sub-item 2.1.1
    - Sub-sub-item 2.1.2

(quickstart-numbered-lists)=

### Numbered Lists

Simple numbered list:

1. First step
2. Second step
3. Third step

With sub-items:

1. Preparation

   1. Gather materials
   2. Read instructions
   3. Set up workspace

2. Execution

   1. Follow step-by-step guide
   2. Monitor progress
   3. Make adjustments as needed

3. Cleanup

   1. Store tools
   2. Document results

(quickstart-definition-lists)=

### Definition Lists

Parser

: A component that analyzes document structure

Analyzer

: Processes parsed nodes to extract information

Reporter

: Generates human-readable output from analysis

(quickstart-code-examples)=

## Code Examples

(quickstart-inline-code)=

### Inline Code

Use `inline code` for short snippets like `variable_name` or `function()`.

(quickstart-code-blocks)=

### Code Blocks

Python example:

```{code-block} python
:emphasize-lines: 4,5
:linenos: true

def fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n  # Base case
    return fibonacci(n-1) + fibonacci(n-2)  # Recursive case

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

JavaScript example:

```{code-block} javascript
:caption: async-example.js

async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

(quickstart-literal-blocks)=

### Literal Blocks

Simple literal block using double colon:

```
This is a literal block.
All whitespace is preserved.
    Including indentation.
```

(quickstart-admonitions)=

## Admonitions

(quickstart-information-notes)=

### Information Notes

:::{note}
This is a note providing additional information that might be
helpful but isn't critical to understanding.
:::

:::{tip}
Here's a helpful tip that can save you time or improve your workflow.
:::

(quickstart-warnings-and-cautions)=

### Warnings and Cautions

:::{warning}
This is a warning about potential issues or problems you might encounter.
:::

:::{caution}
Exercise caution when performing this operation as it may have
unintended consequences.
:::

:::{danger}
This action is dangerous and could result in data loss or system damage.
:::

(quickstart-other-admonitions)=

### Other Admonitions

:::{important}
This information is important for proper system operation.
:::

:::{attention}
Pay special attention to this information.
:::

:::{hint}
This might help you solve a common problem.
:::

:::{error}
This describes an error condition and how to resolve it.
:::

(quickstart-tables)=

## Tables

(quickstart-simple-table)=

### Simple Table

```{eval-rst}
.. table:: Feature Comparison
   :widths: auto

   ===============  =========  =========  =========
   Feature          Basic      Pro        Enterprise
   ===============  =========  =========  =========
   Users            5          50         Unlimited
   Storage          10GB       100GB      1TB
   Support          Email      Phone      24/7
   API Access       No         Yes        Yes
   Custom Domain    No         Yes        Yes
   ===============  =========  =========  =========
```

(quickstart-csv-table)=

### CSV Table

```{eval-rst}
.. csv-table:: Performance Metrics
   :header: "Operation", "Time (ms)", "Memory (MB)", "CPU (%)"
   :widths: 30, 20, 20, 20

   "Parse", "45", "12.3", "25"
   "Analyze", "120", "45.6", "60"
   "Generate", "30", "8.9", "15"
   "Export", "15", "5.2", "10"
```

(quickstart-list-table)=

### List Table

```{eval-rst}
.. list-table:: Command Options
   :widths: 15 30 55
   :header-rows: 1
   :stub-columns: 1

   * - Option
     - Type
     - Description
   * - -v, --verbose
     - flag
     - Enable verbose output
   * - -o, --output
     - string
     - Specify output file path
   * - -f, --format
     - choice
     - Output format (json, yaml, xml)
   * - --config
     - path
     - Path to configuration file
```

(quickstart-cross-references)=

## Cross-References

(quickstart-internal-links)=

### Internal Links

- See the {ref}`quickstart-guide` (this page)
- Check {ref}`basic-config` for configuration details
- Review {ref}`main-index` for the complete index

(quickstart-document-links)=

### Document Links

- Read the {doc}`index` page
- Explore {doc}`advanced` features
- API documentation in {doc}`api/index`

(quickstart-footnotes)=

## Footnotes

This is a sentence with a footnote [^f1].

You can also use numbered footnotes [^footnote-1] which are automatically numbered.

Citations are similar but use a different syntax [^cite_cit2024].

[^f1]: This is the footnote text that appears at the bottom.

[^footnote-1]: This footnote is automatically numbered.

[^cite_cit2024]: Example Citation, "Title of Work", 2024.

(quickstart-images-and-figures)=

## Images and Figures

(quickstart-simple-image)=

### Simple Image

```{image} _static/diagram.png
:align: center
:alt: System Architecture Diagram
:width: 400px
```

(quickstart-figure-with-caption)=

### Figure with Caption

:::{figure} _static/diagram.png
:align: center
:alt: Detailed system architecture
:name: fig-architecture
:width: 500px

**Figure 1:** Complete system architecture showing all components
and their interactions. Notice the bidirectional data flow.
:::

(quickstart-substitutions)=

## Substitutions

This documentation is for {{ project }} version {{ version }}, generated on {{ date }}.

(quickstart-raw-output)=

## Raw Output

```{raw} html
<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
    <strong>HTML Note:</strong> This content is only visible in HTML output.
</div>
```

(quickstart-include-files)=

## Include Files

You can include other files:

% commented out as the file doesn't exist
% .. include:: ../README.rst
%    :start-line: 10
%    :end-line: 20

(quickstart-summary)=

## Summary

You've now learned the basics of:

1. Installation and configuration
2. Basic document operations
3. Various text formatting options
4. Code blocks and examples
5. Tables and lists
6. Cross-references and links
7. Admonitions and notes

(quickstart-next-steps)=

### Next Steps

- Try the {doc}`advanced` guide for more features
- Explore the {doc}`api/reference` for detailed API documentation
- Join our community forum for support

______________________________________________________________________

*Last updated: January 2024*

:::{admonition} MyST-Specific Features in This Document
:class: tip dropdown

This MyST version demonstrates several features unique to MyST:

- **Tab Sets**: See the Configuration section for tabbed content
- **Dropdown Admonitions**: This very box is collapsible!
- **Enhanced Cross-references**: `{doc}` and `{ref}` syntax
- **Substitutions**: Using {{ project }} and {{ version }} variables
- **Native Markdown**: Mix of Markdown and Sphinx directives
:::

