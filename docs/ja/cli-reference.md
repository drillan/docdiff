(cli-reference)=
# CLIリファレンス

docdiffコマンドラインインターフェースは、文書翻訳の分析および管理を行うためのツール群を提供します。

(cli-installation)=
## インストール方法

`uv` を使用して `docdiff` をインストールするには:

```{code-block} bash
:name: cli-code-installation
:caption: インストールコマンド
:linenos:

uv sync
uv pip install -e .
```

(cli-available-commands)=
## 使用可能なコマンド

(cli-command-compare)=
### `docdiff compare`

文書比較機能と翻訳範囲分析機能を備えています。

```{code-block} bash
:name: cli-code-compare-usage
:caption: compareコマンドの使用法

docdiff compare <source-dir> <target-dir> [OPTIONS]
```

**引数:**
- `source-dir`: ソースドキュメントのディレクトリ（例: docs/en）
- `target-dir`: ターゲットドキュメントのディレクトリ（例: docs/ja）

**オプション:**
- `--source-lang, -s`: ソース言語コード（デフォルト: en）
- `--target-lang, -t`: ターゲット言語コード（デフォルト: ja）
- `--output, -o`: レポートの出力先パス（.json および .md 拡張子に対応）
- `--html`: .docdiff/reports/ ディレクトリに HTML レポートを生成
- `--view`: 表示モードを選択:
  - `summary`: カバレッジ統計の概要表示（デフォルト）
  - `tree`: ドキュメントの階層ツリー表示
  - `metadata`: メタデータ別グループ表示（ラベル/名称別）
  - `side-by-side`: コンテンツの左右比較表示
  - `stats`: 詳細統計情報の表示
- `--verbose, -v`: 詳細な出力を表示

**使用例:**
```{code-block} bash
:name: cli-code-compare-examples
:caption: compareコマンドの例
:linenos:

# 概要ビューでの基本比較
docdiff compare docs/en docs/ja

# Markdownレポートを生成（ファイル名からスタイルを自動検出）
docdiff compare docs/en docs/ja --output report.md          # 詳細スタイル
docdiff compare docs/en docs/ja --output report.github.md   # GitHubスタイル
docdiff compare docs/en docs/ja --output report.compact.md  # コンパクトスタイル

# メタデータベースのグループ表示
docdiff compare docs/en docs/ja --view metadata

# HTMLレポートを生成
docdiff compare docs/en docs/ja --html
```

**出力形式:**

**Markdownレポートスタイル:**
- 詳細表示（デフォルト）: 全セクションを含む包括的なレポート
- GitHubスタイル: GitHub風のMarkdown形式（折りたたみ可能なセクションとMermaidダイアグラム付き）
- 簡易表示: 翻訳不足箇所に焦点を当てた最小限のレポート

**ターミナル表示モード:**
- 概要表示: 全体のカバー率統計と構造の差異を表示
- ツリー表示: 文書階層構造と翻訳状況を示すインジケーター
- メタデータ表示: ラベルとname属性でグループ化し、カバー率バーを表示
- 横並び表示: 原文と訳文の内容を比較する表形式
- 統計表示: 詳細な統計データと各タイプの分布状況

(cli-command-parse)=
### `docdiff parse`

ドキュメントを解析し、分析用の構造を抽出します。

```{code-block} bash
:name: cli-code-parse-usage
:caption: parseコマンドの使用法

docdiff parse <project-dir> [OPTIONS]
```

**引数:**
- `project-dir`: ドキュメントディレクトリへのパス

**オプション:**
- `--cache-dir`: デフォルトのキャッシュディレクトリを上書きする（デフォルト: .docdiff/cache）
- `--verbose, -v`: 詳細な解析情報を表示する

**使用例:**
```{code-block} bash
:name: cli-code-parse-examples
:caption: parseコマンドの例
:linenos:

# ドキュメントを解析
docdiff parse docs/en

# 詳細出力付きで解析
docdiff parse docs/ja --verbose
```

(cli-command-status)=
### `docdiff status`

翻訳ステータスの概要を表示します。

```{code-block} bash
:name: cli-code-status-usage
:caption: statusコマンドの使用法

docdiff status <source-dir> <target-dir> [OPTIONS]
```

**引数:**
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: ターゲットドキュメントのディレクトリ

**オプション:**
- `--source-lang, -s`: ソース言語コード（デフォルト: en）
- `--target-lang, -t`: ターゲット言語コード（デフォルト: ja）
- `--format`: 出力形式（`summary`, `detailed`）

**使用例:**
```{code-block} bash
:name: cli-code-status-examples
:caption: statusコマンドの例
:linenos:

# クイックステータスチェック
docdiff status docs/en docs/ja

# 詳細ステータス
docdiff status docs/en docs/ja --format detailed
```

(cli-command-export)=
### `docdiff export`

翻訳タスクを各種フォーマットにエクスポートします。

```{code-block} bash
:name: cli-code-export-usage
:caption: exportコマンドの使用法

docdiff export <source-dir> <target-dir> [OPTIONS]
```

**引数:**
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: ターゲットドキュメントのディレクトリ

**オプション:**
- `--format, -f`: エクスポート形式：
  - `json`: AI最適化された階層JSON形式（デフォルト）
  - `csv`: CSVスプレッドシート形式
  - `xlsx`: Excelワークブック形式
  - `xliff`: XLIFF 2.1翻訳形式
- `--output, -o`: 出力ファイルパス（必須）
- `--source-lang, -s`: ソース言語コード（デフォルト: en）
- `--target-lang, -t`: ターゲット言語コード（デフォルト: ja）
- `--include-missing`: 未翻訳部分を含める（デフォルト: true）
- `--include-outdated`: 古くなった翻訳を含める（デフォルト: false）
- `--include-context`: AI翻訳向上のため周辺コンテキストを含める（デフォルト: false）
- `--batch-size, -b`: AI翻訳用のバッチサイズをトークン数で指定（デフォルト: 2000、範囲: 500-2000）
- `--context-window, -w`: コンテキスト用の周辺ノード数（デフォルト: 3）
- `--glossary, -g`: 用語一貫性のための用語集ファイルパス
- `--verbose, -v`: 最適化レポートを含む詳細出力を表示

**使用例:**
```{code-block} bash
:name: cli-code-export-examples
:caption: exportコマンドの例
:linenos:

# AI翻訳に最適化されたエクスポート
docdiff export docs/en docs/ja translation.json \
  --include-context \
  --batch-size 1500 \
  --context-window 5 \
  --glossary glossary.yml \
  --verbose

# スプレッドシート翻訳用のCSVエクスポート
docdiff export docs/en docs/ja tasks.csv --format csv

# CATツール用のXLIFFエクスポート
docdiff export docs/en docs/ja translation.xlf --format xliff

# 複数シート付きExcelエクスポート
docdiff export docs/en docs/ja tasks.xlsx --format xlsx

# レビュー用に古くなった翻訳を含める
docdiff export docs/en docs/ja review.json --include-outdated
```

**出力形式:**

**階層JSON形式（AI最適化）:**
```{code-block} json
:name: cli-code-export-json-format
:caption: 階層JSON エクスポート形式

{
  "schema_version": "1.0",
  "metadata": {
    "docdiff_version": "0.1.0",
    "export_timestamp": "2025-09-07T15:45:01",
    "source_lang": "en",
    "target_lang": "ja",
    "statistics": {
      "total_nodes": 497,
      "total_batches": 40,
      "batch_efficiency": "81%",
      "api_calls_saved": 457
    }
  },
  "translation_batches": [
    {
      "batch_id": 1,
      "estimated_tokens": 1773,
      "file_group": "docs/en/index.md",
      "section_range": "## Overview to ### Features",
      "node_ids": ["id1", "id2", "id3"]
    }
  ],
  "document_hierarchy": {},
  "sphinx_context": {}
}
```

**最適化レポート（--verboseオプション使用時）:**
```{code-block} text
:name: cli-code-export-optimization-report
:caption: バッチ最適化レポート

適応バッチ最適化レポート
===================================
総ノード数:         497
総バッチ数:         40
バッチ効率:         81.0%

トークン統計:
  平均:             1532 tokens/batch
  最小:             502 tokens
  最大:             1998 tokens
  目標:             1500-2000 tokens

最適化結果:
  API呼び出し削減:   457 (92.0% 削減)
  トークンオーバーヘッド: 8.0% (優秀)
  コスト削減:        ~70%
  
ステータス: ✅ 最適
```

**CSV形式:**
```{code-block} text
:name: cli-code-export-csv-format
:caption: CSVエクスポート形式

ID,File,Line,Type,Status,Similarity,Source,Target,Label,Name,Notes
7f3a2b,index.md,7,paragraph,missing,0.0,"docdiff is a powerful...",,,,,
8c4d5e,index.md,11,list,fuzzy,100.0,"- Intelligent Structure...","- Intelligent Structure...",,,
```

XLIFF Format:
```{code-block} xml
:name: cli-code-export-xliff-format
:caption: XLIFF 2.1エクスポート形式

<?xml version="1.0" encoding="UTF-8"?>
<xliff version="2.1" srcLang="en" trgLang="ja">
  <file id="index.md">
    <unit id="7f3a2b">
      <segment>
        <source>docdiff is a powerful multilingual...</source>
        <target state="initial"></target>
      </segment>
    </unit>
  </file>
</xliff>
```

(cli-command-import)=
### `docdiff import`

完了された翻訳をドキュメントに逆インポートします。

```{code-block} bash
:name: cli-code-import-usage
:caption: importコマンドの使用法

docdiff import <import-file> <target-dir> [OPTIONS]
```

**引数:**
- `import-file`: インポートファイルのパス（JSON、CSV、XLSX、またはXLIFF）
- `target-dir`: ターゲットドキュメントディレクトリ

**オプション:**
- `--format, -f`: インポート形式（指定されない場合は自動検出）
- `--target-lang, -t`: ターゲット言語コード（デフォルト: ja）
- `--create-missing`: 未翻訳ファイル用の新規ファイル作成（デフォルト: true）
- `--overwrite`: 既存翻訳の上書き（デフォルト: false）
- `--dry-run`: 実際に適用せずに変更をプレビュー
- `--verbose, -v`: 詳細な出力を表示

**使用例:**
```{code-block} bash
:name: cli-code-import-examples
:caption: importコマンドの例
:linenos:

# AI翻訳済みJSONのインポート
docdiff import translation_complete.json docs/ja

# 変更をプレビューするためのドライラン
docdiff import translation.json docs/ja --dry-run

# 上書きオプション付きCSVインポート
docdiff import tasks_complete.csv docs/ja --overwrite

# CATツールからのXLIFFインポート
docdiff import translation.xlf docs/ja --format xliff

# 詳細出力付きインポート
docdiff import translation.json docs/ja --verbose
```

(cli-command-simple-compare)=
### `docdiff simple-compare`

ディレクトリ間の基本的な構造比較を実行します。

```{code-block} bash
:name: cli-code-simple-compare-usage
:caption: simple-compareコマンドの使用法

docdiff simple-compare <source-dir> <target-dir> [OPTIONS]
```

**引数:**
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: ターゲットドキュメントのディレクトリ

**オプション:**
- `--verbose, -v`: 詳細比較を表示

**使用例:**
```{code-block} bash
:name: cli-code-simple-compare-examples
:caption: simple-compareコマンドの例
:linenos:

# 簡単な構造比較
docdiff simple-compare docs/en docs/ja

# 詳細比較
docdiff simple-compare docs/en docs/ja --verbose
```

(cli-configuration)=
## 設定

docdiffはプロジェクトルートディレクトリに`.docdiff/`フォルダを使用してキャッシュとレポートを管理します:

```{code-block} text
:name: cli-code-cache-structure
:caption: キャッシュディレクトリ構造

.docdiff/
├── cache/           # 解析済みドキュメントキャッシュ
│   ├── nodes.db     # ドキュメント構造データベース
│   └── mappings.db  # 翻訳マッピング
└── reports/         # 生成されたレポート
    ├── comparison_en_ja.html
    └── *.md         # Markdownレポート
```

**注意:** バージョン管理からキャッシュを除外するため、`.docdiff/`を`.gitignore`ファイルに追加してください。

(cli-environment-variables)=
## 環境変数

- `DOCDIFF_DB_PATH`: デフォルトのデータベース保存場所を上書き
- `DOCDIFF_CONFIG`: 設定ファイルのパス
- `DOCDIFF_LOG_LEVEL`: ログレベル（DEBUG, INFO, WARNING, ERROR）

(cli-common-workflows)=
## 一般的なワークフロー

(cli-workflow-initial-setup)=
### 初期翻訳設定

```{code-block} bash
:name: cli-code-workflow-initial
:caption: 初期翻訳設定
:linenos:

# 1. ソースとターゲットドキュメントの比較
docdiff compare docs/en docs/ja

# 2. レビュー用の詳細レポート生成
docdiff compare docs/en docs/ja --output initial-status.md

# 3. 未翻訳部分をCSVにエクスポート
docdiff export docs/en docs/ja --format csv --output translations-needed.csv

# 4. 翻訳完了後、CSVをインポート
docdiff import translations-completed.csv --source-dir docs/en --target-dir docs/ja
```

(cli-workflow-continuous)=
### 継続的翻訳管理

```{code-block} bash
:name: cli-code-workflow-continuous
:caption: 継続的翻訳ワークフロー
:linenos:

# 日常ワークフロー
# 1. 現在の翻訳カバレージをチェック
docdiff compare docs/en docs/ja --view summary

# 2. PR用のGitHubスタイルレポート生成
docdiff compare docs/en docs/ja --output report.github.md

# 3. 未翻訳部分のみをエクスポート
docdiff export docs/en docs/ja --format xlsx --output weekly-tasks.xlsx

# 4. 優先度付けのためのメタデータベースグルーピング表示
docdiff compare docs/en docs/ja --view metadata
```

(cli-workflow-team)=
### チーム翻訳ワークフロー

```{code-block} bash
:name: cli-code-workflow-team
:caption: チーム翻訳ワークフロー
:linenos:

# プロジェクトマネージャー: タスクのエクスポート
docdiff export docs/en docs/ja --format xlsx --output team-tasks.xlsx

# 翻訳者: Excelファイルで作業
# ... 翻訳作業 ...

# プロジェクトマネージャー: 完了した翻訳のインポート
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run  # まずプレビュー

# プレビューが良ければ、実際にインポート
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# ステークホルダー向けレポート生成
docdiff compare docs/en docs/ja --output status-report.md
```

(cli-exit-codes)=
## 終了コード

- `0`: 成功
- `1`: 一般エラー
- `2`: 解析エラー
- `3`: データベースエラー
- `4`: 検証エラー
- `5`: 設定エラー

(cli-tips-best-practices)=
## 活用のコツとベストプラクティス

1. **定期的な解析**: ドキュメント構造の変更を検知するため、定期的にドキュメントを再解析しましょう
2. **バージョン管理**: `.docdiff.yml`ファイルをバージョン管理に含め、`.docdiff/`ディレクトリは除外してください
3. **段階的更新**: `--filter outdated`を使用して変更されたコンテンツにフォーカスします
4. 検証作業: メジャーリリース前には必ず検証を実行し、参照情報の整合性を確認してください
5. 一括処理: 個別のコマンド実行ではなく、設定ファイル内で複数の対象言語をまとめて処理することを推奨します