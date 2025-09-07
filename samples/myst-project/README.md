# MyST (Markedly Structured Text) Sample Project

This sample project demonstrates docdiff's support for MyST documentation.
It contains the same content as `samples/rest-project` but in MyST format,
showcasing both format conversion and MyST-specific features.

## Project Structure

```text
myst-project/
├── README.md          # This file
├── en/                # English documentation
│   ├── index.md      # Main page
│   ├── quickstart.md # Basic MyST features
│   ├── advanced.md   # Advanced features
│   ├── api/          # Nested structure
│   │   ├── index.md
│   │   └── reference.md
│   └── _static/      # Static files
│       └── diagram.png
└── ja/               # Japanese translations
    ├── index.md      # Partial translation
    └── quickstart.md # Full translation
```

## MyST vs reStructuredText

This project was converted from reStructuredText using `rst2myst` and then optimized
to showcase MyST-specific features.

### Key Differences

| Feature | reStructuredText | MyST |
|---------|-----------------|------|
| **Labels** | `.. _label:` | `(label)=` |
| **Cross-references** | `:ref:`label`` | `{ref}`label`` |
| **Code blocks** | `.. code-block:: python` | ` ```{code-block} python` |
| **Admonitions** | `.. note::` | `:::{note}` |
| **Tables** | Complex directive syntax | Markdown tables + `{list-table}` |
| **Math** | `.. math::` | `$` for inline, `$$` for block |

### MyST-Specific Features

This sample includes MyST features not available in standard reStructuredText:

1. **Tab Sets** (`{tab-set}`)
   - See `quickstart.md` Configuration section
   - Organize content in switchable tabs

2. **Dropdown Admonitions**
   - Collapsible content boxes
   - Custom titles and styling

3. **Markdown Compatibility**
   - Standard Markdown syntax works
   - Links: `[text](url)`
   - Images: `![alt](path)`

4. **Substitutions**
   - Define variables in frontmatter
   - Use with `{{ variable }}` syntax

5. **Enhanced Directives**
   - Simpler, more readable syntax
   - Better integration with Markdown

## Testing docdiff

### Parse the Project

```bash
# Parse the English documentation
docdiff parse samples/myst-project/en

# Parse the Japanese documentation
docdiff parse samples/myst-project/ja
```

### Compare Translations

```bash
# Compare English and Japanese versions
docdiff compare samples/myst-project/en samples/myst-project/ja

# Generate a detailed report
docdiff compare samples/myst-project/en samples/myst-project/ja \
    --output report.md
```

### Format Comparison

Compare MyST with reStructuredText version:

```bash
# Compare same content in different formats
docdiff compare samples/rest-project/en samples/myst-project/en

# This shows structural equivalence despite format differences
```

## Conversion from reStructuredText

This project was created by converting the reST version:

```bash
# Automated conversion
uvx --from "rst-to-myst[sphinx]" rst2myst stream input.rst > output.md

# Then optimized with:
# - Native MyST table syntax
# - Tab sets for configuration examples
# - Dropdown admonitions
# - Simplified cross-references
```

## Expected Results

The MySTParser should correctly identify:

1. **Sections**: All heading levels with proper hierarchy
2. **Code Blocks**: Both fence-style and directive-style
3. **Admonitions**: Various types with enhanced features
4. **Tables**: Markdown and list-table directives
5. **Cross-references**: MyST-style labels and references

### Translation Tracking

The comparison should show:

- Fully translated documents (`quickstart.md`)
- Partially translated documents (`index.md`)
- Missing translations (`advanced.md`, `api/*`)

## Benefits of MyST Format

1. **Familiar Syntax**: Markdown-based, easier for developers
2. **Rich Features**: Sphinx directives + Markdown extensions
3. **Better Tooling**: VSCode/IDE support for Markdown
4. **Jupyter Integration**: Works with Jupyter notebooks
5. **Extensible**: Custom roles and directives

## Notes

:::{note}
This sample project demonstrates that docdiff works equally well with
both MyST and reStructuredText formats, making it suitable for any
Sphinx-based documentation project.
:::

:::{tip}
Use the format that best suits your team's workflow:
- **reStructuredText**: More features, standard Sphinx format
- **MyST**: Easier to write, better developer experience
:::

## See Also

- [MyST Parser Documentation](https://myst-parser.readthedocs.io/)
- [MyST Syntax Guide](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html)
- [rst2myst Converter](https://github.com/executablebooks/rst-to-myst)
- `samples/rest-project/` - reStructuredText version