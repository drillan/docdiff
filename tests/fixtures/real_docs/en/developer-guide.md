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
│       ├── cli.py              # CLI implementation (Typer)
│       ├── models.py            # Pydantic data models
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract parser interface
│       │   ├── myst.py         # MyST parser implementation
│       │   └── rest.py         # reStructuredText parser
│       ├── database.py          # SQLite database management
│       ├── analyzer.py          # Project analysis
│       └── translator.py        # Translation management
├── tests/
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_parser_myst.py
│   │   ├── test_parser_rest.py
│   │   └── test_database.py
│   ├── integration/             # Integration tests
│   │   └── test_parse_flow.py
│   └── fixtures/               # Test data
├── docs/
│   └── en/                     # English documentation
├── adr/                         # Architecture Decision Records
├── pyproject.toml              # Project configuration
└── CLAUDE.md                   # AI assistant instructions
```

(dev-testing-strategy)=
## Testing Strategy

(dev-running-tests)=
### Running Tests

Run all tests:
```{code-block} bash
:name: dev-code-run-all-tests
:caption: Run All Tests

uv run pytest
```

Run with coverage:
```{code-block} bash
:name: dev-code-run-with-coverage
:caption: Run Tests with Coverage

uv run pytest --cov=docdiff --cov-report=html
```

Run specific test categories:
```{code-block} bash
:name: dev-code-run-specific-tests
:caption: Run Specific Test Categories
:linenos:

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/
```

(dev-test-coverage-goals)=
### Test Coverage Goals

- **Overall Coverage**: 80% minimum
- **Core Logic**: 90% minimum
- **Error Handling**: 100% required

(dev-writing-tests)=
### Writing Tests

Example unit test:
```{code-block} python
:name: dev-code-unit-test-example
:caption: Unit Test Example
:linenos:

import pytest
from docdiff.models import DocumentNode, NodeType

def test_document_node_creation():
    node = DocumentNode(
        id="test123",
        type=NodeType.SECTION,
        content="Test Section",
        file_path="test.md",
        line_number=1
    )
    assert node.id == "test123"
    assert node.type == NodeType.SECTION
```

Example integration test:
```{code-block} python
:name: dev-code-integration-test-example
:caption: Integration Test Example
:linenos:

import pytest
from pathlib import Path
from docdiff.cli import parse_command

def test_parse_sphinx_project(tmp_path):
    # Create test project structure
    project_dir = tmp_path / "docs"
    project_dir.mkdir()
    (project_dir / "index.md").write_text("# Test")
    
    # Run parse command
    result = parse_command(str(project_dir))
    assert result.success
    assert result.nodes_count > 0
```

(dev-code-style-guidelines)=
## Code Style Guidelines

(dev-python-conventions)=
### Python Code Conventions

1. **Type Hints**: Always use type hints for function signatures
```{code-block} python
:name: dev-code-type-hints-example
:caption: Type Hints Example

def parse_document(file_path: Path) -> List[DocumentNode]:
    ...
```

2. **Docstrings**: Use Google-style docstrings
```{code-block} python
:name: dev-code-docstring-example
:caption: Docstring Example
:linenos:

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