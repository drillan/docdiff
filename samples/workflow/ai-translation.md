# AI-Powered Translation Workflow Guide

This guide demonstrates the recommended workflow for using docdiff's AI translation features to achieve maximum efficiency and quality.

## Prerequisites

- docdiff installed and configured
- Source documentation in MyST or reStructuredText format
- Access to an AI translation service (OpenAI, Anthropic, etc.)

## Step 1: Initial Setup

### 1.1 Create Project Structure

```
project/
├── docs/
│   ├── en/          # English source documentation
│   │   ├── index.md
│   │   ├── guide.md
│   │   └── api.md
│   └── ja/          # Japanese translations (target)
│       └── index.md # Partial translations
├── .docdiff/        # docdiff configuration
│   ├── glossary.json
│   └── ai-config.yaml
└── docdiff.yaml     # Project configuration
```

### 1.2 Initialize Glossary

Create a glossary to ensure terminology consistency:

```bash
# Copy sample glossary as starting point
cp $(docdiff --sample-glossary) .docdiff/glossary.json

# Edit to add your project-specific terms
vi .docdiff/glossary.json
```

Key glossary principles:
- Mark product names with `"maintain_original": true`
- Provide translations for common technical terms
- Include aliases for variations (e.g., "API", "APIs", "api")
- Group terms by category for better organization

### 1.3 Configure AI Settings

```bash
# Copy sample configuration
cp $(docdiff --sample-config) .docdiff/ai-config.yaml

# Adjust settings for your needs
vi .docdiff/ai-config.yaml
```

Important settings to customize:
- `model.provider`: Your AI service provider
- `batching.target_size`: Based on your model's token limits
- `cost.daily_limit`: To control expenses
- `glossary.file`: Path to your glossary

## Step 2: Analyze Current State

### 2.1 Check Translation Coverage

```bash
# Get overview of translation status
docdiff compare docs/en docs/ja

# Generate detailed report
docdiff compare docs/en docs/ja \
  --output reports/coverage.md \
  --view stats
```

### 2.2 Identify Missing Translations

```bash
# List all missing translations
docdiff compare docs/en docs/ja \
  --view tree \
  --filter missing
```

## Step 3: Export for Translation

### 3.1 Basic Export (Quick Start)

```bash
# Simple export with defaults
docdiff export docs/en docs/ja translation.json --adaptive
```

### 3.2 Optimized Export (Recommended)

```bash
# Export with full optimization
docdiff export docs/en docs/ja \
  translation.json \
  --adaptive \
  --batch-size 1500 \
  --context-window 3 \
  --glossary .docdiff/glossary.json \
  --verbose
```

This will:
- Use adaptive batching for 95% efficiency
- Include context for better translation quality
- Apply glossary for terminology consistency
- Show optimization metrics

### 3.3 Review Export Quality

```bash
# Check the export file
jq '.metadata.statistics' translation.json

# View batch distribution
jq '.translation_batches | length' translation.json

# Check average batch size
jq '[.translation_batches[].estimated_tokens] | add/length' translation.json
```

Expected results:
- Batch count: 10-20x fewer than node count
- Average batch size: 1000-1500 tokens
- Batch efficiency: >80%

## Step 4: Translate Content

### 4.1 Prepare Translation Prompts

For each batch in the export file:

```python
import json

with open('translation.json', 'r') as f:
    data = json.load(f)

for batch in data['translation_batches']:
    # Extract batch content
    nodes = [data['document_hierarchy'].get_node_by_id(node_id) 
             for node_id in batch['node_ids']]
    
    # Create translation prompt
    prompt = create_translation_prompt(
        nodes=nodes,
        glossary=batch['shared_context']['glossary_terms'],
        context=batch['shared_context']
    )
    
    # Send to AI service
    translation = ai_service.translate(prompt)
    
    # Store results
    store_translation(batch['batch_id'], translation)
```

### 4.2 Use docdiff Translation Helper (Coming Soon)

```bash
# Automated translation with configured AI service
docdiff translate translation.json \
  --output translated.json \
  --provider openai \
  --model gpt-4
```

## Step 5: Import Translations

### 5.1 Validate Translations

```bash
# Check translation file integrity
docdiff validate translated.json \
  --source docs/en \
  --check-references \
  --check-glossary
```

### 5.2 Import to Target Directory

```bash
# Import with backup
docdiff import translated.json \
  --source-dir docs/en \
  --target-dir docs/ja \
  --backup \
  --verbose
```

### 5.3 Verify Results

```bash
# Check new coverage
docdiff compare docs/en docs/ja

# Generate comparison report
docdiff compare docs/en docs/ja \
  --output reports/post-translation.md \
  --view side-by-side
```

## Step 6: Quality Assurance

### 6.1 Run Quality Checks

```bash
# Check translation quality metrics
docdiff quality translated.json \
  --glossary .docdiff/glossary.json \
  --output reports/quality.md
```

Quality metrics include:
- Terminology consistency
- Reference preservation
- Format integrity
- Completeness

### 6.2 Review Problem Areas

```bash
# Find inconsistencies
docdiff lint docs/ja \
  --check-glossary \
  --check-references \
  --check-formatting
```

## Step 7: Iterative Improvement

### 7.1 Update Glossary

Based on translation results, update your glossary:

```bash
# Extract new terms from translations
docdiff glossary extract \
  --source docs/en \
  --target docs/ja \
  --output new-terms.json

# Merge with existing glossary
docdiff glossary merge \
  .docdiff/glossary.json \
  new-terms.json \
  --output .docdiff/glossary.json
```

### 7.2 Retranslate Problem Areas

```bash
# Export only outdated translations
docdiff export docs/en docs/ja \
  updates.json \
  --filter outdated \
  --adaptive \
  --glossary .docdiff/glossary.json
```

## Best Practices

### Batch Size Optimization

Choose batch size based on your AI model:

| Model | Recommended Batch Size | Max Batch Size |
|-------|------------------------|----------------|
| GPT-4 | 1500 tokens | 2000 tokens |
| Claude-3 | 2000 tokens | 3000 tokens |
| Gemini Pro | 1800 tokens | 2500 tokens |

### Glossary Management

1. **Start Small**: Begin with 20-30 essential terms
2. **Iterate**: Add terms as you discover inconsistencies
3. **Categorize**: Group related terms for better organization
4. **Review Regularly**: Update translations based on feedback

### Cost Optimization

1. **Use Adaptive Batching**: Reduces API calls by 90%
2. **Cache Translations**: Reuse previous translations
3. **Incremental Updates**: Only translate changes
4. **Set Limits**: Configure daily token limits

### Quality Assurance

1. **Always Use Glossary**: Ensures consistency
2. **Include Context**: Improves translation accuracy
3. **Validate References**: Check cross-references work
4. **Review Metrics**: Monitor quality scores

## Troubleshooting

### Problem: Low Batch Efficiency

```bash
# Check current efficiency
docdiff export docs/en docs/ja test.json --adaptive --verbose

# If efficiency < 60%, try:
docdiff export docs/en docs/ja test.json \
  --adaptive \
  --batch-size 2000 \
  --min-batch-size 800
```

### Problem: Terminology Inconsistencies

```bash
# Analyze term usage
docdiff glossary analyze docs/ja --glossary .docdiff/glossary.json

# Update glossary with findings
docdiff glossary update .docdiff/glossary.json --interactive
```

### Problem: High Translation Costs

```bash
# Enable all optimizations
docdiff export docs/en docs/ja optimized.json \
  --adaptive \
  --cache \
  --differential \
  --max-tokens 1500
```

## Advanced Features

### Parallel Processing

For large projects, use parallel batch processing:

```bash
# Export with parallel batch preparation
docdiff export docs/en docs/ja \
  large-project.json \
  --adaptive \
  --parallel 5 \
  --progress
```

### Custom Prompts

For specialized domains, customize translation prompts:

```yaml
# In ai-config.yaml
advanced:
  prompts:
    system_prompt: |
      You are a technical documentation translator specializing in 
      cloud computing. Maintain technical accuracy while ensuring
      natural language flow.
```

### Differential Translation

Only translate what has changed:

```bash
# Export only changes since last translation
docdiff export docs/en docs/ja \
  changes.json \
  --since "2024-01-01" \
  --adaptive
```

## Conclusion

By following this workflow, you can achieve:
- **90% reduction** in translation API costs
- **95% batch efficiency** for optimal token usage
- **Consistent terminology** across all documents
- **High-quality translations** with context awareness

For more information, see the [full documentation](https://docdiff.readthedocs.io/).