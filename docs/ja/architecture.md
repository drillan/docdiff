(architecture)=
# アーキテクチャ

(architecture-overview)=
## 概要

docdiffは、MyST/reStructuredTextドキュメントのための多言語翻訳管理ツールです。文書を構造単位で解析し、翻訳状態を追跡することで、技術ドキュメントの国際化を支援します。

(architecture-core-design)=
## コア設計思想

システムは以下の設計原則を採用しています：

- **レイヤードアーキテクチャ**: レイヤー間の関心事の明確な分離
- **構造単位による分離**: 文書を論理的な構造単位（セクション、コードブロック、図表、表など）で分離
- **機械的文字分割なし**: 文書コンテキストと意味の保持
- **翻訳状態管理**: 各構造要素の状態追跡（未翻訳/翻訳済み/レビュー済み/期限切れ）

(architecture-system)=
## システムアーキテクチャ

システムは翻訳管理の各側面に特化されたコンポーネントを持つモジュラーアーキテクチャに従います：

```{code-block} text
:name: architecture-diagram-layers
:caption: システムアーキテクチャ図

┌───────────────────────────────────────────────────┐
│                   CLI Layer (Typer)               │
│     Commands: compare, export, import, parse      │
├───────────────────────────────────────────────────┤
│              AI Translation Layer                  │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │AdaptiveBatch    │  │TokenEstimator  │          │
│  │Optimizer        │  │                │          │
│  └─────────────────┘  └────────────────┘          │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │ContextManager   │  │Glossary        │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│              Comparison & Analysis Layer           │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │ComparisonEngine │  │ MetadataView   │          │
│  └─────────────────┘  └────────────────┘          │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │MarkdownReporter │  │ NodeMapping    │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│               Translation Workflow Layer           │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │   Exporter     │  │   Importer     │          │
│  │ (Hierarchical  │  │ (Multi-format  │          │
│  │  JSON v1.0)    │  │   support)     │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│                Sphinx Integration Layer            │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │GlossaryExtractor│  │ReferenceTracker│          │
│  └─────────────────┘  └────────────────┘          │
│  ┌─────────────────┐                              │
│  │ProjectDetector  │                              │
│  └─────────────────┘                              │
├───────────────────────────────────────────────────┤
│                  Parser Layer                      │
│  ┌─────────────────┐  ┌────────────────┐          │
│  │  MySTParser    │  │ DocumentNode   │          │
│  └─────────────────┘  └────────────────┘          │
├───────────────────────────────────────────────────┤
│              Cache Management Layer                │
│  ┌──────────────────────────────────────────┐     │
│  │         CacheManager (.docdiff/)         │     │
│  │    - cache/: SQLite databases            │     │
│  │    - reports/: Generated reports         │     │
│  └──────────────────────────────────────────┘     │
└───────────────────────────────────────────────────┘
```

(architecture-core-components)=
## コアコンポーネント

(architecture-document-node)=
### DocumentNode
文書構造の基本単位で、Pydanticモデルとして実装されています。セクション、段落、コードブロックなどの個別要素を表し、ラベル、名前、キャプションを含む完全なメタデータの保持を行います。

(architecture-myst-parser)=
### MySTParser
MyST（Markedly Structured Text）および標準Markdownフォーマットのための高度なパーサーです。すべてのメタデータ属性と相互参照を保持しながら文書構造を抽出します。

(architecture-comparison-engine)=
### ComparisonEngine
以下を行う高度なマルチパス比較システム：
- **完全一致**: 第一パスでラベルと名前属性によってノードをマッチ
- **あいまい一致**: 第二パスでコンテンツ類似性を使って近似マッチ
- **欠損検出**: 未翻訳コンテンツの識別
- **パフォーマンス**: 毎秒14,000+ノード処理

(architecture-metadata-view)=
### MetadataView
複数の表示モードを提供するリッチターミナル視覚化コンポーネント：
- **ツリービュー**: ステータスインジケータ付き階層文書構造
- **メタデータグループ**: ラベルと名前によってグループ化されたカバレッジ統計
- **サイドバイサイド**: 並列ソース/ターゲットコンテンツ比較
- **統計**: 詳細な型分布とカバレッジメトリクス

(architecture-markdown-reporter)=
### MarkdownReporter
3つのスタイルでGitフレンドリーなMarkdownレポートを生成：
- **詳細**: すべてのセクションと視覚化を含む包括レポート
- **GitHub**: 折りたたみ可能セクション、Mermaid図、タスクリスト
- **コンパクト**: 重要な未翻訳部分に焦点を当てた最小フォーマット

(architecture-adaptive-batch-optimizer)=
### AdaptiveBatchOptimizer
81%のバッチ効率を実現するAI翻訳最適化エンジン：
- **インテリジェントノード結合**: 小さなノードを結合して最適なバッチサイズ（500-2000トークン）に到達
- **意味保持**: コンテンツ間の論理的関係を維持
- **セクション境界**: 最適化しながら文書構造を尊重
- **パフォーマンス**: API呼び出しを69%削減、約70%のコスト削減

(architecture-token-estimator)=
### TokenEstimator
様々なAIモデルに対する正確なトークンカウント：
- **マルチモデルサポート**: OpenAI、Anthropic、その他のプロバイダー
- **言語対応**: ソース/ターゲット言語に基づいた推定調整
- **高速計算**: 毎秒数千ノードを処理
- **キャッシュ**: 冗長な計算を削減

(architecture-context-manager)=
### ContextManager
より良い翻訳品質のための周辺コンテキスト提供：
- **設定可能ウィンドウ**: 1-10の周辺ノード
- **階層認識**: 親/兄弟コンテキストを含む
- **スマート選択**: 関連コンテキストを優先
- **メモリ効率**: 大きな文書に最適化

(architecture-glossary)=
### 用語集（AI & Sphinx）
二重目的の専門用語管理：
- **Sphinx統合**: ドキュメントから用語集を抽出
- **AI翻訳**: 一貫した用語使用を確保
- **マルチフォーマットサポート**: YAML、JSON、CSV用語集
- **自動検出**: 技術用語の識別

(architecture-sphinx-integration)=
### Sphinx統合コンポーネント
Sphinxドキュメントとのシームレスな統合：
- **GlossaryExtractor**: Sphinx用語集ディレクティブの解析
- **ReferenceTracker**: 相互参照の維持
- **ProjectDetector**: Sphinxプロジェクトの自動検出

(architecture-exporter)=
### Exporter
AI最適化されたマルチフォーマットエクスポートシステム：
- **階層JSON v1.0**: AI最適化されたバッチ構造
- **CSV**: 簡単編集のための汎用スプレッドシート形式
- **XLSX**: 複数シートのExcelワークブック
- **XLIFF 2.1**: 業界標準CATツール形式

(architecture-importer)=
### Importer
以下を行うインテリジェントインポートシステム：
- ソース構造に対して翻訳を検証
- 文書フォーマットとメタデータを保持
- プレビュー用ドライランモードをサポート
- すべてのエクスポート形式をシームレスに処理

(architecture-cache-manager)=
### CacheManager
集中キャッシュ管理システム：
- **場所**: プロジェクトルート`.docdiff/`ディレクトリ
- **構造**: 整理されたcache/とreports/サブディレクトリ
- **永続化**: 解析済み構造のためのSQLiteデータベース
- **パフォーマンス**: 冗長な解析操作を排除

(architecture-cli)=
### CLI
Typerで構築された直感的なコマンドを提供するコマンドラインインターフェース：
- `compare`: 複数のビューモード付き高度比較
- `export`: マルチフォーマット翻訳タスクエクスポート
- `import`: 検証付き翻訳インポート
- `parse`: 文書構造抽出
- `status`: 迅速カバレッジサマリー

(architecture-key-features)=
## 主要機能

(architecture-structure-analysis)=
### 文書構造解析
- **セクション識別**: 見出しレベル、タイトル、ラベルの認識
- **属性抽出**: `:name:`と`:caption:`属性の保持
- **相互参照追跡**: JupyterBook/Sphinx参照システムの維持
- **論理分離**: 構造単位による分離（コードブロック、表、図）
- **コンテキスト保持**: 機械的文字カウントベース分割なし

(architecture-translation-management)=
### 翻訳管理
- **状態追跡**: 各構造要素の翻訳ステータス監視
- **変更検出**: ハッシュベースコンテンツ変更検出
- **増分更新**: 変更されたコンテンツのみの効率的更新

(architecture-performance-metrics)=
## パフォーマンスメトリクス

システムはインテリジェント最適化によって卓越したパフォーマンスを実現します：

(architecture-ai-optimization-metrics)=
### AI翻訳最適化
- **バッチ効率**: 81%（2.2%ベースラインから）
  - バッチ利用率3,681%改善
  - 最適トークンパッキング（バッチあたり500-2000トークン）
- **API呼び出し削減**: 69%削減
  - 典型的ドキュメントで139回から43回の呼び出し
  - 大規模プロジェクトでの大幅なコスト節約
- **コスト削減**: AI翻訳サービスで約70%
  - トークンオーバーヘッドを92%から8%に削減
  - 最適化されたコンテキスト包含

(architecture-processing-performance)=
### 処理パフォーマンス
- **解析速度**: 毎秒14,000+ノード
- **比較速度**: 毎秒10,000+ノード比較
- **エクスポート速度**: 完全最適化で毎秒5,000+ノード
- **メモリ効率**: 10,000ノード文書で100MB未満

(architecture-batch-statistics)=
### バッチ最適化統計
```text
例：497ノードドキュメント
- 最適化前：497 API呼び出し（ノードあたり1回）
- 最適化後：40バッチ
- 効率向上：API呼び出し92%削減
- 平均バッチサイズ：1,532トークン
- トークン利用率：目標容量の81%
```
- **バージョン履歴**: 翻訳履歴とタイムスタンプの維持

(architecture-sphinx-support)=
### Sphinxプロジェクトサポート
- **設定読み込み**: `conf.py`設定の自動読み込み
- **バッチ解析**: プロジェクト全体を一括処理
- **Toctree理解**: 文書階層と関係の理解

(architecture-database-design)=
## データベース設計

システムはデータ永続化に以下の主要テーブルを持つSQLiteを使用します：

(architecture-nodes-table)=
### Nodesテーブル
型、コンテンツ、階層、参照を含む完全なメタデータと共に文書構造要素を格納します。

(architecture-references-table)=
### Referencesテーブル
相互参照解決のための文書要素間の関係を維持します。

(architecture-translation-units-table)=
### Translation Unitsテーブル
言語ペア間の各文書要素の翻訳ステータスとコンテンツを追跡します。

データベースには、最適なクエリパフォーマンスのためのラベル、名前、親ID、ファイルパス、ステータスフィールドへの戦略的インデックスが含まれています。

(architecture-technology-stack)=
## 技術スタック

```{list-table} 技術スタック
:name: architecture-table-tech-stack
:header-rows: 1
:widths: 30 70

* - 技術
  - 目的
* - Python 3.12+
  - モダンな型ヒント、改善されたパフォーマンス
* - Pydantic
  - データ検証、シリアライゼーション、型安全性
* - Typer
  - 型ヒントベースCLIと自動ヘルプ生成
* - SQLite
  - トランザクションサポート付き軽量組み込みデータベース
* - myst-parser
  - メタデータ抽出付き高度MyST/Markdown解析
* - Rich
  - 美しいターミナル出力、テーブル、プログレスインジケータ
* - difflib
  - コンテンツ比較のためのあいまい文字列マッチング
* - csv/openpyxl/lxml
  - マルチフォーマットエクスポート/インポートサポート
* - pytest
  - フィクスチャ付き包括的テストフレームワーク
* - ruff
  - 高速Pythonリンター・フォーマッター
* - mypy
  - コード品質のための静的型チェック
```

(architecture-future-extensibility)=
## 将来の拡張性

アーキテクチャは以下の拡張ポイントで設計されています：

- **JupyterBook JSONフォーマットサポート**: モダンドキュメントワークフロー用
- **翻訳API統合**: OpenAI、Claude、その他のAI翻訳サービス
- **Web UI**: 非技術ユーザーのためのブラウザベースインターフェース
- **マルチ言語ペアサポート**: 複数言語への同時翻訳
- **プラグインシステム**: カスタムプロセッサと統合

(architecture-design-considerations)=
## 設計考慮事項

(architecture-interface-separation)=
### インターフェース分離
コンポーネントは明確に定義されたインターフェースを通じて通信し、疎結合と保守性を確保します。

(architecture-flexible-data-models)=
### 柔軟なデータモデル
Pydanticモデルは、データ構造の簡単な拡張と検証を可能にします。

(architecture-data-persistence)=
### データ永続化
SQLiteは軽量性を保ちながらACIDコンプライアンス付きの信頼性のあるストレージを提供します。

(architecture-extensibility-abstraction)=
### 抽象化による拡張性
抽象基底クラスにより、新しいパーサー実装と処理戦略が可能になります。