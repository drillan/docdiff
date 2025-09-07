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
    DIRECTIVE = "directive"
    TOC_TREE = "toc_tree"
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

(api-ai-modules)=
## AI Translation Modules

(api-adaptive-batch-optimizer)=
### AdaptiveBatchOptimizer

Intelligent batch optimization for AI translation:

```{code-block} python
:name: api-code-adaptive-batch-optimizer
:caption: AdaptiveBatchOptimizer Class
:linenos:

class AdaptiveBatchOptimizer:
    def __init__(
        self,
        target_batch_size: int = 1500,
        min_batch_size: int = 500,
        max_batch_size: int = 2000,
        source_lang: str = "en",
        preserve_hierarchy: bool = True,
        enable_context: bool = True,
        context_window: int = 3,
    ):
        """Initialize adaptive batch optimizer.
        
        Args:
            target_batch_size: Target tokens per batch
            min_batch_size: Minimum batch size
            max_batch_size: Maximum batch size
            source_lang: Source language code
            preserve_hierarchy: Maintain document structure
            enable_context: Include surrounding context
            context_window: Number of context nodes
        """
    
    def optimize_batches(
        self, nodes: List[TranslationNode]
    ) -> List[TranslationBatch]:
        """Optimize nodes into efficient batches."""
```

(api-token-estimator)=
### TokenEstimator

Token counting and estimation for various AI models:

```{code-block} python
:name: api-code-token-estimator
:caption: TokenEstimator Class
:linenos:

class TokenEstimator:
    def estimate_tokens(
        self,
        text: str,
        model: str = "gpt-4",
        language: str = "en"
    ) -> int:
        """Estimate token count for text.
        
        Args:
            text: Input text
            model: AI model name
            language: Language code
            
        Returns:
            Estimated token count
        """
```

(api-context-manager)=
### ContextManager

Manages translation context for better quality:

```{code-block} python
:name: api-code-context-manager
:caption: ContextManager Class
:linenos:

class ContextManager:
    def get_context(
        self,
        node_id: str,
        window_size: int = 3,
        include_hierarchy: bool = True
    ) -> Dict[str, Any]:
        """Get surrounding context for a node.
        
        Args:
            node_id: Target node ID
            window_size: Context window size
            include_hierarchy: Include parent/child context
            
        Returns:
            Context dictionary with surrounding nodes
        """
```

(api-sphinx-modules)=
## Sphinx Integration Modules

(api-glossary-extractor)=
### GlossaryExtractor

Extracts glossary terms from Sphinx documentation:

```{code-block} python
:name: api-code-glossary-extractor
:caption: GlossaryExtractor Class
:linenos:

class GlossaryExtractor:
    def extract_glossary(
        self,
        doc_path: Path,
        output_format: str = "yaml"
    ) -> Dict[str, Any]:
        """Extract glossary from Sphinx docs.
        
        Args:
            doc_path: Documentation directory
            output_format: Output format (yaml/json/csv)
            
        Returns:
            Glossary dictionary
        """
```

(api-reference-tracker)=
### ReferenceTracker

Tracks cross-references in Sphinx documentation:

```{code-block} python
:name: api-code-reference-tracker
:caption: ReferenceTracker Class
:linenos:

class ReferenceTracker:
    def track_references(
        self,
        nodes: List[DocumentNode]
    ) -> Dict[str, List[str]]:
        """Track all cross-references.
        
        Args:
            nodes: Document nodes to analyze
            
        Returns:
            Reference map (source -> targets)
        """
```

(api-export-schema)=
## Export Schema Models

(api-translation-batch)=
### TranslationBatch

Optimized batch for AI translation:

```{code-block} python
:name: api-code-translation-batch
:caption: TranslationBatch Model
:linenos:

class TranslationBatch(BaseModel):
    batch_id: int
    estimated_tokens: int
    file_group: str
    section_range: str
    node_ids: List[str]
    context: Optional[Dict[str, Any]]
```

(api-document-hierarchy)=
### DocumentHierarchy

Maintains document structure relationships:

```{code-block} python
:name: api-code-document-hierarchy
:caption: DocumentHierarchy Model
:linenos:

class DocumentHierarchy(BaseModel):
    root_nodes: List[str]
    parent_map: Dict[str, str]
    children_map: Dict[str, List[str]]
    depth_map: Dict[str, int]
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

(api-comparison-engine)=
### ComparisonEngine

Advanced document comparison engine:

```{code-block} python
:name: api-code-comparison-engine
:caption: ComparisonEngine Interface
:linenos:

class ComparisonEngine:
    def compare(self, 
                source_nodes: List[DocumentNode],
                target_nodes: List[DocumentNode],
                source_lang: str = "en",
                target_lang: str = "ja") -> ComparisonResult:
        """Compare source and target document nodes.
        
        Returns:
            ComparisonResult with mappings and statistics
        """
        pass
```

(api-cache-manager)=
### CacheManager

Project cache management:

```{code-block} python
:name: api-code-cache-manager
:caption: CacheManager Interface
:linenos:

class CacheManager:
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize cache manager.
        
        Args:
            project_root: Project root directory
        """
        self.base_dir = project_root / '.docdiff'
        self.cache_dir = self.base_dir / 'cache'
        self.reports_dir = self.base_dir / 'reports'
    
    def initialize(self) -> None:
        """Create cache directory structure."""
        pass
    
    def get_cache_db(self) -> Path:
        """Get path to cache database."""
        return self.cache_dir / 'nodes.db'
```

(api-metadata-view)=
### MetadataView

Rich terminal visualization:

```{code-block} python
:name: api-code-metadata-view
:caption: MetadataView Interface
:linenos:

class MetadataView:
    def __init__(self, console: Console):
        """Initialize with Rich console."""
        self.console = console
    
    def display_tree_view(self, result: ComparisonResult) -> None:
        """Display hierarchical tree view."""
        pass
    
    def display_metadata_groups(self, result: ComparisonResult) -> None:
        """Display grouped by metadata."""
        pass
    
    def display_side_by_side(self, result: ComparisonResult) -> None:
        """Display side-by-side comparison."""
        pass
```

(api-comparison-models)=
## Comparison Models

(api-comparison-result)=
### ComparisonResult

Contains the complete result of document comparison:

```{code-block} python
:name: api-code-comparison-result
:caption: ComparisonResult Model
:linenos:

class ComparisonResult(BaseModel):
    source_lang: str                    # Source language code
    target_lang: str                    # Target language code
    mappings: List[NodeMapping]         # All node mappings
    coverage_stats: Dict[str, Any]      # Coverage statistics
    structure_diff: Dict[str, Any]      # Structure differences
    timestamp: datetime                 # Comparison timestamp
    
    @property
    def overall_coverage(self) -> float:
        """Calculate overall translation coverage percentage."""
        return self.coverage_stats['overall']
```

(api-node-mapping)=
### NodeMapping

Represents the mapping between source and target nodes:

```{code-block} python
:name: api-code-node-mapping
:caption: NodeMapping Model
:linenos:

class NodeMapping(BaseModel):
    source_node: DocumentNode           # Source document node
    target_node: Optional[DocumentNode] # Target node (if exists)
    mapping_type: str                   # 'exact', 'fuzzy', or 'missing'
    similarity: float                   # Content similarity score (0-1)
    metadata_match: bool                # Whether metadata matches
```

(api-reporter-classes)=
## Reporter Classes

(api-markdown-reporter)=
### MarkdownReporter

Generates Markdown reports from comparison results:

```{code-block} python
:name: api-code-markdown-reporter
:caption: MarkdownReporter Class
:linenos:

class MarkdownReporter:
    def __init__(self, style: str = "detailed"):
        """Initialize with report style.
        
        Args:
            style: 'detailed', 'github', or 'compact'
        """
        self.style = style
    
    def generate(self, 
                result: ComparisonResult, 
                include_badges: bool = False) -> str:
        """Generate markdown report.
        
        Returns:
            Formatted markdown string
        """
        pass
```

(api-usage-examples)=
## Usage Examples

(api-example-comparison)=
### Comparing Documents

```{code-block} python
:name: api-code-example-comparison
:caption: Document Comparison Example
:linenos:

from docdiff.compare import ComparisonEngine
from docdiff.parsers import MySTParser
from pathlib import Path

# Parse documents
parser = MySTParser()
source_nodes = parser.parse("Hello\n## Section", Path("test.md"))
target_nodes = parser.parse("Bonjour\n## Section", Path("test.fr.md"))

# Compare
engine = ComparisonEngine()
result = engine.compare(source_nodes, target_nodes, "en", "fr")

print(f"Coverage: {result.coverage_stats['overall']:.1%}")
print(f"Missing: {result.coverage_stats['counts']['missing']}")
```

(api-example-export)=
### Exporting Translation Tasks

```{code-block} python
:name: api-code-example-export
:caption: Export Example
:linenos:

from docdiff.workflow import Exporter
from docdiff.compare import ComparisonResult

exporter = Exporter()

# Export to different formats
exporter.export(result, Path("tasks.csv"), format="csv")
exporter.export(result, Path("tasks.xlsx"), format="xlsx")
exporter.export(result, Path("tasks.xlf"), format="xliff")
```

(api-example-import)=
### Importing Translations

```{code-block} python
:name: api-code-example-import
:caption: Import Example
:linenos:

from docdiff.workflow import Importer

importer = Importer()

# Import from CSV
result = importer.import_file(
    Path("translated.csv"),
    source_dir=Path("docs/en"),
    target_dir=Path("docs/ja")
)

print(f"Imported {result['imported_count']} translations")
```