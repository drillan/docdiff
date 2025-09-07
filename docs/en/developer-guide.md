(developer-guide)=
# Developer Guide

(dev-environment-setup)=
## Development Environment Setup

(dev-prerequisites)=
### Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- Git

(dev-initial-setup)=
### Initial Setup

1. Clone the repository:
```{code-block} bash
:name: dev-code-clone-repository
:caption: Clone Repository
:linenos:

git clone https://github.com/yourusername/docdiff.git
cd docdiff
```

2. Install dependencies using uv:
```{code-block} bash
:name: dev-code-install-dependencies
:caption: Install Dependencies

uv sync
```

3. Install the package in development mode:
```{code-block} bash
:name: dev-code-install-development
:caption: Install in Development Mode

uv pip install -e .
```

4. Verify installation:
```{code-block} bash
:name: dev-code-verify-installation
:caption: Verify Installation

uv run docdiff --version

# Test a basic command
uv run docdiff compare docs/en docs/ja --view summary
```

(dev-project-structure)=
## Project Structure

```{code-block} text
:name: dev-code-project-structure
:caption: Project Directory Structure

docdiff/
├── src/
│   └── docdiff/
│       ├── __init__.py
│       ├── cli/                 # CLI commands
│       │   ├── __init__.py
│       │   ├── main.py         # Main CLI entry
│       │   ├── parse.py        # Parse command
│       │   ├── compare.py      # Compare command
│       │   ├── export.py       # Export command
│       │   └── import_.py      # Import command
│       ├── models.py            # Pydantic data models
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── myst.py         # MyST/Markdown parser
│       ├── cache/
│       │   ├── __init__.py
│       │   └── manager.py      # Cache management
│       ├── compare/
│       │   ├── __init__.py
│       │   ├── engine.py       # Comparison engine
│       │   ├── models.py       # Comparison models
│       │   ├── views.py        # Terminal views
│       │   └── reporters.py    # Markdown reporters
│       └── workflow/
│           ├── __init__.py
│           ├── exporter.py     # Multi-format export
│           └── importer.py     # Translation import
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── fixtures/               # Test data
├── docs/
│   ├── en/                     # English documentation
│   └── ja/                     # Japanese documentation
├── .docdiff/                    # Cache directory (gitignored)
│   ├── cache/                  # Parsed data cache
│   └── reports/                # Generated reports
├── pyproject.toml              # Project configuration
├── CLAUDE.md                   # AI assistant instructions
└── .claude/                    # Claude-specific configs
    └── commands/               # Custom commands
```

(dev-testing-strategy)=
## Testing Strategy

(dev-running-tests)=
### Running Tests

Run all tests:
```{code-block} bash
:name: dev-code-run-all-tests
:caption: Run All Tests

uv run pytest tests/
```

Run with coverage:
```{code-block} bash
:name: dev-code-run-with-coverage
:caption: Run Tests with Coverage

uv run pytest tests/ --cov=docdiff --cov-report=term-missing
```

Run specific test types:
```{code-block} bash
:name: dev-code-run-specific-tests
:caption: Run Specific Test Types

# Unit tests only
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# E2E tests
uv run pytest tests/e2e/
```

(dev-test-coverage-goals)=
### Test Coverage Goals

- Unit test coverage: > 80%
- Integration test coverage: Key workflows
- E2E test coverage: Main user journeys

(dev-writing-tests)=
### Writing Tests

Example unit test:
```{code-block} python
:name: dev-code-unit-test-example
:caption: Unit Test Example
:linenos:

import pytest
from docdiff.parsers import MySTParser
from pathlib import Path

def test_parse_basic_markdown():
    parser = MySTParser()
    content = "# Title\n\nParagraph"
    nodes = parser.parse(content, Path("test.md"))
    
    assert len(nodes) == 2
    assert nodes[0].type.value == "section"
    assert nodes[0].content == "# Title"
    assert nodes[1].type.value == "paragraph"
    assert nodes[1].content == "Paragraph"
```

(dev-ai-translation-optimization)=
## AI Translation Optimization

(dev-ai-batch-algorithm)=
### Batch Optimization Algorithm

The AdaptiveBatchOptimizer uses a sophisticated algorithm to achieve 81% batch efficiency:

```{code-block} python
:name: dev-code-batch-algorithm
:caption: Batch Optimization Algorithm
:linenos:

def optimize_batches(nodes: List[TranslationNode]) -> List[TranslationBatch]:
    """Optimize nodes into efficient batches.
    
    Algorithm:
    1. Sort nodes by file and position
    2. Merge adjacent small nodes
    3. Respect section boundaries
    4. Maintain semantic relationships
    5. Target 500-2000 tokens per batch
    """
    batches = []
    current_batch = []
    current_tokens = 0
    
    for node in nodes:
        node_tokens = estimate_tokens(node.content)
        
        # Check if adding would exceed max size
        if current_tokens + node_tokens > max_batch_size:
            if current_batch:
                batches.append(create_batch(current_batch))
            current_batch = [node]
            current_tokens = node_tokens
        else:
            current_batch.append(node)
            current_tokens += node_tokens
            
            # Check if we've reached optimal size
            if current_tokens >= target_batch_size:
                batches.append(create_batch(current_batch))
                current_batch = []
                current_tokens = 0
    
    return batches
```

(dev-ai-token-estimation)=
### Token Estimation

Accurate token counting for different languages and models:

```{code-block} python
:name: dev-code-token-estimation
:caption: Token Estimation Implementation
:linenos:

def estimate_tokens(text: str, language: str = "en") -> int:
    """Estimate token count for text.
    
    Factors:
    - English: ~4 characters per token
    - Japanese: ~2 characters per token
    - Code blocks: ~3 characters per token
    - Adjustments for specific models
    """
    if language == "ja":
        return len(text) // 2
    elif language == "zh":
        return len(text) // 2
    else:
        return len(text) // 4
```

(dev-ai-context-management)=
### Context Management

Including relevant context for better translation quality:

```{code-block} python
:name: dev-code-context-management
:caption: Context Management
:linenos:

def add_context(node: TranslationNode, window: int = 3) -> Dict:
    """Add surrounding context to node.
    
    Includes:
    - Previous N nodes
    - Following N nodes
    - Parent section
    - Related glossary terms
    """
    context = {
        "before": get_previous_nodes(node, window),
        "after": get_following_nodes(node, window),
        "parent": get_parent_section(node),
        "glossary": get_relevant_terms(node)
    }
    return context
```

(dev-ai-performance-metrics)=
### Performance Metrics

Key metrics to monitor:

- **Batch Efficiency**: Target 80%+ (actual/optimal tokens)
- **API Call Reduction**: Target 90%+ reduction
- **Token Overhead**: Target < 10%
- **Processing Speed**: > 1000 nodes/second

(dev-code-style-guidelines)=
## Code Style Guidelines

(dev-python-conventions)=
### Python Conventions

- Use Python 3.12+ features
- Type hints for all functions
- Docstrings for all public APIs
- Follow PEP 8 with ruff enforcement
- Zero tolerance for legacy code

(dev-quality-tools)=
### Quality Management Tools

```{code-block} bash
:name: dev-code-quality-check
:caption: Run Quality Checks
:linenos:

# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check . --fix

# Type checking
uv run mypy .

# All checks at once
uv run ruff format . && uv run ruff check . --fix && uv run mypy . && uv run pytest tests/
```

(dev-commit-guidelines)=
### Commit Guidelines

- Use conventional commits format
- Commit messages in English
- Reference issues when applicable

Examples:
```
feat: add CSV export format support
fix: correct fuzzy matching threshold
docs: update CLI reference for compare command
refactor: simplify comparison engine logic
test: add E2E tests for export/import workflow
```

(dev-breaking-changes)=
## Breaking Changes Policy

**Important**: docdiff follows a "breaking changes welcome" philosophy:

- No backward compatibility requirements
- No deprecation periods needed
- Always use the best available solution
- Refactor freely for better design
- Remove unused code immediately

This policy accelerates development and maintains code quality by avoiding technical debt.

(dev-contributing)=
## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks
5. Submit pull request

### Pull Request Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Quality checks pass (ruff, mypy, pytest)
- [ ] Commit messages follow conventions
- [ ] PR description explains changes

def extract_references(nodes: List[DocumentNode]) -> List[Reference]:
    """Extract cross-references from document nodes.
    
    Args:
        nodes: List of document nodes to process
        
    Returns:
        List of extracted references
        
    Raises:
        ParseError: If reference syntax is invalid
    """
```

3. **Comments**: Write comments in English
```{code-block} python
:name: dev-code-comment-example
:caption: Comment Example
:linenos:

# Calculate content hash for change detection
content_hash = hashlib.sha256(content.encode()).hexdigest()
```

(dev-data-validation)=
### Data Validation

Always use Pydantic models for data validation:
```{code-block} python
:name: dev-code-pydantic-validation
:caption: Pydantic Validation Example
:linenos:

from pydantic import BaseModel, validator

class TranslationUnit(BaseModel):
    source_content: str
    target_lang: str
    
    @validator('target_lang')
    def validate_language_code(cls, v):
        if len(v) != 2:
            raise ValueError('Language code must be 2 characters')
        return v.lower()
```

(dev-implementation-phases)=
## Implementation Phases

(dev-phase-1-mvp)=
### Phase 1: MVP (2 weeks)

Core functionality to be implemented:

1. **Project Structure Setup**
   - Initialize repository structure
   - Configure pyproject.toml
   - Set up development environment

2. **Pydantic Models**
   - DocumentNode
   - TranslationUnit
   - NodeType enumeration

3. **SQLite Database Management**
   - Schema creation
   - CRUD operations
   - Migration support

4. **Basic Parser Implementation**
   - MyST parser using myst-parser
   - reStructuredText parser using docutils
   - Common interface definition

5. **CLI Commands**
   - `parse` command
   - `status` command
   - Basic error handling

(dev-phase-2-enhancement)=
### Phase 2: Enhancement (1 week)

Additional features:

1. **Incremental Updates**
   - Change detection using content hashes
   - Efficient update strategies

2. **Advanced Error Handling**
   - Detailed error messages
   - Recovery mechanisms
   - Logging system

3. **Export Functionality**
   - JSON export
   - CSV export
   - Custom formats

4. **Comprehensive Testing**
   - Unit test coverage
   - Integration tests
   - Performance benchmarks

(dev-phase-3-future)=
### Phase 3: Future Extensions

Planned extensions:

1. **JupyterBook Support**
   - JSON format parsing
   - Notebook integration

2. **Translation API Integration**
   - OpenAI API
   - Claude API
   - Custom translation services

3. **Web UI**
   - REST API backend
   - React frontend
   - Real-time updates

4. **Plugin System**
   - Custom parser plugins
   - Translation service plugins
   - Export format plugins

(dev-database-migrations)=
## Database Migrations

(dev-creating-migrations)=
### Creating Migrations

When schema changes are needed:

```{code-block} python
:name: dev-code-migration-example
:caption: Migration Example
:linenos:

# migrations/001_add_review_status.py
def upgrade(db):
    db.execute("""
        ALTER TABLE translation_units 
        ADD COLUMN reviewer_id TEXT
    """)
    
def downgrade(db):
    # SQLite doesn't support DROP COLUMN
    # Need to recreate table
    pass
```

(dev-running-migrations)=
### Running Migrations

```{code-block} bash
:name: dev-code-run-migrations
:caption: Running Migrations
:linenos:

docdiff db upgrade
docdiff db downgrade --to 001
```

(dev-performance-optimization)=
## Performance Optimization

(dev-indexing-strategy)=
### Indexing Strategy

Critical indexes for performance:
- `nodes.label` - Reference resolution
- `nodes.parent_id` - Hierarchy traversal
- `nodes.file_path` - File operations
- `translation_units.status` - Status filtering

(dev-batch-operations)=
### Batch Operations

Process multiple files efficiently:
```{code-block} python
:name: dev-code-batch-operations
:caption: Batch Operations Example
:linenos:

async def parse_batch(files: List[Path]) -> List[DocumentNode]:
    tasks = [parse_file(f) for f in files]
    results = await asyncio.gather(*tasks)
    return flatten(results)
```

(dev-caching)=
### Caching

Implement caching for expensive operations:
```{code-block} python
:name: dev-code-caching-example
:caption: Caching Example
:linenos:

from functools import lru_cache

@lru_cache(maxsize=128)
def resolve_reference(label: str) -> Optional[str]:
    # Expensive database lookup
    return db.find_node_by_label(label)
```

(dev-debugging-tips)=
## Debugging Tips

(dev-enable-debug-logging)=
### Enable Debug Logging

```{code-block} bash
:name: dev-code-debug-logging
:caption: Enable Debug Logging
:linenos:

export DOCDIFF_LOG_LEVEL=DEBUG
docdiff parse docs/
```

(dev-database-inspection)=
### Database Inspection

```{code-block} bash
:name: dev-code-database-inspection
:caption: Database Inspection
:linenos:

# Open SQLite database
sqlite3 .docdiff/structure.db

# Useful queries
.tables
.schema nodes
SELECT type, COUNT(*) FROM nodes GROUP BY type;
```

(dev-parser-debugging)=
### Parser Debugging

```{code-block} python
:name: dev-code-parser-debugging
:caption: Parser Debugging
:linenos:

# Enable AST printing
from docdiff.parsers import MySTParser

parser = MySTParser(debug=True)
nodes = parser.parse(Path("test.md"))
# Will print AST structure
```

(dev-contributing-guidelines)=
## Contributing Guidelines

(dev-pull-request-process)=
### Pull Request Process

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description

(dev-commit-message-format)=
### Commit Message Format

```{code-block} text
:name: dev-code-commit-message
:caption: Commit Message Format

feat: Add support for JupyterBook format

- Implement JSON parser
- Add notebook cell extraction
- Update CLI commands

Closes #123
```

(dev-code-review-checklist)=
### Code Review Checklist

- [ ] Type hints present
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considered
- [ ] Error handling complete