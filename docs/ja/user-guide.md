(user-guide)=
# ユーザーガイド

このガイドでは、docdiffを使用して多言語ドキュメントの翻訳管理を行うための実践的な手順を説明します。

(user-guide-overview)=
## 概要

docdiffは次の機能で技術ドキュメントの翻訳を追跡・管理します：
- 生テキストではなく文書構造の解析
- 詳細な指標による翻訳カバレッジの追跡
- 翻訳ワークフロー用の複数のエクスポート形式の提供
- プロジェクト管理用のレポート生成

(user-guide-getting-started)=
## はじめに

(user-guide-installation)=
### インストール

uvパッケージマネージャーを使用してdocdiffをインストールします：

```{code-block} bash
:name: user-code-installation
:caption: インストール手順

# リポジトリをクローン
git clone https://github.com/yourusername/docdiff.git
cd docdiff

# 依存関係をインストール
uv sync

# docdiffをインストール
uv pip install -e .

# インストール確認
uv run docdiff --version
```

(user-guide-basic-workflow)=
## 基本的な翻訳ワークフロー

翻訳管理の典型的なワークフローは4つの主要ステップで構成されます：

```{code-block} text
:name: user-workflow-diagram
:caption: 翻訳ワークフロー

1. 比較 → 2. エクスポート → 3. 翻訳 → 4. インポート
     ↑                                         ↓
     └─────────────── 5. 検証 ←─────────────┘
```

(user-guide-step1-compare)=
### ステップ 1: ドキュメントの比較

まず、現在の翻訳ステータスを解析します：

```{code-block} bash
:name: user-code-compare
:caption: ソースとターゲットドキュメントの比較

# 基本比較
uv run docdiff compare docs/en docs/ja

# 詳細ビューで表示
uv run docdiff compare docs/en docs/ja --view metadata

# マークダウンレポート生成
uv run docdiff compare docs/en docs/ja --output status.md
```

比較では以下の情報が表示されます：
- 全体的な翻訳カバレッジ率
- 翻訳済み、欠落、曖昧一致のノード数
- ソースとターゲット間の構造差

(user-guide-step2-export)=
### ステップ 2: 翻訳用エクスポート

翻訳ワークフローに適した形式で未翻訳部分をエクスポートします：

```{code-block} bash
:name: user-code-export
:caption: 翻訳タスクのエクスポート

# CSVへのエクスポート（スプレッドシートツール用推奨）
uv run docdiff export docs/en docs/ja --format csv --output tasks.csv

# メタデータ付きExcelエクスポート
uv run docdiff export docs/en docs/ja --format xlsx --output tasks.xlsx

# CATツール用XLIFFエクスポート
uv run docdiff export docs/en docs/ja --format xliff --output tasks.xlf
```

**JSON形式（AI最適化）** は以下に推奨：
- AI駆動翻訳サービス
- 最適効率でのバッチ処理
- 階層保持によるコンテキスト対応翻訳
- API呼び出しを70%削減

**CSV形式** は以下に推奨：
- シンプルなスプレッドシート編集
- バージョン管理（Git対応）
- 汎用的な互換性

**Excel形式** は以下を提供：
- 組織化のための複数シート
- リッチフォーマットオプション
- コメントとメモのサポート

**XLIFF形式** は以下に最適：
- プロフェッショナルCATツール
- 翻訳メモリシステム
- 業界標準ワークフロー

(user-guide-step3-translate)=
### ステップ 3: コンテンツの翻訳

お好みのツールでエクスポートファイルを開きます：
- **CSV**: Excel、Google Sheets、LibreOffice Calc
- **XLSX**: Microsoft Excel
- **XLIFF**: SDL Trados、MemoQ、OmegaT

翻訳のコツ：
- フォーマットマーカー（Markdownの`**太字**`など）を保持する
- 技術用語の一貫性を保つ
- ID、ファイル、タイプ列は変更しない
- Target列に翻訳を記入する

(user-guide-step4-import)=
### ステップ 4: 翻訳のインポート

翻訳完了後、完成ファイルをインポートします：

```{code-block} bash
:name: user-code-import
:caption: 完成翻訳のインポート

# 最初にプレビューを確認（ドライラン）
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja \
  --dry-run

# プレビューが良好であれば実際にインポート
uv run docdiff import translated.csv \
  --source-dir docs/en \
  --target-dir docs/ja
```

インポート処理では以下が実行されます：
- ソース構造に対する翻訳の検証
- ターゲットファイルの作成・更新
- 文書フォーマットの保持
- 発見された問題の報告

(user-guide-step5-verify)=
### ステップ 5: 結果の検証

インポート後、翻訳更新を検証します：

```{code-block} bash
:name: user-code-verify
:caption: 翻訳更新の検証

# 新しいカバレッジを確認
uv run docdiff compare docs/en docs/ja

# 詳細レポートを生成
uv run docdiff compare docs/en docs/ja --output final-report.md
```

(user-guide-ai-translation)=
## AI駆動翻訳最適化

docdiffには革新的なAI最適化機能が含まれており、インテリジェントなバッチ処理とコンテキスト管理により翻訳コストを劇的に削減し品質を向上させます。

(user-guide-ai-translation-workflow)=
## AI翻訳ワークフロー

docdiffは品質を維持しながら大幅にコストを削減する高度なAI翻訳最適化を提供します。

(user-guide-ai-overview)=
### AI翻訳概要

適応バッチシステムは以下を実現します：
- **81%のバッチ効率**: インテリジェントノード統合によりトークン使用量を最適化
- **69%のAPI呼び出し削減**: 典型的なドキュメントで139回から43回に削減
- **約70%のコスト削減**: API呼び出し減少により翻訳費用を削減
- **コンテキスト対応バッチ処理**: より良い品質のために意味関係を維持
- **用語集駆動の一貫性**: ドキュメント全体で用語統一を確保

**パフォーマンス比較:**
```
従来手法:     497 API呼び出し（ノード毎に1回）     ❌ $$$
最適化手法:    40 バッチ（81%効率）              ✅ $
改善効果:      92%のAPI呼び出し削減
```

(user-guide-ai-setup)=
### AI翻訳の設定

(user-guide-ai-glossary)=
#### ステップ 1: 用語集の作成

用語の一貫性を確保するために用語集を作成します：

```{code-block} bash
:name: user-code-ai-glossary
:caption: 用語集の設定

# オプション 1: Sphinxドキュメントから抽出
uv run docdiff extract-glossary docs/en --output glossary.yml

# オプション 2: テンプレートから作成
cat > glossary.yml << EOF
terms:
  - term: API
    definition: Application Programming Interface
    translation: API
    maintain_original: true
  - term: docdiff
    definition: Document diff and translation tool
    maintain_original: true
EOF
```

サポートされる用語集形式：
- **YAML**: 人間が読みやすい、Git対応
- **JSON**: 構造化データ形式
- **CSV**: スプレッドシート互換

(user-guide-ai-config)=
#### ステップ 2: AI設定の構成

バッチ最適化設定を構成します：

```{code-block} bash
:name: user-code-ai-config
:caption: AI設定のセットアップ

# 設定テンプレートをコピー
cp samples/ai-config.yaml .docdiff/ai-config.yaml

# 設定をカスタマイズ
vi .docdiff/ai-config.yaml
```

主要な設定オプション：
- `batching.target_size`: バッチあたりの最適トークン数（デフォルト: 1500）
- `batching.min_size`: 最小バッチサイズ（デフォルト: 500）
- `batching.max_size`: 最大バッチサイズ（デフォルト: 2000）
- `context.window_size`: コンテキスト用の周囲ノード数（デフォルト: 3）
- `glossary.file`: 用語集ファイルのパス

(user-guide-ai-export)=
### AI最適化エクスポートの使用

(user-guide-ai-basic-export)=
#### AI最適化による基本エクスポート

```{code-block} bash
:name: user-code-ai-export-basic
:caption: 基本AI最適化エクスポート

# デフォルト最適化によるシンプルエクスポート（自動バッチ処理）
uv run docdiff export docs/en docs/ja translation.json
```

(user-guide-ai-advanced-export)=
#### 完全最適化による高度エクスポート

```{code-block} bash
:name: user-code-ai-export-advanced
:caption: 高度AI最適化エクスポート

# 全最適化によるエクスポート
uv run docdiff export docs/en docs/ja translation.json \
  --include-context \
  --batch-size 1500 \
  --context-window 5 \
  --glossary .docdiff/glossary.yml \
  --verbose
```

これにより以下が実行されます：
- 81%効率の適応バッチ処理を使用（常時有効）
- より良い翻訳コンテキストのために周囲5ノードを含含
- 用語一貫性のために用語集を適用
- 約70%のコスト削減を含む詳細な最適化指標を表示

(user-guide-ai-metrics)=
### AI指標の理解

(user-guide-ai-batch-metrics)=
#### バッチ効率指標

`--verbose`を使用すると、最適化指標が表示されます：

```
バッチ最適化指標:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 総ノード数:           432
• バッチ数:             2
• 平均バッチサイズ:     1,554 トークン
• バッチ効率:           95.2%
• API呼び出し削減:      99.5%
• 推定コスト削減:       90%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**指標の説明:**
- **バッチ効率**: 使用されたバッチ容量の割合
- **API呼び出し削減**: 非最適化時と比較したAPI呼び出しの減少
- **コスト削減**: 推定翻訳コスト削減

(user-guide-ai-quality-metrics)=
#### 翻訳品質指標

```{code-block} bash
:name: user-code-ai-quality
:caption: 翻訳品質のチェック

# バッチ品質スコアの表示
jq '.translation_batches[].quality_metrics' translation.json

# 全体統計の確認
jq '.metadata.statistics' translation.json
```

品質指標：
- **一貫性スコア**: 意味関係の強さ（0-1）
- **コンテキストカバレッジ**: コンテキスト付きノードの割合
- **用語集カバレッジ**: 用語集でカバーされる用語

(user-guide-ai-optimization)=
### 最適化ガイドライン

(user-guide-ai-batch-sizing)=
#### バッチサイズの選択

AIモデル別最適バッチサイズ：

| モデル | 推奨 | 最大 | 備考 |
|-------|-------------|---------|--------|
| GPT-4 | 1500 トークン | 2000 トークン | 技術文書に最適 |
| Claude-3 | 2000 トークン | 3000 トークン | 良好なコンテキストウィンドウ |
| Gemini Pro | 1800 トークン | 2500 トークン | バランスの取れた性能 |

```{code-block} bash
:name: user-code-ai-batch-size
:caption: モデル特化バッチサイズ

# GPT-4用
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 1500

# Claude-3用
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 2000

# Gemini Pro用
uv run docdiff export docs/en docs/ja output.json \
  --adaptive --batch-size 1800
```

(user-guide-ai-context)=
#### コンテキストウィンドウ設定

コンテキストにより翻訳品質が向上します：

```{code-block} bash
:name: user-code-ai-context
:caption: コンテキストウィンドウ設定

# 最小コンテキスト（高速、低品質）
--context-window 1

# 標準コンテキスト（バランス）
--context-window 3

# 拡張コンテキスト（低速、高品質）
--context-window 5
```

(user-guide-ai-cost-control)=
### コスト管理

(user-guide-ai-incremental)=
#### 増分翻訳

変更があった部分のみを翻訳します：

```{code-block} bash
:name: user-code-ai-incremental
:caption: 増分翻訳エクスポート

# 欠落翻訳のみエクスポート
uv run docdiff export docs/en docs/ja \
  updates.json \
  --adaptive \
  --filter missing \
  --glossary .docdiff/glossary.json

# 古い翻訳のみエクスポート
uv run docdiff export docs/en docs/ja \
  outdated.json \
  --adaptive \
  --filter outdated
```

(user-guide-ai-caching)=
#### 翻訳キャッシュ

以前の翻訳を再利用するためにキャッシュを有効化します：

```{code-block} bash
:name: user-code-ai-cache
:caption: 翻訳キャッシュの使用

# キャッシュ有効化でエクスポート
uv run docdiff export docs/en docs/ja \
  cached.json \
  --adaptive \
  --cache \
  --cache-dir .docdiff/translation-cache
```

(user-guide-ai-limits)=
#### コスト制限の設定

`ai-config.yaml`で日次トークン制限を設定します：

```{code-block} yaml
:name: user-code-ai-limits
:caption: コスト管理設定

cost:
  track_usage: true
  daily_limit: 100000     # 日次トークン制限
  batch_limit: 5000       # バッチ毎制限
  alert_threshold: 0.8    # 80%使用時にアラート
```

(user-guide-ai-workflow-integration)=
### 翻訳ワークフローとの統合

(user-guide-ai-complete-workflow)=
#### 完全AI最適化ワークフロー

```{code-block} bash
:name: user-code-ai-workflow
:caption: エンドツーエンドAI翻訳

# 1. 現在の状態を解析
uv run docdiff compare docs/en docs/ja --view summary

# 2. AI最適化でエクスポート
uv run docdiff export docs/en docs/ja \
  translation.json \
  --adaptive \
  --batch-size 1500 \
  --glossary .docdiff/glossary.json \
  --verbose

# 3. 最適化結果を確認
echo "作成されたバッチ数: $(jq '.translation_batches | length' translation.json)"
echo "平均効率: $(jq '.metadata.statistics.avg_batch_efficiency' translation.json)%"

# 4. 翻訳サービスに送信
# （ここに翻訳プロセスが入ります）

# 5. 完了した翻訳をインポート
uv run docdiff import translated.json \
  --source-dir docs/en \
  --target-dir docs/ja

# 6. 結果を検証
uv run docdiff compare docs/en docs/ja --output report.md
```

(user-guide-ai-troubleshooting)=
### AI翻訳トラブルシューティング

(user-guide-ai-low-efficiency)=
#### 問題: バッチ効率が低い

効率が60%以下の場合：

```{code-block} bash
:name: user-code-ai-troubleshoot-efficiency
:caption: バッチ効率の改善

# 現在の効率を確認
uv run docdiff export docs/en docs/ja test.json \
  --adaptive --verbose | grep "efficiency"

# バッチパラメータを調整
uv run docdiff export docs/en docs/ja optimized.json \
  --adaptive \
  --batch-size 2000 \
  --min-batch-size 800 \
  --merge-small-nodes
```

(user-guide-ai-glossary-issues)=
#### 問題: 用語の不一致

```{code-block} bash
:name: user-code-ai-troubleshoot-glossary
:caption: 用語集問題の修正

# 用語使用状況を解析
uv run docdiff glossary analyze docs/ja \
  --glossary .docdiff/glossary.json

# 新しい用語を抽出
uv run docdiff glossary extract \
  --source docs/en \
  --target docs/ja \
  --output new-terms.json

# 既存用語集と統合
uv run docdiff glossary merge \
  .docdiff/glossary.json \
  new-terms.json \
  --output .docdiff/glossary.json
```

(user-guide-ai-best-practices)=
### AI翻訳ベストプラクティス

1. **小さな用語集から開始**（重要用語20-30個）
2. **適応バッチ処理を使用** 全てのエクスポートで
3. **バッチ効率を監視**（目標 >80%）
4. **翻訳をキャッシュ** 再処理を避ける
5. **コスト制限を設定** 超過を防ぐ
6. **品質指標を確認** 各バッチ後に
7. **用語集を更新** 結果に基づいて
8. **増分更新を使用** 継続翻訳のために

詳細なAIワークフロー例については、{doc}`ai-translation`ガイドを参照してください。

(user-guide-reports)=
## レポートの理解

(user-guide-markdown-reports)=
### マークダウンレポート

docdiffは3つのスタイルでマークダウンレポートを生成します：

**詳細レポート**（デフォルト）：
```bash
uv run docdiff compare docs/en docs/ja --output report.md
```
- 包括的なカバレッジ統計
- メタデータベースのグループ化
- 並行比較
- 欠落翻訳詳細

**GitHub形式レポート**：
```bash
uv run docdiff compare docs/en docs/ja --output report.github.md
```
- 折りたたみ可能セクション
- Mermaidダイアグラム
- 追跡用タスクリスト
- バッジとアラート

**コンパクトレポート**：
```bash
uv run docdiff compare docs/en docs/ja --output report.compact.md
```
- 最小限の形式
- 上位の欠落項目のみ
- クイックステータス概要

(user-guide-terminal-views)=
### ターミナルビューモード

異なるビューで翻訳ステータスを理解できます：

```{code-block} bash
:name: user-code-views
:caption: ターミナルビューオプション

# サマリービュー（デフォルト）
uv run docdiff compare docs/en docs/ja --view summary

# ツリービュー - 階層構造
uv run docdiff compare docs/en docs/ja --view tree

# メタデータビュー - ラベル/名前でグループ化
uv run docdiff compare docs/en docs/ja --view metadata

# 並行表示 - 並列比較
uv run docdiff compare docs/en docs/ja --view side-by-side

# 統計 - 詳細メトリクス
uv run docdiff compare docs/en docs/ja --view stats
```

(user-guide-team-workflow)=
## チーム翻訳ワークフロー

チームで翻訳作業を行う場合：

(user-guide-team-setup)=
### 初期設定

1. **プロジェクトマネージャー**: 全翻訳タスクをエクスポート
```bash
uv run docdiff export docs/en docs/ja \
  --format xlsx \
  --output team-tasks-week1.xlsx
```

2. **割り当て** Excelシートを使って各翻訳者にセクションを割り当て

3. **共有** クラウドストレージやバージョン管理システム経由で共有

(user-guide-team-process)=
### 翻訳プロセス

1. **翻訳者** が割り当てられたセクションに作業
2. **保存** 進捗を定期的に保存
3. **マーク** ステータス列で完了項目をマーク

(user-guide-team-integration)=
### 統合プロセス

1. **収集** 翻訳者からの完了ファイルを収集

2. **インポート** 各ファイルを順次インポート：
```bash
# 翻訳者Aの作業をインポート
uv run docdiff import translator-a.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja

# 翻訳者Bの作業をインポート  
uv run docdiff import translator-b.xlsx \
  --source-dir docs/en \
  --target-dir docs/ja
```

3. **生成** 進捗レポート：
```bash
uv run docdiff compare docs/en docs/ja \
  --output weekly-progress.github.md
```

(user-guide-continuous-updates)=
## 継続的更新の管理

ソースドキュメントが変更された場合：

1. **変更検知**：
```bash
# 現在のステータスを比較
uv run docdiff compare docs/en docs/ja --view summary
```

2. **新規/変更コンテンツのみエクスポート**：
```bash
# 欠落翻訳をエクスポート
uv run docdiff export docs/en docs/ja \
  --format csv \
  --output updates-$(date +%Y%m%d).csv
```

3. **Gitでの進捗追跡**：
```bash
# 翻訳更新をコミット
git add docs/ja/
git commit -m "docs: update Japanese translations"

# レポートを追跡
git add *.md
git commit -m "docs: add translation status report"
```

(user-guide-tips)=
## コツとベストプラクティス

(user-guide-tips-performance)=
### パフォーマンス最適化

- 再解析を避けるため`.docdiff/`キャッシュを使用
- エクスポート前に比較を実行してステータスを確認
- 必要に応じて大規模プロジェクトをセクションに分けて処理

(user-guide-tips-quality)=
### 翻訳品質

- 一貫した用語を維持
- コードブロックは正確に保持
- クロスリファレンスを維持
- 曖昧一致を慎重に確認

(user-guide-tips-organization)=
### プロジェクト構成

```{code-block} text
:name: user-project-structure
:caption: 推奨プロジェクト構造

project/
├── docs/
│   ├── en/          # ソースドキュメント
│   ├── ja/          # 日本語翻訳
│   ├── zh/          # 中国語翻訳
│   └── ko/          # 韓国語翻訳
├── translations/    # 翻訳作業ファイル
│   ├── exports/     # エクスポートされたタスクファイル
│   ├── completed/   # 完了翻訳
│   └── reports/     # ステータスレポート
└── .docdiff/        # キャッシュ（gitignore対象）
```

(user-guide-troubleshooting)=
## トラブルシューティング

(user-guide-common-issues)=
### 一般的な問題

**問題**: インポートが「structure mismatch」で失敗
- **解決策**: ソースディレクトリがエクスポート時に使用したものと一致することを確認

**問題**: 曖昧一致精度が低い
- **解決策**: コンテンツに軽微なフォーマット違いがないか確認

**問題**: 欠落翻訳が検出されない
- **解決策**: ターゲットファイルが正しい場所に存在することを確認

**問題**: キャッシュが古いようである
- **解決策**: `.docdiff/cache/`を削除して比較を再実行

(user-guide-getting-help)=
### ヘルプの取得

- コマンド詳細については{doc}`cli-reference`を確認
- プログラマティック使用については{doc}`api-reference`を確認
- [GitHub Issues](https://github.com/yourusername/docdiff/issues)で問題を報告
- [GitHub Discussions](https://github.com/yourusername/docdiff/discussions)でディスカッションに参加