(readme-title)=
# 🔍 docdiff

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/translation-8.3%25-red)](samples/reports/report-detailed.md)

**インテリジェントな多言語ドキュメント比較・翻訳管理ツール**

docdiffは文書構造を解析して翻訳の進捗を追跡し、欠落している翻訳を特定し、多言語ドキュメントを効率的に管理します。

(readme-key-features)=
## ✨ 主な機能

(readme-translation-coverage)=
### 📊 翻訳カバレッジ分析
翻訳が必要なコンテンツを正確に示す詳細なメトリクスによる、リアルタイムの翻訳カバレッジ追跡。

[→ サンプルレポートを見る](samples/reports/report-detailed.md)

(readme-view-modes)=
### 🔄 複数の表示モード
翻訳状況を理解するための様々な可視化モードから選択：
- **サマリービュー**: 翻訳カバレッジの概要
- **サイドバイサイド**: 並列コンテンツ比較
- **ツリービュー**: 階層的なドキュメント構造
- **メタデータビュー**: ラベルと属性によるグループ化
- **統計ビュー**: 詳細な統計情報

[→ 表示例を見る](samples/views/)

(readme-export-formats)=
### 📤 柔軟なエクスポート形式
ワークフローにシームレスに統合するため、複数の形式で翻訳タスクをエクスポート：
- **CSV**: スプレッドシートツール用（Excel、Googleスプレッドシート）
- **JSON**: プログラマティック処理用
- **XLSX**: リッチなExcelワークブック
- **XLIFF**: 業界標準のCATツール形式

[→ エクスポートサンプルを見る](samples/exports/)

(readme-content-matching)=
### 🎯 スマートコンテンツマッチング
- ラベルベースの構造マッピング
- ファジーコンテンツマッチング
- メタデータの保持
- 言語対応の比較

(readme-quick-start)=
## 🚀 クイックスタート

(readme-installation)=
### インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/docdiff.git
cd docdiff

# uvでインストール（推奨）
uv sync
uv pip install -e .

# インストールの確認
docdiff --version
```

(readme-basic-usage)=
### 基本的な使い方

```bash
# ドキュメントを比較
docdiff compare docs/en docs/ja

# 詳細レポートを生成
docdiff compare docs/en docs/ja --output report.md

# 翻訳タスクをエクスポート
docdiff export docs/en docs/ja tasks.csv --format csv

# 完了した翻訳をインポート
docdiff import tasks.csv --source-dir docs/en --target-dir docs/ja
```

(readme-output-examples)=
## 📸 出力例

(readme-coverage-summary)=
### 翻訳カバレッジサマリー
```
Translation Coverage Summary
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric               ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Overall Coverage     │  8.3% │
│ Total Nodes          │   432 │
│ Translated           │    36 │
│ Missing              │   396 │
└──────────────────────┴───────┘
```
[→ 完全なサマリー](samples/views/summary.txt)

(readme-side-by-side)=
### サイドバイサイド比較
簡単なレビューと検証のため、ソースとターゲットのコンテンツを並列表示。

[→ 比較を見る](samples/views/side-by-side.txt)

(readme-markdown-reports)=
### マークダウンレポート
複数のスタイルで包括的なレポートを生成：
- **[詳細レポート](samples/reports/report-detailed.md)** - すべてのセクションを含む完全な分析
- **[GitHubスタイル](samples/reports/report-github.md)** - 折りたたみ可能なセクションとタスクリスト
- **[コンパクトレポート](samples/reports/report-compact.md)** - 必要な情報のみ

(readme-advanced-features)=
## 🔧 高度な機能

(readme-metadata-processing)=
### メタデータ対応の処理
docdiffはプレーンテキスト以上のドキュメント構造を理解：
- ラベル（`(section-name)=`）を保持
- `:name:`と`:caption:`属性を追跡
- 相互参照を維持
- MyST/reStructuredTextディレクティブを尊重

(readme-intelligent-comparison)=
### インテリジェント比較
比較エンジンはマルチパスマッチングを使用：
1. **構造マッチング** - ラベルと名前による
2. **コンテンツ比較** - 翻訳状態を決定
3. **ファジーマッチング** - 類似コンテンツ用
4. **位置ベース** - マークされていないコンテンツのフォールバック

(readme-cache-management)=
### キャッシュ管理
`.docdiff/`ディレクトリの効率的なキャッシングシステム：
- 解析済みドキュメント構造
- 比較結果
- 生成されたレポート

(readme-documentation)=
## 📚 ドキュメント

- **[ユーザーガイド](docs/en/user-guide.md)** - 詳細な使用方法
- **[CLIリファレンス](docs/en/cli-reference.md)** - 完全なコマンドリファレンス
- **[アーキテクチャ](docs/en/architecture.md)** - システム設計とコンポーネント
- **[APIリファレンス](docs/en/api-reference.md)** - プログラミングインターフェース
- **[開発者ガイド](docs/en/developer-guide.md)** - 貢献と開発

(readme-use-cases)=
## 🎯 ユースケース

(readme-technical-docs)=
### 技術ドキュメント
- APIドキュメント
- ソフトウェアマニュアル
- 開発者ガイド
- READMEファイル

(readme-academic-writing)=
### アカデミックライティング
- 研究論文
- 論文ドキュメント
- コース教材

(readme-corporate-docs)=
### 企業ドキュメント
- 製品マニュアル
- トレーニング資料
- ポリシー文書

(readme-roadmap)=
## 🗺️ ロードマップ

- [ ] 機械翻訳統合
- [ ] 翻訳メモリサポート
- [ ] WebベースUI
- [ ] リアルタイムコラボレーション
- [ ] Gitフック統合
- [ ] CI/CDパイプラインサポート

(readme-contributing)=
## 🤝 貢献

貢献を歓迎します！詳細については[開発者ガイド](docs/en/developer-guide.md)をお読みください：
- 開発環境のセットアップ
- コードスタイルガイドライン
- テスト要件
- プルリクエストプロセス

(readme-license)=
## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

(readme-acknowledgments)=
## 🙏 謝辞

- CLI用の[Typer](https://typer.tiangolo.com/)で構築
- ターミナルフォーマット用の[Rich](https://rich.readthedocs.io/)を使用
- ドキュメント解析用の[myst-parser](https://myst-parser.readthedocs.io/)で駆動

---

<p align="center">
  世界中のドキュメントチームのために❤️を込めて作られました
</p>