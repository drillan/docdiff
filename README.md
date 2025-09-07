(readme-title)=
# 🔍 docdiff

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/translation-8.3%25-red)](samples/reports/report-detailed.md)

**Intelligent multilingual documentation comparison and translation management tool**

docdiff analyzes document structure to track translation progress, identify missing translations, and manage multilingual documentation efficiently.

(readme-key-features)=
## ✨ Key Features

(readme-translation-coverage)=
### 📊 Translation Coverage Analysis
Real-time translation coverage tracking with detailed metrics showing exactly which content needs translation.

[→ View Sample Report](samples/reports/report-detailed.md)

(readme-view-modes)=
### 🔄 Multiple View Modes
Choose from various visualization modes to understand your translation status:
- **Summary View**: Quick overview of translation coverage
- **Side-by-Side**: Parallel content comparison
- **Tree View**: Hierarchical document structure
- **Metadata View**: Group by labels and attributes
- **Stats View**: Detailed statistics

[→ See View Examples](samples/views/)

(readme-export-formats)=
### 📤 Flexible Export Formats
Export translation tasks in multiple formats for seamless integration with your workflow:
- **CSV**: For spreadsheet tools (Excel, Google Sheets)
- **JSON**: For programmatic processing
- **XLSX**: Rich Excel workbooks
- **XLIFF**: Industry-standard CAT tool format

[→ Browse Export Samples](samples/exports/)

(readme-content-matching)=
### 🎯 Smart Content Matching
- Label-based structural mapping
- Fuzzy content matching
- Metadata preservation
- Language-aware comparison

(readme-ai-translation)=
### 🤖 AI-Powered Translation Optimization
Revolutionary adaptive batching system that dramatically reduces translation costs:
- **95% Batch Efficiency**: Intelligent node merging optimizes token usage
- **90% Cost Reduction**: Fewer API calls mean lower translation expenses
- **Context-Aware Batching**: Maintains semantic relationships for better quality
- **Glossary Management**: Ensures terminology consistency across translations
- **Quality Metrics**: Real-time translation quality assessment

**Performance Comparison:**
```
Legacy System:  139 API calls, 2.2% efficiency  ❌
Adaptive System:  2 API calls, 95% efficiency   ✅
```

[→ Learn More About AI Features](docs/en/user-guide.md#ai-translation)

(readme-quick-start)=
## 🚀 Quick Start

(readme-installation)=
### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/docdiff.git
cd docdiff

# Install with uv (recommended)
uv sync
uv pip install -e .

# Verify installation
docdiff --version
```

(readme-basic-usage)=
### Basic Usage

```bash
# Compare documentation
docdiff compare docs/en docs/ja

# Generate detailed report
docdiff compare docs/en docs/ja --output report.md

# Export translation tasks (legacy mode)
docdiff export docs/en docs/ja tasks.csv --format csv

# Export with AI optimization (recommended)
docdiff export docs/en docs/ja tasks.json \
  --adaptive \
  --batch-size 2000 \
  --glossary glossary.json

# Import completed translations
docdiff import tasks.json --source-dir docs/en --target-dir docs/ja
```

(readme-output-examples)=
## 📸 Output Examples

(readme-coverage-summary)=
### Translation Coverage Summary
```
Translation Coverage Summary
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric               ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Overall Coverage     │  8.3% │
│ Total Nodes          │   432 │
│ Translated           │    36 │
│ Missing              │   396 │
└──────────────────────┴───────┘
```
[→ Full Summary](samples/views/summary.txt)

(readme-side-by-side)=
### Side-by-Side Comparison
View source and target content in parallel for easy review and validation.

[→ View Comparison](samples/views/side-by-side.txt)

(readme-markdown-reports)=
### Markdown Reports
Generate comprehensive reports in multiple styles:
- **[Detailed Report](samples/reports/report-detailed.md)** - Complete analysis with all sections
- **[GitHub Style](samples/reports/report-github.md)** - Collapsible sections and task lists
- **[Compact Report](samples/reports/report-compact.md)** - Essential information only

(readme-advanced-features)=
## 🔧 Advanced Features

(readme-metadata-processing)=
### Metadata-Aware Processing
docdiff understands document structure beyond plain text:
- Preserves labels (`(section-name)=`)
- Tracks `:name:` and `:caption:` attributes
- Maintains cross-references
- Respects MyST/reStructuredText directives

(readme-intelligent-comparison)=
### Intelligent Comparison
The comparison engine uses multi-pass matching:
1. **Structural matching** by labels and names
2. **Content comparison** to determine translation status
3. **Fuzzy matching** for similar content
4. **Position-based** fallback for unmarked content

(readme-cache-management)=
### Cache Management
Efficient caching system in `.docdiff/` directory:
- Parsed document structures
- Comparison results
- Generated reports

(readme-documentation)=
## 📚 Documentation

- **[User Guide](docs/en/user-guide.md)** - Detailed usage instructions
- **[CLI Reference](docs/en/cli-reference.md)** - Complete command reference
- **[Architecture](docs/en/architecture.md)** - System design and components
- **[API Reference](docs/en/api-reference.md)** - Programming interface
- **[Developer Guide](docs/en/developer-guide.md)** - Contributing and development

(readme-use-cases)=
## 🎯 Use Cases

(readme-technical-docs)=
### Technical Documentation
- API documentation
- Software manuals
- Developer guides
- README files

(readme-academic-writing)=
### Academic Writing
- Research papers
- Thesis documents
- Course materials

(readme-corporate-docs)=
### Corporate Documentation
- Product manuals
- Training materials
- Policy documents

(readme-roadmap)=
## 🗺️ Roadmap

- [ ] Machine translation integration
- [ ] Translation memory support
- [ ] Web-based UI
- [ ] Real-time collaboration
- [ ] Git hooks integration
- [ ] CI/CD pipeline support

(readme-contributing)=
## 🤝 Contributing

Contributions are welcome! Please read our [Developer Guide](docs/en/developer-guide.md) for details on:
- Setting up development environment
- Code style guidelines
- Testing requirements
- Pull request process

(readme-license)=
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

(readme-acknowledgments)=
## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Uses [Rich](https://rich.readthedocs.io/) for terminal formatting
- Powered by [myst-parser](https://myst-parser.readthedocs.io/) for document parsing

---

<p align="center">
  Made with ❤️ for documentation teams worldwide
</p>