(cli-reference)=
# CLIリファレンス

docdiffコマンドラインインターフェースは、文書翻訳の分析および管理を行うためのツール群を提供します。

(cli-installation)=
## インストール方法

`uv` を使用して `docdiff` をインストールするには:

```{code-block} bash
:name: cli-code-installation
:caption: Installation Commands
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
:caption: Compare Command Usage

docdiff compare <source-dir> <target-dir> [OPTIONS]
```

Arguments:
- `source-dir`: ソースドキュメントのディレクトリ（例: docs/en）
- `target-dir`: ターゲットドキュメントのディレクトリ（例: docs/ja）

Options:
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

Example:
```{code-block} bash
:name: cli-code-compare-examples
:caption: Compare Command Examples
:linenos:

# Basic comparison with summary view
docdiff compare docs/en docs/ja

# Generate Markdown report (style auto-detected from filename)
docdiff compare docs/en docs/ja --output report.md          # detailed style
docdiff compare docs/en docs/ja --output report.github.md   # GitHub style
docdiff compare docs/en docs/ja --output report.compact.md  # compact style

# View metadata-based grouping
docdiff compare docs/en docs/ja --view metadata

# Generate HTML report
docdiff compare docs/en docs/ja --html
```

出力形式:

Markdownレポートスタイル:
- 詳細表示（デフォルト）: 全セクションを含む包括的なレポート
- GitHubスタイル: GitHub風のMarkdown形式（折りたたみ可能なセクションとMermaidダイアグラム付き）
- 簡易表示: 翻訳不足箇所に焦点を当てた最小限のレポート

ターミナル表示モード:
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
:caption: Parse Command Usage

docdiff parse <project-dir> [OPTIONS]
```

Arguments:
- `project-dir`: ドキュメントディレクトリへのパス

Options:
- `--cache-dir`: デフォルトのキャッシュディレクトリを上書きする（デフォルト: .docdiff/cache）
- `--verbose, -v`: 詳細な解析情報を表示する

Example:
```{code-block} bash
:name: cli-code-parse-examples
:caption: Parse Command Examples
:linenos:

# Parse documentation
docdiff parse docs/en

# Parse with verbose output
docdiff parse docs/ja --verbose
```

(cli-command-status)=
### `docdiff status`

翻訳ステータスの概要を表示します。

```{code-block} bash
:name: cli-code-status-usage
:caption: Status Command Usage

docdiff status <source-dir> <target-dir> [OPTIONS]
```

Arguments:
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: 出力ドキュメントのディレクトリ

Options:
- `--source-lang, -s`: ソース言語コード（デフォルト: en）
- `--target-lang, -t`: ターゲット言語コード（デフォルト: ja）
- `--format`: 出力形式（`summary`, `detailed`）

Example:
```{code-block} bash
:name: cli-code-status-examples
:caption: Status Command Examples
:linenos:

# Quick status check
docdiff status docs/en docs/ja

# Detailed status
docdiff status docs/en docs/ja --format detailed
```

(cli-command-export)=
### `docdiff export`

翻訳タスクを各種フォーマットにエクスポートします。

```{code-block} bash
:name: cli-code-export-usage
:caption: Export Command Usage

docdiff export <source-dir> <target-dir> [OPTIONS]
```

Arguments:
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: 出力ドキュメントのディレクトリ

Options:
- `--format, -f`: エクスポート形式：
  - `json`：JSON形式（デフォルト）
  - `csv`：CSVスプレッドシート形式
  - `xlsx`：Excelワークブック形式
  - `xliff`：XLIFF 2.1翻訳形式
- `--output, -o`: 出力ファイルパス（必須）
- `--source-lang, -s`: ソース言語コード（デフォルト：en）
- `--target-lang, -t`: ターゲット言語コード（デフォルト：ja）
- `--include-translated`: 既に翻訳済みのコンテンツを含める
- `--metadata-only`: コンテンツは含めずメタデータのみをエクスポート

Example:
```{code-block} bash
:name: cli-code-export-examples
:caption: Export Command Examples
:linenos:

# Export to CSV for spreadsheet translation
docdiff export docs/en docs/ja --format csv --output tasks.csv

# Export to XLIFF for CAT tools
docdiff export docs/en docs/ja --format xliff --output translation.xlf

# Export to Excel with multiple sheets
docdiff export docs/en docs/ja --format xlsx --output tasks.xlsx

# Include already translated content for review
docdiff export docs/en docs/ja --format json --output all.json --include-translated
```

Output Formats:

CSV Format:
```{code-block} text
:name: cli-code-export-csv-format
:caption: CSV Export Format

ID,File,Line,Type,Status,Similarity,Source,Target,Label,Name,Notes
7f3a2b,index.md,7,paragraph,missing,0.0,"docdiff is a powerful...",,,,,
8c4d5e,index.md,11,list,fuzzy,100.0,"- Intelligent Structure...","- Intelligent Structure...",,,
```

XLIFF Format:
```{code-block} xml
:name: cli-code-export-xliff-format
:caption: XLIFF 2.1 Export Format

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

エクスポートされたファイルから翻訳をインポートします。

```{code-block} bash
:name: cli-code-import-usage
:caption: Import Command Usage

docdiff import <input-file> [OPTIONS]
```

Arguments:
- `input-file`: Path to the file containing translations (CSV, JSON, XLSX, or XLIFF)

Options:
- `--source-dir`: Source documentation directory (for validation)
- `--target-dir`: Target documentation directory (where to write translations)
- `--source-lang, -s`: Source language code (default: en)
- `--target-lang, -t`: Target language code (default: ja)
- `--dry-run`: Preview changes without writing files
- `--verbose, -v`: Show detailed import progress

Example:
```{code-block} bash
:name: cli-code-import-examples
:caption: Import Command Examples
:linenos:

# Import translations from CSV
docdiff import translated.csv --source-dir docs/en --target-dir docs/ja

# Dry run to preview changes
docdiff import translated.xlsx --source-dir docs/en --target-dir docs/ja --dry-run

# Import from XLIFF with verbose output
docdiff import translation.xlf --target-dir docs/ja --verbose
```

(cli-command-simple-compare)=
### `docdiff simple-compare`

ディレクトリ間の基本構造の比較。

```{code-block} bash
:name: cli-code-simple-compare-usage
:caption: Simple Compare Command Usage

docdiff simple-compare <source-dir> <target-dir> [OPTIONS]
```

Arguments:
- `source-dir`: ソースドキュメントのディレクトリ
- `target-dir`: 出力ドキュメントのディレクトリ

Options:
- `--verbose, -v`: Show detailed comparison

Example:
```{code-block} bash
:name: cli-code-simple-compare-examples
:caption: Simple Compare Command Examples
:linenos:

# Quick structure comparison
docdiff simple-compare docs/en docs/ja

# Detailed comparison
docdiff simple-compare docs/en docs/ja --verbose
```

(cli-configuration)=
## Configuration

docdiffはプロジェクトルートディレクトリに`.docdiff/`フォルダを使用してキャッシュとレポートを管理します:

```{code-block} text
:name: cli-code-cache-structure
:caption: Cache Directory Structure

.docdiff/
├── cache/           # Parsed document cache
│   ├── nodes.db     # Document structure database
│   └── mappings.db  # Translation mappings
└── reports/         # Generated reports
    ├── comparison_en_ja.html
    └── *.md         # Markdown reports
```

Note: Add `.docdiff/` to your `.gitignore` file to exclude cache from version control.

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
:caption: Initial Translation Setup
:linenos:

# 1. Compare source and target documentation
docdiff compare docs/en docs/ja

# 2. Generate detailed report for review
docdiff compare docs/en docs/ja --output initial-status.md

# 3. Export missing translations to CSV
docdiff export docs/en docs/ja --format csv --output translations-needed.csv

# 4. After translation, import the completed CSV
docdiff import translations-completed.csv --source-dir docs/en --target-dir docs/ja
```

(cli-workflow-continuous)=
### 継続的翻訳管理

```{code-block} bash
:name: cli-code-workflow-continuous
:caption: Continuous Translation Workflow
:linenos:

# Daily workflow
# 1. Check current translation coverage
docdiff compare docs/en docs/ja --view summary

# 2. Generate GitHub-style report for PR
docdiff compare docs/en docs/ja --output report.github.md

# 3. Export only missing translations
docdiff export docs/en docs/ja --format xlsx --output weekly-tasks.xlsx

# 4. View metadata-based grouping for prioritization
docdiff compare docs/en docs/ja --view metadata
```

(cli-workflow-team)=
### チーム翻訳ワークフロー

```{code-block} bash
:name: cli-code-workflow-team
:caption: Team Translation Workflow
:linenos:

# Project manager: Export tasks
docdiff export docs/en docs/ja --format xlsx --output team-tasks.xlsx

# Translator: Work on Excel file
# ... translation work ...

# Project manager: Import completed translations
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run  # Preview first

# If preview looks good, import for real
docdiff import team-tasks-completed.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# Generate report for stakeholders
docdiff compare docs/en docs/ja --output status-report.md
```

(cli-exit-codes)=
## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Parse error
- `3`: Database error
- `4`: Validation error
- `5`: Configuration error

(cli-tips-best-practices)=
## 活用のコツとベストプラクティス

1. 定期的な解析処理: ドキュメント構造の変更を検知するため、定期的にドキュメントを再解析しましょう
2. バージョン管理: `.docdiff.yml`ファイルをバージョン管理システムに含め、`.docdiff/`ディレクトリは除外設定してください
3. 段階的な更新処理: `--filter outdated`オプションを使用して、変更のあったコンテンツのみを対象に処理を行います
4. 検証作業: メジャーリリース前には必ず検証を実行し、参照情報の整合性を確認してください
5. 一括処理: 個別のコマンド実行ではなく、設定ファイル内で複数の対象言語をまとめて処理することを推奨します