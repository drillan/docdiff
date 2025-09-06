# docdiff Sample Outputs

This directory contains sample outputs from the docdiff tool, demonstrating various view modes, report formats, and export options.

## Directory Structure

```
samples/
├── views/       # Terminal view outputs
├── reports/     # Markdown report formats
└── exports/     # Export file formats
```

## Views

Terminal-based visualization modes for interactive exploration:

- **[summary.txt](views/summary.txt)** - Default view showing translation coverage statistics
- **[side-by-side.txt](views/side-by-side.txt)** - Parallel comparison of source and target content

## Reports

Markdown-formatted reports for documentation and tracking:

- **[report-detailed.md](reports/report-detailed.md)** - Comprehensive report with all sections
- **[report-github.md](reports/report-github.md)** - GitHub-flavored markdown with collapsible sections
- **[report-compact.md](reports/report-compact.md)** - Minimal report focusing on critical information

## Exports

Machine-readable formats for translation workflows:

- **[tasks.csv](exports/tasks.csv)** - CSV format for spreadsheet tools
- **[tasks.json](exports/tasks.json)** - JSON format for programmatic processing

## Generated From

These samples were generated from the actual docdiff documentation:
- Source: `docs/en/` (English documentation)
- Target: `docs/ja/` (Japanese documentation)
- Translation Coverage: 8.3%

## Usage Examples

### Generate a summary view
```bash
docdiff compare docs/en docs/ja --view summary
```

### Create a detailed report
```bash
docdiff compare docs/en docs/ja --output report.md
```

### Export for translation
```bash
docdiff export docs/en docs/ja tasks.csv --format csv
```

### Import completed translations
```bash
docdiff import tasks.csv --source-dir docs/en --target-dir docs/ja
```