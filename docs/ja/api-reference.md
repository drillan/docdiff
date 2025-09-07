(api-reference)=
# API参照

(api-data-models)=
## データモデル

(api-nodetype-enum)=
### NodeType 列挙型

ドキュメント構造要素のタイプを定義します：

```{code-block} python
:name: api-code-nodetype-enum
:caption: NodeType 列挙型の定義
:linenos:

class NodeType(str, Enum):
    SECTION = "section"        # セクション
    PARAGRAPH = "paragraph"    # 段落
    CODE_BLOCK = "code_block"  # コードブロック
    MATH_BLOCK = "math_block"  # 数式ブロック
    TABLE = "table"            # テーブル
    FIGURE = "figure"          # 図
    ADMONITION = "admonition"  # 注釈
    LIST = "list"              # リスト
    LIST_ITEM = "list_item"    # リスト項目
    DIRECTIVE = "directive"    # ディレクティブ
    TOC_TREE = "toc_tree"      # 目次ツリー
```

(api-document-node)=
### DocumentNode モデル

ドキュメント構造内の単一要素を表します：

```{code-block} python
:name: api-code-document-node
:caption: DocumentNode モデル
:linenos:

class DocumentNode(BaseModel):
    id: str                      # 一意ID（ハッシュベース）
    type: NodeType               # 要素タイプ
    content: str                 # テキストコンテンツ
    level: Optional[int]         # セクション階層レベル
    title: Optional[str]         # セクションタイトル
    label: Optional[str]         # 参照ラベル
    name: Optional[str]          # :name: 属性
    caption: Optional[str]       # :caption: 属性
    language: Optional[str]      # コードブロック言語
    parent_id: Optional[str]     # 親ノード参照
    children_ids: List[str]      # 子ノード参照
    file_path: Path              # ソースファイルパス
    line_number: int             # ソース内行番号
    metadata: Dict[str, Any]     # 追加メタデータ
```

(api-translation-unit)=
### TranslationUnit モデル

ドキュメント要素の翻訳データを管理します：

```{code-block} python
:name: api-code-translation-unit
:caption: TranslationUnit モデル
:linenos:

class TranslationUnit(BaseModel):
    node_id: str                           # DocumentNode への参照
    source_lang: str                       # ソース言語コード
    target_lang: str                       # ターゲット言語コード
    source_content: str                    # 元のコンテンツ
    translated_content: Optional[str]      # 翻訳されたコンテンツ
    status: TranslationStatus              # 翻訳ステータス
    content_hash: str                      # 変更検知用コンテンツハッシュ
    translation_date: Optional[datetime]   # 最終翻訳タイムスタンプ
```

(api-translation-status)=
### TranslationStatus 列挙型

翻訳の状態を追跡します：

```{code-block} python
:name: api-code-translation-status
:caption: TranslationStatus 列挙型
:linenos:

class TranslationStatus(str, Enum):
    PENDING = "pending"        # 未翻訳
    TRANSLATED = "translated"  # 翻訳完了
    REVIEWED = "reviewed"      # 翻訳レビュー済み
    OUTDATED = "outdated"      # ソースコンテンツが変更された
```

(api-ai-modules)=
## AI翻訳モジュール

(api-adaptive-batch-optimizer)=
### AdaptiveBatchOptimizer

AI翻訳のためのインテリジェントなバッチ最適化：

```{code-block} python
:name: api-code-adaptive-batch-optimizer
:caption: AdaptiveBatchOptimizer クラス
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
        """適応型バッチオプティマイザーを初期化します。
        
        Args:
            target_batch_size: バッチあたりの目標トークン数
            min_batch_size: 最小バッチサイズ
            max_batch_size: 最大バッチサイズ
            source_lang: ソース言語コード
            preserve_hierarchy: ドキュメント構造を維持
            enable_context: 周辺コンテキストを含める
            context_window: コンテキストノード数
        """
    
    def optimize_batches(
        self, nodes: List[TranslationNode]
    ) -> List[TranslationBatch]:
        """ノードを効率的なバッチに最適化します。"""
```

(api-token-estimator)=
### TokenEstimator

各種AIモデルのためのトークンカウントと推定：

```{code-block} python
:name: api-code-token-estimator
:caption: TokenEstimator クラス
:linenos:

class TokenEstimator:
    def estimate_tokens(
        self,
        text: str,
        model: str = "gpt-4",
        language: str = "en"
    ) -> int:
        """テキストのトークン数を推定します。
        
        Args:
            text: 入力テキスト
            model: AIモデル名
            language: 言語コード
            
        Returns:
            推定トークン数
        """
```

(api-context-manager)=
### ContextManager

より高品質な翻訳のための翻訳コンテキストを管理します：

```{code-block} python
:name: api-code-context-manager
:caption: ContextManager クラス
:linenos:

class ContextManager:
    def get_context(
        self,
        node_id: str,
        window_size: int = 3,
        include_hierarchy: bool = True
    ) -> Dict[str, Any]:
        """ノードの周辺コンテキストを取得します。
        
        Args:
            node_id: ターゲットノードID
            window_size: コンテキストウィンドウサイズ
            include_hierarchy: 親子関係のコンテキストを含める
            
        Returns:
            周辺ノードを含むコンテキスト辞書
        """
```

(api-sphinx-modules)=
## Sphinx統合モジュール

(api-glossary-extractor)=
### GlossaryExtractor

Sphinxドキュメントから用語集を抽出します：

```{code-block} python
:name: api-code-glossary-extractor
:caption: GlossaryExtractor クラス
:linenos:

class GlossaryExtractor:
    def extract_glossary(
        self,
        doc_path: Path,
        output_format: str = "yaml"
    ) -> Dict[str, Any]:
        """Sphinxドキュメントから用語集を抽出します。
        
        Args:
            doc_path: ドキュメントディレクトリ
            output_format: 出力形式（yaml/json/csv）
            
        Returns:
            用語集辞書
        """
```

(api-reference-tracker)=
### ReferenceTracker

Sphinxドキュメント内の相互参照を追跡します：

```{code-block} python
:name: api-code-reference-tracker
:caption: ReferenceTracker クラス
:linenos:

class ReferenceTracker:
    def track_references(
        self,
        nodes: List[DocumentNode]
    ) -> Dict[str, List[str]]:
        """すべての相互参照を追跡します。
        
        Args:
            nodes: 分析するドキュメントノード
            
        Returns:
            参照マップ（ソース → ターゲット）
        """
```

(api-export-schema)=
## エクスポートスキーマモデル

(api-translation-batch)=
### TranslationBatch

AI翻訳のための最適化されたバッチ：

```{code-block} python
:name: api-code-translation-batch
:caption: TranslationBatch モデル
:linenos:

class TranslationBatch(BaseModel):
    batch_id: int                         # バッチID
    estimated_tokens: int                 # 推定トークン数
    file_group: str                       # ファイルグループ
    section_range: str                    # セクション範囲
    node_ids: List[str]                   # ノードID一覧
    context: Optional[Dict[str, Any]]     # コンテキスト
```

(api-document-hierarchy)=
### DocumentHierarchy

ドキュメント構造の関係を維持します：

```{code-block} python
:name: api-code-document-hierarchy
:caption: DocumentHierarchy モデル
:linenos:

class DocumentHierarchy(BaseModel):
    root_nodes: List[str]                 # ルートノード
    parent_map: Dict[str, str]            # 親マップ
    children_map: Dict[str, List[str]]    # 子マップ
    depth_map: Dict[str, int]             # 深度マップ
```

(api-database-schema)=
## データベーススキーマ

(api-nodes-table)=
### Nodes テーブル

ドキュメントの構造要素を格納します：

```{code-block} sql
:name: api-code-nodes-table-schema
:caption: Nodes テーブルスキーマ
:linenos:

CREATE TABLE nodes (
    id TEXT PRIMARY KEY,                    -- 一意ID
    type TEXT NOT NULL,                     -- ノードタイプ
    content TEXT NOT NULL,                  -- コンテンツ
    level INTEGER,                          -- レベル
    title TEXT,                             -- タイトル
    label TEXT,                             -- ラベル
    name TEXT,                              -- 名前属性
    caption TEXT,                           -- キャプション
    language TEXT,                          -- 言語
    parent_id TEXT,                         -- 親ID
    children_ids TEXT,                      -- 子ID一覧
    file_path TEXT NOT NULL,                -- ファイルパス
    line_number INTEGER NOT NULL,           -- 行番号
    content_hash TEXT NOT NULL,             -- コンテンツハッシュ
    metadata JSON,                          -- メタデータ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 作成日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新日時
    FOREIGN KEY (parent_id) REFERENCES nodes(id) ON DELETE CASCADE
);
```

**インデックス:**
- `label` と `name`: 高速な参照解決
- `parent_id`: 効率的な階層トラバーサル
- `file_path`: ファイルベースの操作
- `content_hash`: 変更検知

(api-references-table)=
### References テーブル

相互参照関係を維持します：

```{code-block} sql
:name: api-code-references-table-schema
:caption: References テーブルスキーマ
:linenos:

CREATE TABLE references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自動増分ID
    source_node_id TEXT NOT NULL,          -- ソースノードID
    target_label TEXT NOT NULL,            -- ターゲットラベル
    ref_type TEXT NOT NULL,                -- 参照タイプ
    resolved_target_id TEXT,               -- 解決されたターゲットID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 作成日時
    FOREIGN KEY (source_node_id) REFERENCES nodes(id) ON DELETE CASCADE
);
```

**フィールド:**
- `source_node_id`: 参照を含むノード
- `target_label`: 参照されているラベル
- `ref_type`: 参照タイプ（例: 'ref', 'doc', 'numref'）
- `resolved_target_id`: 解決されたターゲットノードID（見つかった場合）

(api-translation-units-table)=
### Translation Units テーブル

翻訳ステータスとコンテンツを追跡します：

```{code-block} sql
:name: api-code-translation-units-schema
:caption: Translation Units テーブルスキーマ
:linenos:

CREATE TABLE translation_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,         -- 自動増分ID
    node_id TEXT NOT NULL,                        -- ノードID
    source_lang TEXT NOT NULL,                    -- ソース言語
    target_lang TEXT NOT NULL,                    -- ターゲット言語
    source_content TEXT NOT NULL,                 -- ソースコンテンツ
    translated_content TEXT,                      -- 翻訳コンテンツ
    status TEXT DEFAULT 'pending',               -- ステータス
    content_hash TEXT NOT NULL,                   -- コンテンツハッシュ
    translation_date TIMESTAMP,                  -- 翻訳日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 作成日時
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新日時
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE(node_id, source_lang, target_lang)
);
```

**インデックス:**
- `status`: 翻訳状態によるフィルタ
- `(node_id, source_lang, target_lang)`: 言語ペアの一意制約

(api-core-interfaces)=
## コアインターフェース

(api-comparison-engine)=
### ComparisonEngine

高度なドキュメント比較エンジン：

```{code-block} python
:name: api-code-comparison-engine
:caption: ComparisonEngine インターフェース
:linenos:

class ComparisonEngine:
    def compare(self, 
                source_nodes: List[DocumentNode],
                target_nodes: List[DocumentNode],
                source_lang: str = "en",
                target_lang: str = "ja") -> ComparisonResult:
        """ソースとターゲットのドキュメントノードを比較します。
        
        Returns:
            マッピングと統計を含むComparisonResult
        """
        pass
```

(api-cache-manager)=
### CacheManager

プロジェクトキャッシュ管理：

```{code-block} python
:name: api-code-cache-manager
:caption: CacheManager インターフェース
:linenos:

class CacheManager:
    def __init__(self, project_root: Optional[Path] = None):
        """キャッシュマネージャーを初期化します。
        
        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.base_dir = project_root / '.docdiff'
        self.cache_dir = self.base_dir / 'cache'
        self.reports_dir = self.base_dir / 'reports'
    
    def initialize(self) -> None:
        """キャッシュディレクトリ構造を作成します。"""
        pass
    
    def get_cache_db(self) -> Path:
        """キャッシュデータベースへのパスを取得します。"""
        return self.cache_dir / 'nodes.db'
```

(api-metadata-view)=
### MetadataView

リッチターミナル可視化：

```{code-block} python
:name: api-code-metadata-view
:caption: MetadataView インターフェース
:linenos:

class MetadataView:
    def __init__(self, console: Console):
        """Richコンソールで初期化します。"""
        self.console = console
    
    def display_tree_view(self, result: ComparisonResult) -> None:
        """階層ツリービューを表示します。"""
        pass
    
    def display_metadata_groups(self, result: ComparisonResult) -> None:
        """メタデータでグループ化して表示します。"""
        pass
    
    def display_side_by_side(self, result: ComparisonResult) -> None:
        """サイドバイサイド比較を表示します。"""
        pass
```

(api-comparison-models)=
## 比較モデル

(api-comparison-result)=
### ComparisonResult

ドキュメント比較の完全な結果を含みます：

```{code-block} python
:name: api-code-comparison-result
:caption: ComparisonResult モデル
:linenos:

class ComparisonResult(BaseModel):
    source_lang: str                    # ソース言語コード
    target_lang: str                    # ターゲット言語コード
    mappings: List[NodeMapping]         # すべてのノードマッピング
    coverage_stats: Dict[str, Any]      # カバレッジ統計
    structure_diff: Dict[str, Any]      # 構造の差分
    timestamp: datetime                 # 比較タイムスタンプ
    
    @property
    def overall_coverage(self) -> float:
        """全体的な翻訳カバレッジのパーセンテージを計算します。"""
        return self.coverage_stats['overall']
```

(api-node-mapping)=
### NodeMapping

ソースとターゲットノード間のマッピングを表します：

```{code-block} python
:name: api-code-node-mapping
:caption: NodeMapping モデル
:linenos:

class NodeMapping(BaseModel):
    source_node: DocumentNode           # ソースドキュメントノード
    target_node: Optional[DocumentNode] # ターゲットノード（存在する場合）
    mapping_type: str                   # 'exact', 'fuzzy', または 'missing'
    similarity: float                   # コンテンツ類似度スコア（0-1）
    metadata_match: bool                # メタデータが一致するかどうか
```

(api-reporter-classes)=
## レポータークラス

(api-markdown-reporter)=
### MarkdownReporter

比較結果からMarkdownレポートを生成します：

```{code-block} python
:name: api-code-markdown-reporter
:caption: MarkdownReporter クラス
:linenos:

class MarkdownReporter:
    def __init__(self, style: str = "detailed"):
        """レポートスタイルで初期化します。
        
        Args:
            style: 'detailed', 'github', または 'compact'
        """
        self.style = style
    
    def generate(self, 
                result: ComparisonResult, 
                include_badges: bool = False) -> str:
        """markdownレポートを生成します。
        
        Returns:
            フォーマットされたmarkdown文字列
        """
        pass
```

(api-usage-examples)=
## 使用例

(api-example-comparison)=
### ドキュメントの比較

```{code-block} python
:name: api-code-example-comparison
:caption: ドキュメント比較例
:linenos:

from docdiff.compare import ComparisonEngine
from docdiff.parsers import MySTParser
from pathlib import Path

# ドキュメントをパース
parser = MySTParser()
source_nodes = parser.parse("Hello\n## Section", Path("test.md"))
target_nodes = parser.parse("Bonjour\n## Section", Path("test.fr.md"))

# 比較
engine = ComparisonEngine()
result = engine.compare(source_nodes, target_nodes, "en", "fr")

print(f"カバレッジ: {result.coverage_stats['overall']:.1%}")
print(f"未翻訳: {result.coverage_stats['counts']['missing']}")
```

(api-example-export)=
### 翻訳タスクのエクスポート

```{code-block} python
:name: api-code-example-export
:caption: エクスポート例
:linenos:

from docdiff.workflow import Exporter
from docdiff.compare import ComparisonResult

exporter = Exporter()

# 異なる形式にエクスポート
exporter.export(result, Path("tasks.csv"), format="csv")
exporter.export(result, Path("tasks.xlsx"), format="xlsx")
exporter.export(result, Path("tasks.xlf"), format="xliff")
```

(api-example-import)=
### 翻訳のインポート

```{code-block} python
:name: api-code-example-import
:caption: インポート例
:linenos:

from docdiff.workflow import Importer

importer = Importer()

# CSVからインポート
result = importer.import_file(
    Path("translated.csv"),
    source_dir=Path("docs/en"),
    target_dir=Path("docs/ja")
)

print(f"{result['imported_count']} 件の翻訳をインポートしました")
```