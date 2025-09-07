(developer-guide)=
# 開発者ガイド

(dev-environment-setup)=
## 開発環境セットアップ

(dev-prerequisites)=
### 前提条件

- Python 3.12 以上
- uv (Python パッケージマネージャー)
- Git

(dev-initial-setup)=
### 初期セットアップ

1. リポジトリのクローン:
```{code-block} bash
:name: dev-code-clone-repository
:caption: リポジトリのクローン
:linenos:

git clone https://github.com/yourusername/docdiff.git
cd docdiff
```

2. uvを使って依存関係をインストール:
```{code-block} bash
:name: dev-code-install-dependencies
:caption: 依存関係のインストール

uv sync
```

3. パッケージを開発モードでインストール:
```{code-block} bash
:name: dev-code-install-development
:caption: 開発モードでのインストール

uv pip install -e .
```

4. インストールの確認:
```{code-block} bash
:name: dev-code-verify-installation
:caption: インストールの確認

uv run docdiff --version

# 基本コマンドのテスト
uv run docdiff compare docs/en docs/ja --view summary
```

(dev-project-structure)=
## プロジェクト構造

```{code-block} text
:name: dev-code-project-structure
:caption: プロジェクトディレクトリ構造

docdiff/
├── src/
│   └── docdiff/
│       ├── __init__.py
│       ├── cli/                 # CLIコマンド
│       │   ├── __init__.py
│       │   ├── main.py         # メインCLIエントリ
│       │   ├── parse.py        # parseコマンド
│       │   ├── compare.py      # compareコマンド
│       │   ├── export.py       # exportコマンド
│       │   └── import_.py      # importコマンド
│       ├── models.py            # Pydanticデータモデル
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── myst.py         # MyST/Markdownパーサー
│       ├── cache/
│       │   ├── __init__.py
│       │   └── manager.py      # キャッシュ管理
│       ├── compare/
│       │   ├── __init__.py
│       │   ├── engine.py       # 比較エンジン
│       │   ├── models.py       # 比較モデル
│       │   ├── views.py        # ターミナルビュー
│       │   └── reporters.py    # Markdownレポーター
│       └── workflow/
│           ├── __init__.py
│           ├── exporter.py     # 多様な形式でのエクスポート
│           └── importer.py     # 翻訳のインポート
├── tests/
│   ├── unit/                   # 単体テスト
│   ├── integration/            # 統合テスト
│   ├── e2e/                    # エンドツーエンドテスト
│   └── fixtures/               # テストデータ
├── docs/
│   ├── en/                     # 英語ドキュメント
│   └── ja/                     # 日本語ドキュメント
├── .docdiff/                    # キャッシュディレクトリ（gitignoreされる）
│   ├── cache/                  # 解析データキャッシュ
│   └── reports/                # 生成されたレポート
├── pyproject.toml              # プロジェクト設定
├── CLAUDE.md                   # AIアシスタント指示
└── .claude/                    # Claude固有の設定
    └── commands/               # カスタムコマンド
```

(dev-testing-strategy)=
## テスト戦略

(dev-running-tests)=
### テストの実行

全テストを実行:
```{code-block} bash
:name: dev-code-run-all-tests
:caption: 全テストを実行

uv run pytest tests/
```

カバレッジ付きで実行:
```{code-block} bash
:name: dev-code-run-with-coverage
:caption: カバレッジ付きでテスト実行

uv run pytest tests/ --cov=docdiff --cov-report=term-missing
```

特定のテストタイプを実行:
```{code-block} bash
:name: dev-code-run-specific-tests
:caption: 特定のテストタイプの実行

# 単体テストのみ
uv run pytest tests/unit/

# 統合テスト
uv run pytest tests/integration/

# E2Eテスト
uv run pytest tests/e2e/
```

(dev-test-coverage-goals)=
### テストカバレッジ目標

- 単体テストカバレッジ: > 80%
- 統合テストカバレッジ: 主要なワークフロー
- E2Eテストカバレッジ: メインのユーザージャーニー

(dev-writing-tests)=
### テストの作成

単体テストの例:
```{code-block} python
:name: dev-code-unit-test-example
:caption: 単体テストの例
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
## AI翻訳最適化

(dev-ai-batch-algorithm)=
### バッチ最適化アルゴリズム

AdaptiveBatchOptimizerは、81%のバッチ効率を達成する洗練されたアルゴリズムを使用します：

```{code-block} python
:name: dev-code-batch-algorithm
:caption: バッチ最適化アルゴリズム
:linenos:

def optimize_batches(nodes: List[TranslationNode]) -> List[TranslationBatch]:
    """ノードを効率的なバッチに最適化する。
    
    アルゴリズム:
    1. ファイルと位置でノードをソート
    2. 隣接する小さなノードをマージ
    3. セクション境界を尊重
    4. セマンティックな関係を維持
    5. バッチあたり500-2000トークンを目標
    """
    batches = []
    current_batch = []
    current_tokens = 0
    
    for node in nodes:
        node_tokens = estimate_tokens(node.content)
        
        # 追加により最大サイズを超えるかチェック
        if current_tokens + node_tokens > max_batch_size:
            if current_batch:
                batches.append(create_batch(current_batch))
            current_batch = [node]
            current_tokens = node_tokens
        else:
            current_batch.append(node)
            current_tokens += node_tokens
            
            # 最適サイズに達したかチェック
            if current_tokens >= target_batch_size:
                batches.append(create_batch(current_batch))
                current_batch = []
                current_tokens = 0
    
    return batches
```

(dev-ai-token-estimation)=
### トークン推定

さまざまな言語とモデルに対する正確なトークンカウント:

```{code-block} python
:name: dev-code-token-estimation
:caption: トークン推定の実装
:linenos:

def estimate_tokens(text: str, language: str = "en") -> int:
    """テキストのトークン数を推定する。
    
    要因:
    - 英語: ~4文字あたり1トークン
    - 日本語: ~2文字あたり1トークン
    - コードブロック: ~3文字あたり1トークン
    - 特定モデルでの調整
    """
    if language == "ja":
        return len(text) // 2
    elif language == "zh":
        return len(text) // 2
    else:
        return len(text) // 4
```

(dev-ai-context-management)=
### コンテキスト管理

翻訳品質向上のための関連コンテキストの含有:

```{code-block} python
:name: dev-code-context-management
:caption: コンテキスト管理
:linenos:

def add_context(node: TranslationNode, window: int = 3) -> Dict:
    """ノードに周囲のコンテキストを追加する。
    
    含まれる内容:
    - 前のNノード
    - 後のNノード
    - 親セクション
    - 関連する用語集
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
### パフォーマンス指標

監視すべき主要指標:

- **バッチ効率**: 目標80%以上（実際/最適トークン）
- **API呼び出し削減**: 目標90%以上削減
- **トークンオーバーヘッド**: 目標10%未満
- **処理速度**: > 1000ノード/秒

(dev-code-style-guidelines)=
## コードスタイルガイドライン

(dev-python-conventions)=
### Python規約

- Python 3.12+の機能を使用
- すべての関数に型ヒント
- すべてのパブリックAPIにdocstring
- ruff強制でPEP 8に従う
- レガシーコードに対するゼロトレランス

(dev-quality-tools)=
### 品質管理ツール

```{code-block} bash
:name: dev-code-quality-check
:caption: 品質チェックの実行
:linenos:

# コードフォーマット
uv run ruff format .

# リントと自動修正
uv run ruff check . --fix

# 型チェック
uv run mypy .

# 一度にすべてのチェック
uv run ruff format . && uv run ruff check . --fix && uv run mypy . && uv run pytest tests/
```

(dev-commit-guidelines)=
### コミットガイドライン

- 従来のコミット形式を使用
- コミットメッセージは英語
- 該当する場合はissueを参照

例:
```
feat: add CSV export format support
fix: correct fuzzy matching threshold
docs: update CLI reference for compare command
refactor: simplify comparison engine logic
test: add E2E tests for export/import workflow
```

(dev-breaking-changes)=
## 破壊的変更ポリシー

**重要**: docdiffは「破壊的変更歓迎」の哲学に従います：

- 後方互換性要件なし
- 非推奨期間不要
- 常に利用可能な最良のソリューションを使用
- 良いデザインのために自由にリファクタリング
- 未使用コードは即座に削除

このポリシーは、技術的負債を避けることで開発を加速し、コード品質を維持します。

(dev-contributing)=
## 貢献

### 開発ワークフロー

1. リポジトリをフォーク
2. 機能ブランチを作成
3. テスト付きで変更を加える
4. 品質チェックを実行
5. プルリクエストを提出

### プルリクエストチェックリスト

- [ ] テスト追加/更新済み
- [ ] ドキュメント更新済み
- [ ] 品質チェック通過（ruff、mypy、pytest）
- [ ] コミットメッセージが規約に従う
- [ ] PR説明が変更を説明

def extract_references(nodes: List[DocumentNode]) -> List[Reference]:
    """ドキュメントノードからクロスリファレンスを抽出する。
    
    Args:
        nodes: 処理するドキュメントノードのリスト
        
    Returns:
        抽出されたリファレンスのリスト
        
    Raises:
        ParseError: リファレンス構文が無効な場合
    """
```

3. **コメント**: コメントは英語で記述
```{code-block} python
:name: dev-code-comment-example
:caption: コメントの例
:linenos:

# Calculate content hash for change detection
content_hash = hashlib.sha256(content.encode()).hexdigest()
```

(dev-data-validation)=
### データ検証

データ検証には常にPydanticモデルを使用:
```{code-block} python
:name: dev-code-pydantic-validation
:caption: Pydantic検証の例
:linenos:

from pydantic import BaseModel, validator

class TranslationUnit(BaseModel):
    source_content: str
    target_lang: str
    
    @validator('target_lang')
    def validate_language_code(cls, v):
        if len(v) != 2:
            raise ValueError('言語コードは2文字である必要があります')
        return v.lower()
```

(dev-implementation-phases)=
## 実装フェーズ

(dev-phase-1-mvp)=
### フェーズ1: MVP (2週間)

実装するコア機能:

1. **プロジェクト構造セットアップ**
   - リポジトリ構造の初期化
   - pyproject.tomlの設定
   - 開発環境のセットアップ

2. **Pydanticモデル**
   - DocumentNode
   - TranslationUnit
   - NodeType列挙

3. **SQLiteデータベース管理**
   - スキーマ作成
   - CRUD操作
   - マイグレーションサポート

4. **基本パーサー実装**
   - myst-parserを使用したMySTパーサー
   - docutilsを使用したreStructuredTextパーサー
   - 共通インターフェース定義

5. **CLIコマンド**
   - `parse`コマンド
   - `status`コマンド
   - 基本的なエラーハンドリング

(dev-phase-2-enhancement)=
### フェーズ2: 機能拡張 (1週間)

追加機能:

1. **増分更新**
   - コンテンツハッシュを使用した変更検出
   - 効率的な更新戦略

2. **高度なエラーハンドリング**
   - 詳細なエラーメッセージ
   - 復旧メカニズム
   - ロギングシステム

3. **エクスポート機能**
   - JSONエクスポート
   - CSVエクスポート
   - カスタム形式

4. **包括的テスト**
   - 単体テストカバレッジ
   - 統合テスト
   - パフォーマンスベンチマーク

(dev-phase-3-future)=
### フェーズ3: 将来の拡張

予定される拡張:

1. **JupyterBookサポート**
   - JSON形式解析
   - ノートブック統合

2. **翻訳API統合**
   - OpenAI API
   - Claude API
   - カスタム翻訳サービス

3. **Web UI**
   - REST APIバックエンド
   - Reactフロントエンド
   - リアルタイム更新

4. **プラグインシステム**
   - カスタムパーサープラグイン
   - 翻訳サービスプラグイン
   - エクスポート形式プラグイン

(dev-database-migrations)=
## データベースマイグレーション

(dev-creating-migrations)=
### マイグレーションの作成

スキーマ変更が必要な場合:

```{code-block} python
:name: dev-code-migration-example
:caption: マイグレーションの例
:linenos:

# migrations/001_add_review_status.py
def upgrade(db):
    db.execute("""
        ALTER TABLE translation_units 
        ADD COLUMN reviewer_id TEXT
    """)
    
def downgrade(db):
    # SQLiteはDROP COLUMNをサポートしない
    # テーブルの再作成が必要
    pass
```

(dev-running-migrations)=
### マイグレーションの実行

```{code-block} bash
:name: dev-code-run-migrations
:caption: マイグレーションの実行
:linenos:

docdiff db upgrade
docdiff db downgrade --to 001
```

(dev-performance-optimization)=
## パフォーマンス最適化

(dev-indexing-strategy)=
### インデックス戦略

パフォーマンスのための重要なインデックス:
- `nodes.label` - リファレンス解決
- `nodes.parent_id` - 階層トラバーサル
- `nodes.file_path` - ファイル操作
- `translation_units.status` - ステータスフィルタリング

(dev-batch-operations)=
### バッチ操作

複数ファイルを効率的に処理:
```{code-block} python
:name: dev-code-batch-operations
:caption: バッチ操作の例
:linenos:

async def parse_batch(files: List[Path]) -> List[DocumentNode]:
    tasks = [parse_file(f) for f in files]
    results = await asyncio.gather(*tasks)
    return flatten(results)
```

(dev-caching)=
### キャッシュ

高コストな操作のキャッシュ実装:
```{code-block} python
:name: dev-code-caching-example
:caption: キャッシュの例
:linenos:

from functools import lru_cache

@lru_cache(maxsize=128)
def resolve_reference(label: str) -> Optional[str]:
    # 高コストなデータベースルックアップ
    return db.find_node_by_label(label)
```

(dev-debugging-tips)=
## デバッグのヒント

(dev-enable-debug-logging)=
### デバッグログの有効化

```{code-block} bash
:name: dev-code-debug-logging
:caption: デバッグログの有効化
:linenos:

export DOCDIFF_LOG_LEVEL=DEBUG
docdiff parse docs/
```

(dev-database-inspection)=
### データベース検査

```{code-block} bash
:name: dev-code-database-inspection
:caption: データベース検査
:linenos:

# SQLiteデータベースを開く
sqlite3 .docdiff/structure.db

# 有用なクエリ
.tables
.schema nodes
SELECT type, COUNT(*) FROM nodes GROUP BY type;
```

(dev-parser-debugging)=
### パーサーデバッグ

```{code-block} python
:name: dev-code-parser-debugging
:caption: パーサーデバッグ
:linenos:

# AST印刷を有効化
from docdiff.parsers import MySTParser

parser = MySTParser(debug=True)
nodes = parser.parse(Path("test.md"))
# AST構造を印刷
```

(dev-contributing-guidelines)=
## 貢献ガイドライン

(dev-pull-request-process)=
### プルリクエストプロセス

1. `main`から機能ブランチを作成
2. 新機能のテストを作成
3. すべてのテストが通ることを確認
4. ドキュメントを更新
5. 明確な説明でPRを提出

(dev-commit-message-format)=
### コミットメッセージ形式

```{code-block} text
:name: dev-code-commit-message
:caption: コミットメッセージ形式

feat: Add support for JupyterBook format

- Implement JSON parser
- Add notebook cell extraction
- Update CLI commands

Closes #123
```

(dev-code-review-checklist)=
### コードレビューチェックリスト

- [ ] 型ヒントが存在する
- [ ] テストが作成されて通過している
- [ ] ドキュメントが更新されている
- [ ] セキュリティ脆弱性がない
- [ ] パフォーマンスが考慮されている
- [ ] エラーハンドリングが完備されている