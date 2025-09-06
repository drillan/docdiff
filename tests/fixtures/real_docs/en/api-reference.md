(api-reference)=
# API Reference

(api-data-models)=
## Data Models

(api-nodetype-enum)=
### NodeType Enumeration

Defines the types of document structure elements:

```{code-block} python
:name: api-code-nodetype-enum
:caption: NodeType Enumeration Definition
:linenos:

class NodeType(str, Enum):
    SECTION = "section"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    MATH_BLOCK = "math_block"
    TABLE = "table"
    FIGURE = "figure"
    ADMONITION = "admonition"
    LIST = "list"
    LIST_ITEM = "list_item"
```

(api-document-node)=
### DocumentNode Model

Represents a single element in the document structure:

```{code-block} python
:name: api-code-document-node
:caption: DocumentNode Model
:linenos:

class DocumentNode(BaseModel):
    id: str                      # Unique ID (hash-based)
    type: NodeType               # Element type
    content: str                 # Text content
    level: Optional[int]         # Section hierarchy level
    title: Optional[str]         # Section title
    label: Optional[str]         # Reference label
    name: Optional[str]          # :name: attribute
    caption: Optional[str]       # :caption: attribute
    language: Optional[str]      # Code block language
    parent_id: Optional[str]     # Parent node reference
    children_ids: List[str]      # Child node references
    file_path: Path              # Source file path
    line_number: int             # Line number in source
    metadata: Dict[str, Any]     # Additional metadata
```

(api-translation-unit)=
### TranslationUnit Model

Manages translation data for document elements:

```{code-block} python
:name: api-code-translation-unit
:caption: TranslationUnit Model
:linenos:

class TranslationUnit(BaseModel):
    node_id: str                           # Reference to DocumentNode
    source_lang: str                       # Source language code
    target_lang: str                       # Target language code
    source_content: str                    # Original content
    translated_content: Optional[str]      # Translated content
    status: TranslationStatus              # Translation status
    content_hash: str                      # Content hash for change detection
    translation_date: Optional[datetime]   # Last translation timestamp
```

(api-translation-status)=
### TranslationStatus Enumeration

Tracks the state of translations:

```{code-block} python
:name: api-code-translation-status
:caption: TranslationStatus Enumeration
:linenos:

class TranslationStatus(str, Enum):
    PENDING = "pending"        # Not yet translated
    TRANSLATED = "translated"  # Translation complete
    REVIEWED = "reviewed"      # Translation reviewed
    OUTDATED = "outdated"      # Source content changed
```

(api-database-schema)=
## Database Schema

(api-nodes-table)=
### Nodes Table

Stores document structural elements:

```{code-block} sql
:name: api-code-nodes-table-schema
:caption: Nodes Table Schema
:linenos:

CREATE TABLE nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    level INTEGER,
    title TEXT,
    label TEXT,
    name TEXT,
    caption TEXT,
    language TEXT,
    parent_id TEXT,
    children_ids TEXT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES nodes(id) ON DELETE CASCADE
);
```

**Indexes:**
- `label` and `name`: Fast reference resolution
- `parent_id`: Efficient hierarchy traversal
- `file_path`: File-based operations
- `content_hash`: Change detection

(api-references-table)=
### References Table

Maintains cross-reference relationships:

```{code-block} sql
:name: api-code-references-table-schema
:caption: References Table Schema
:linenos:

CREATE TABLE references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id TEXT NOT NULL,
    target_label TEXT NOT NULL,
    ref_type TEXT NOT NULL,
    resolved_target_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_node_id) REFERENCES nodes(id) ON DELETE CASCADE
);
```

**Fields:**
- `source_node_id`: Node containing the reference
- `target_label`: Label being referenced
- `ref_type`: Type of reference (e.g., 'ref', 'doc', 'numref')
- `resolved_target_id`: Resolved target node ID (if found)

(api-translation-units-table)=
### Translation Units Table

Tracks translation status and content:

```{code-block} sql
:name: api-code-translation-units-schema
:caption: Translation Units Table Schema
:linenos:

CREATE TABLE translation_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    source_content TEXT NOT NULL,
    translated_content TEXT,
    status TEXT DEFAULT 'pending',
    content_hash TEXT NOT NULL,
    translation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE(node_id, source_lang, target_lang)
);
```

**Indexes:**
- `status`: Filter by translation state
- `(node_id, source_lang, target_lang)`: Unique constraint for language pairs

(api-core-interfaces)=
## Core Interfaces

(api-document-parser-abc)=
### DocumentParser (Abstract Base Class)

Base interface for all document parsers:

```{code-block} python
:name: api-code-document-parser-interface
:caption: DocumentParser Interface
:linenos:

class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> List[DocumentNode]:
        """Parse a document file and return structured nodes."""
        pass
    
    @abstractmethod
    def extract_references(self, nodes: List[DocumentNode]) -> List[Reference]:
        """Extract cross-references from document nodes."""
        pass
```

(api-structure-db)=
### StructureDB

Database management interface:

```{code-block} python
:name: api-code-structure-db-interface
:caption: StructureDB Interface
:linenos:

class StructureDB:
    def __init__(self, db_path: Path):
        """Initialize database connection."""
        
    def insert_node(self, node: DocumentNode) -> None:
        """Insert a document node."""
        
    def get_node(self, node_id: str) -> Optional[DocumentNode]:
        """Retrieve a node by ID."""
        
    def update_translation(self, unit: TranslationUnit) -> None:
        """Update translation unit status."""
        
    def get_pending_translations(self, lang_pair: Tuple[str, str]) -> List[TranslationUnit]:
        """Get all pending translations for a language pair."""
```

(api-project-analyzer)=
### ProjectAnalyzer

Sphinx project analysis interface:

```{code-block} python
:name: api-code-project-analyzer-interface
:caption: ProjectAnalyzer Interface
:linenos:

class ProjectAnalyzer:
    def __init__(self, project_dir: Path):
        """Initialize with project directory."""
        
    def load_config(self) -> Dict[str, Any]:
        """Load Sphinx configuration from conf.py."""
        
    def analyze_project(self) -> ProjectStructure:
        """Analyze entire project structure."""
        
    def get_toctree(self) -> TocTree:
        """Extract table of contents structure."""
```

(api-usage-examples)=
## Usage Examples

(api-example-parsing)=
### Parsing a Document

```{code-block} python
:name: api-code-example-parsing
:caption: Document Parsing Example
:linenos:

from docdiff.parsers import MySTParser
from pathlib import Path

parser = MySTParser()
nodes = parser.parse(Path("docs/index.md"))

for node in nodes:
    print(f"{node.type}: {node.title or node.content[:50]}")
```

(api-example-translations)=
### Managing Translations

```{code-block} python
:name: api-code-example-translations
:caption: Translation Management Example
:linenos:

from docdiff.database import StructureDB
from docdiff.models import TranslationStatus

db = StructureDB(Path(".docdiff/structure.db"))

# Get pending translations
pending = db.get_pending_translations(("en", "ja"))

# Update translation status
for unit in pending:
    unit.translated_content = translate(unit.source_content)
    unit.status = TranslationStatus.TRANSLATED
    db.update_translation(unit)
```

(api-example-analyzing)=
### Analyzing a Project

```{code-block} python
:name: api-code-example-analyzing
:caption: Project Analysis Example
:linenos:

from docdiff.analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer(Path("docs/"))
structure = analyzer.analyze_project()

print(f"Found {len(structure.files)} documentation files")
print(f"Total nodes: {structure.total_nodes}")
```