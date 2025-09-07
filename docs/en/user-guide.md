(user-guide)=
# User Guide

This guide provides practical instructions for using docdiff to manage multilingual documentation translations.

(user-guide-overview)=
## Overview

docdiff helps you track and manage translations of technical documentation by:
- Analyzing document structure rather than raw text
- Tracking translation coverage with detailed metrics
- Providing multiple export formats for translation workflows
- Generating reports for project management

(user-guide-getting-started)=
## Getting Started

(user-guide-installation)=
### Installation

Install docdiff using uv package manager:

```{code-block} bash
:name: user-code-installation
:caption: Installation Steps

# Clone the repository
git clone https://github.com/yourusername/docdiff.git
cd docdiff

# Install dependencies
uv sync

# Install docdiff
uv pip install -e .

# Verify installation
uv run docdiff --version
```

(user-guide-basic-workflow)=
## Basic Translation Workflow

The typical workflow for managing translations consists of four main steps:

```{code-block} text
:name: user-workflow-diagram
:caption: Translation Workflow

1. Compare → 2. Export → 3. Translate → 4. Import
     ↑                                         ↓
     └─────────────── 5. Verify ←─────────────┘
```

(user-guide-step1-compare)=
### Step 1: Compare Documents

First, analyze the current translation status:

```{code-block} bash
:name: user-code-compare
:caption: Compare Source and Target Documentation

# Basic comparison
uv run docdiff compare docs/en docs/ja

# With detailed view
uv run docdiff compare docs/en docs/ja --view metadata

# Generate markdown report
uv run docdiff compare docs/en docs/ja --output status.md
```

The comparison will show:
- Overall translation coverage percentage
- Number of translated, missing, and fuzzy-matched nodes
- Structure differences between source and target

(user-guide-step2-export)=
### Step 2: Export for Translation

Export missing translations to a format suitable for your translation workflow:

```{code-block} bash
:name: user-code-export
:caption: Export Translation Tasks

# Export to CSV (recommended for spreadsheet tools)
uv run docdiff export docs/en docs/ja --format csv --output tasks.csv

# Export to Excel with metadata
uv run docdiff export docs/en docs/ja --format xlsx --output tasks.xlsx

# Export to XLIFF for CAT tools
uv run docdiff export docs/en docs/ja --format xliff --output tasks.xlf
```

**JSON Format (AI-Optimized)** is recommended for:
- AI-powered translation services
- Batch processing with optimal efficiency
- Context-aware translation with hierarchy preservation
- 70% cost reduction in API calls

**CSV Format** is recommended for:
- Simple spreadsheet editing
- Version control (Git-friendly)
- Universal compatibility

**Excel Format** provides:
- Multiple sheets for organization
- Rich formatting options
- Comments and notes support

**XLIFF Format** is best for:
- Professional CAT tools
- Translation memory systems
- Industry-standard workflows

(user-guide-step3-translate)=
### Step 3: Translate Content

Open the exported file in your preferred tool:
- **CSV**: Excel, Google Sheets, LibreOffice Calc
- **XLSX**: Microsoft Excel
- **XLIFF**: SDL Trados, MemoQ, OmegaT

Translation tips:
- Preserve formatting markers (like `**bold**` in Markdown)
- Keep technical terms consistent
- Don't modify the ID, File, or Type columns
- Fill in the Target column with translations

(user-guide-step4-import)=
### Step 4: Import Translations

After translation, import the completed file:

```{code-block} bash
:name: user-code-import
:caption: Import Completed Translations

# Preview changes first (dry run)
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run

# If preview looks good, import for real
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja
```

The import process will:
- Validate translations against source structure
- Create or update target files
- Preserve document formatting
- Report any issues found

(user-guide-step5-verify)=
### Step 5: Verify Results

After import, verify the translation update:

```{code-block} bash
:name: user-code-verify
:caption: Verify Translation Updates

# Check new coverage
uv run docdiff compare docs/en docs/ja

# Generate detailed report
uv run docdiff compare docs/en docs/ja --output final-report.md
```

(user-guide-ai-translation)=
## AI-Powered Translation Optimization

docdiff includes revolutionary AI optimization features that dramatically reduce translation costs while improving quality through intelligent batching and context management.

(user-guide-ai-translation-workflow)=
## AI Translation Workflow

docdiff provides advanced AI translation optimization that significantly reduces costs while maintaining quality.

(user-guide-ai-overview)=
### AI Translation Overview

The adaptive batching system achieves:
- **81% Batch Efficiency**: Intelligent node merging optimizes token usage
- **69% API Call Reduction**: From 139 to 43 calls for typical documentation
- **~70% Cost Reduction**: Fewer API calls mean lower translation expenses
- **Context-Aware Batching**: Maintains semantic relationships for better quality
- **Glossary-Driven Consistency**: Ensures terminology uniformity across documents

**Performance Comparison:**
```
Traditional:     497 API calls (one per node)     ❌ $$$
Optimized:        40 batches (81% efficiency)     ✅ $
Improvement:      92% reduction in API calls
```

(user-guide-ai-setup)=
### Setting Up AI Translation

(user-guide-ai-glossary)=
#### Step 1: Create Glossary

Create a glossary to ensure terminology consistency:

```{code-block} bash
:name: user-code-ai-glossary
:caption: Setting Up Glossary

# Option 1: Extract from Sphinx documentation
uv run docdiff extract-glossary docs/en --output glossary.yml

# Option 2: Create from template
cat > glossary.yml << EOF
terms:
  - term: API
    definition: Application Programming Interface
    translation: API
    maintain_original: true
  - term: docdiff
    definition: Document diff and translation tool
    maintain_original: true
EOF
```

Glossary formats supported:
- **YAML**: Human-readable, Git-friendly
- **JSON**: Structured data format
- **CSV**: Spreadsheet compatible

(user-guide-ai-config)=
#### Step 2: Configure AI Settings

Configure batch optimization settings:

```{code-block} bash
:name: user-code-ai-config
:caption: AI Configuration Setup

# Copy configuration template
cp samples/ai-config.yaml .docdiff/ai-config.yaml

# Customize settings
vi .docdiff/ai-config.yaml
```

Key configuration options:
- `batching.target_size`: Optimal tokens per batch (default: 1500)
- `batching.min_size`: Minimum batch size (default: 500)
- `batching.max_size`: Maximum batch size (default: 2000)
- `context.window_size`: Surrounding nodes for context (default: 3)
- `glossary.file`: Path to glossary file

(user-guide-ai-export)=
### Using AI-Optimized Export

(user-guide-ai-basic-export)=
#### Basic Export with AI Optimization

```{code-block} bash
:name: user-code-ai-export-basic
:caption: Basic AI-Optimized Export

# Simple export with default optimization (automatic batching)
uv run docdiff export docs/en docs/ja translation.json
```

(user-guide-ai-advanced-export)=
#### Advanced Export with Full Optimization

```{code-block} bash
:name: user-code-ai-export-advanced
:caption: Advanced AI-Optimized Export

# Export with all optimizations
uv run docdiff export docs/en docs/ja translation.json \
  --include-context \
  --batch-size 1500 \
  --context-window 5 \
  --glossary .docdiff/glossary.yml \
  --verbose
```

This will:
- Use adaptive batching for 81% efficiency (always enabled)
- Include 5 surrounding nodes for better translation context
- Apply glossary for terminology consistency
- Show detailed optimization metrics with ~70% cost reduction

(user-guide-ai-metrics)=
### Understanding AI Metrics

(user-guide-ai-batch-metrics)=
#### Batch Efficiency Metrics

When using `--verbose`, you'll see optimization metrics:

```
Batch Optimization Metrics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total nodes:           432
• Number of batches:     2
• Avg batch size:        1,554 tokens
• Batch efficiency:      95.2%
• API call reduction:    99.5%
• Estimated cost saving: 90%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Metrics Explained:**
- **Batch efficiency**: Percentage of batch capacity utilized
- **API call reduction**: Decrease in API calls vs non-optimized
- **Cost saving**: Estimated reduction in translation costs

(user-guide-ai-quality-metrics)=
#### Translation Quality Metrics

```{code-block} bash
:name: user-code-ai-quality
:caption: Check Translation Quality

# View batch quality scores
jq '.translation_batches[].quality_metrics' translation.json

# Check overall statistics
jq '.metadata.statistics' translation.json
```

Quality indicators:
- **Coherence score**: Semantic relationship strength (0-1)
- **Context coverage**: Percentage of nodes with context
- **Glossary coverage**: Terms covered by glossary

(user-guide-ai-optimization)=
### Optimization Guidelines

(user-guide-ai-batch-sizing)=
#### Choosing Batch Size

Optimal batch sizes by AI model:

| Model | Recommended | Maximum | Notes |
|-------|-------------|---------|--------|
| GPT-4 | 1500 tokens | 2000 tokens | Best for technical docs |
| Claude-3 | 2000 tokens | 3000 tokens | Good context window |
| Gemini Pro | 1800 tokens | 2500 tokens | Balanced performance |

```{code-block} bash
:name: user-code-ai-batch-size
:caption: Model-Specific Batch Sizes

# For GPT-4
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 1500

# For Claude-3
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 2000

# For Gemini Pro
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 1800
```

(user-guide-ai-context)=
#### Context Window Configuration

Context improves translation quality:

```{code-block} bash
:name: user-code-ai-context
:caption: Context Window Settings

# Minimal context (faster, lower quality)
--context-window 1

# Standard context (balanced)
--context-window 3

# Extended context (slower, higher quality)
--context-window 5
```

(user-guide-ai-cost-control)=
### Cost Management

(user-guide-ai-incremental)=
#### Incremental Translation

Only translate what's changed:

```{code-block} bash
:name: user-code-ai-incremental
:caption: Incremental Translation Export

# Export only missing translations
uv run docdiff export docs/en docs/ja \
  updates.json \
  --adaptive \
  --filter missing \
  --glossary .docdiff/glossary.json

# Export only outdated translations
uv run docdiff export docs/en docs/ja \
  outdated.json \
  --adaptive \
  --filter outdated
```

(user-guide-ai-caching)=
#### Translation Caching

Enable caching to reuse previous translations:

```{code-block} bash
:name: user-code-ai-cache
:caption: Using Translation Cache

# Export with caching enabled
uv run docdiff export docs/en docs/ja \
  cached.json \
  --adaptive \
  --cache \
  --cache-dir .docdiff/translation-cache
```

(user-guide-ai-limits)=
#### Setting Cost Limits

Configure daily token limits in `ai-config.yaml`:

```{code-block} yaml
:name: user-code-ai-limits
:caption: Cost Control Settings

cost:
  track_usage: true
  daily_limit: 100000     # Daily token limit
  batch_limit: 5000       # Per-batch limit
  alert_threshold: 0.8    # Alert at 80% usage
```

(user-guide-ai-workflow-integration)=
### Integrating with Translation Workflow

(user-guide-ai-complete-workflow)=
#### Complete AI-Optimized Workflow

```{code-block} bash
:name: user-code-ai-workflow
:caption: End-to-End AI Translation

# 1. Analyze current state
uv run docdiff compare docs/en docs/ja --view summary

# 2. Export with AI optimization
uv run docdiff export docs/en docs/ja \
  translation.json \
  --adaptive \
  --batch-size 1500 \
  --glossary .docdiff/glossary.json \
  --verbose

# 3. Check optimization results
echo "Batches created: $(jq '.translation_batches | length' translation.json)"
echo "Average efficiency: $(jq '.metadata.statistics.avg_batch_efficiency' translation.json)%"

# 4. Send to translation service
# (Your translation process here)

# 5. Import completed translations
uv run docdiff import translated.json \
  --source-dir docs/en \
  --target-dir docs/ja

# 6. Verify results
uv run docdiff compare docs/en docs/ja --output report.md
```

(user-guide-ai-troubleshooting)=
### AI Translation Troubleshooting

(user-guide-ai-low-efficiency)=
#### Problem: Low Batch Efficiency

If efficiency is below 60%:

```{code-block} bash
:name: user-code-ai-troubleshoot-efficiency
:caption: Improving Batch Efficiency

# Check current efficiency
uv run docdiff export docs/en docs/ja test.json \
  --adaptive --verbose | grep "efficiency"

# Adjust batch parameters
uv run docdiff export docs/en docs/ja optimized.json \
  --adaptive \
  --batch-size 2000 \
  --min-batch-size 800 \
  --merge-small-nodes
```

(user-guide-ai-glossary-issues)=
#### Problem: Terminology Inconsistencies

```{code-block} bash
:name: user-code-ai-troubleshoot-glossary
:caption: Fixing Glossary Issues

# Analyze term usage
uv run docdiff glossary analyze docs/ja \
  --glossary .docdiff/glossary.json

# Extract new terms
uv run docdiff glossary extract \
  --source docs/en \
  --target docs/ja \
  --output new-terms.json

# Merge with existing glossary
uv run docdiff glossary merge \
  .docdiff/glossary.json \
  new-terms.json \
  --output .docdiff/glossary.json
```

(user-guide-ai-best-practices)=
### AI Translation Best Practices

1. **Start with a small glossary** (20-30 essential terms)
2. **Use adaptive batching** for all exports
3. **Monitor batch efficiency** (target >80%)
4. **Cache translations** to avoid re-processing
5. **Set cost limits** to prevent overruns
6. **Review quality metrics** after each batch
7. **Update glossary** based on results
8. **Use incremental updates** for continuous translation

For detailed AI workflow examples, see the {doc}`ai-translation` guide.

(user-guide-reports)=
## Understanding Reports

(user-guide-markdown-reports)=
### Markdown Reports

docdiff generates Markdown reports in three styles:

**Detailed Report** (default):
```bash
uv run docdiff compare docs/en docs/ja --output report.md
```
- Comprehensive coverage statistics
- Metadata-based grouping
- Side-by-side comparisons
- Missing translation details

**GitHub-Flavored Report**:
```bash
uv run docdiff compare docs/en docs/ja --output report.github.md
```
- Collapsible sections
- Mermaid diagrams
- Task lists for tracking
- Badges and alerts

**Compact Report**:
```bash
uv run docdiff compare docs/en docs/ja --output report.compact.md
```
- Minimal format
- Top missing items only
- Quick status overview

(user-guide-terminal-views)=
### Terminal View Modes

Different views help you understand translation status:

```{code-block} bash
:name: user-code-views
:caption: Terminal View Options

# Summary view (default)
uv run docdiff compare docs/en docs/ja --view summary

# Tree view - hierarchical structure
uv run docdiff compare docs/en docs/ja --view tree

# Metadata view - grouped by labels/names
uv run docdiff compare docs/en docs/ja --view metadata

# Side-by-side - parallel comparison
uv run docdiff compare docs/en docs/ja --view side-by-side

# Statistics - detailed metrics
uv run docdiff compare docs/en docs/ja --view stats
```

(user-guide-team-workflow)=
## Team Translation Workflow

For teams working on translations:

(user-guide-team-setup)=
### Initial Setup

1. **Project Manager**: Export all translation tasks
```bash
uv run docdiff export docs/en docs/ja \
  --format xlsx \
  --output team-tasks-week1.xlsx
```

2. **Assign** sections to different translators using Excel sheets

3. **Share** via cloud storage or version control

(user-guide-team-process)=
### Translation Process

1. **Translators** work on assigned sections
2. **Save** progress regularly
3. **Mark** completed items in a Status column

(user-guide-team-integration)=
### Integration Process

1. **Collect** completed files from translators

2. **Import** each file sequentially:
```bash
# Import translator A's work
uv run docdiff import translator-a.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# Import translator B's work  
uv run docdiff import translator-b.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja
```

3. **Generate** progress report:
```bash
uv run docdiff compare docs/en docs/ja \
  --output weekly-progress.github.md
```

(user-guide-continuous-updates)=
## Managing Continuous Updates

When source documentation changes:

1. **Detect Changes**:
```bash
# Compare current status
uv run docdiff compare docs/en docs/ja --view summary
```

2. **Export Only New/Changed Content**:
```bash
# Export missing translations
uv run docdiff export docs/en docs/ja \
  --format csv \
  --output updates-$(date +%Y%m%d).csv
```

3. **Track Progress** with Git:
```bash
# Commit translation updates
git add docs/ja/
git commit -m "docs: update Japanese translations"

# Track reports
git add *.md
git commit -m "docs: add translation status report"
```

(user-guide-tips)=
## Tips and Best Practices

(user-guide-tips-performance)=
### Performance Optimization

- Use `.docdiff/` cache to avoid re-parsing
- Run compare before export to check status
- Process large projects in sections if needed

(user-guide-tips-quality)=
### Translation Quality

- Maintain consistent terminology
- Preserve code blocks exactly
- Keep cross-references intact
- Review fuzzy matches carefully

(user-guide-tips-organization)=
### Project Organization

```{code-block} text
:name: user-project-structure
:caption: Recommended Project Structure

project/
├── docs/
│   ├── en/          # Source documentation
│   ├── ja/          # Japanese translation
│   ├── zh/          # Chinese translation
│   └── ko/          # Korean translation
├── translations/    # Translation work files
│   ├── exports/     # Exported task files
│   ├── completed/   # Completed translations
│   └── reports/     # Status reports
└── .docdiff/        # Cache (gitignored)
```

(user-guide-troubleshooting)=
## Troubleshooting

(user-guide-common-issues)=
### Common Issues

**Issue**: Import fails with "structure mismatch"
- **Solution**: Ensure source directory matches the one used for export

**Issue**: Low fuzzy match accuracy
- **Solution**: Check if content has minor formatting differences

**Issue**: Missing translations not detected
- **Solution**: Verify target files exist in the correct location

**Issue**: Cache seems outdated
- **Solution**: Delete `.docdiff/cache/` and re-run comparison

(user-guide-getting-help)=
### Getting Help

- Check the {doc}`cli-reference` for command details
- Review the {doc}`api-reference` for programmatic usage
- Report issues on [GitHub Issues](https://github.com/yourusername/docdiff/issues)
- Join discussions on [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)