(docdiff-docs)=

# docdiff Documentation

(docdiff-overview)=

## 概要

docdiff は、MyST および reStructuredText 形式のドキュメントに特化した、強力な多言語翻訳管理ツールです。高度な文書構造解析機能と翻訳進捗管理機能を備えており、技術文書の国際化プロセスを効率化します。

(docdiff-key-features)=

## 主な機能

- インテリジェントな構造解析: 機械的なテキスト分割ではなく、文書を論理的な構造単位（セクション、コードブロック、表、図など）に解析
- 高度な比較エンジン: 複数回のマッチング処理を行うアルゴリズムを採用し、完全一致・あいまい一致・欠落ノードの検出が可能
- 豊富な可視化機能: ツリービュー、メタデータグループ化、左右並列比較、統計表示など、複数の表示モードを搭載
- 柔軟なエクスポート/インポート: JSON、CSV、XLSX、XLIFF 2.1、Markdown など多様な形式に対応し、スムーズな翻訳ワークフローを実現
- メタデータ対応処理: ラベル、名称、キャプションなどの構造メタデータを保存・追跡可能
- Git 連携対応レポート: 詳細表示・GitHub スタイル・コンパクト表示など複数スタイルに対応した Markdown 出力でバージョン管理と連携
- 段階的更新処理: ハッシュ値に基づくコンテンツ検出により、文書変更を効率的に処理
- キャッシュ管理: `.docdiff/`ディレクトリにプロジェクトキャッシュを一元管理し、持続性とパフォーマンスを向上

(docdiff-quick-start)=

## クイックスタート

```{code-block} bash
:name: docdiff-code-quick-start
:caption: Quick Start Commands
:linenos:

# Install docdiff
uv sync
uv pip install -e .

# Compare documentation between languages
docdiff compare docs/en docs/ja

# Generate detailed Markdown report
docdiff compare docs/en docs/ja --output report.md

# Export translation tasks to CSV
docdiff export docs/en docs/ja --format csv --output tasks.csv

# Import completed translations
docdiff import tasks_completed.csv --source-dir docs/en --target-dir docs/ja
```

(docdiff-documentation-contents)=

## Documentation Contents

```{toctree}
:caption: 'User Documentation:'
:maxdepth: 2

user-guide
cli-reference
architecture
```

```{toctree}
:caption: 'Developer Documentation:'
:maxdepth: 2

developer-guide
api-reference
```

(docdiff-why)=

## docdiff を選ぶ理由

従来の翻訳ツールでは、文書が細かすぎる断片に分割され、重要な文脈が失われてしまうという問題がありました。docdiff はこの問題を解決するために:

1. 文書構造の保持: ドキュメントの論理的な構成を維持します
2. 文脈を考慮した翻訳単位: 関連する内容をグループ化して、翻訳品質を向上させます
3. 効率的な変更管理: 実際に変更された箇所のみを再翻訳します
4. 参照情報の整合性: 言語間の相互参照が適切に機能し続けることを保証します

(docdiff-project-status)=

## プロジェクトの現状

docdiff は現在も活発にメンテナンスが行われており、以下の機能が利用可能です：

- ✅ 文書構造解析：メタデータを保持した高度な MyST/reStructuredText パーシング機能
- ✅ 翻訳範囲分析：ファジーマッチングに対応した包括的な比較エンジン
- ✅ 複数の出力形式：JSON、CSV、XLSX、XLIFF 2.1、および Markdown 形式のレポート
- ✅ 豊富な可視化機能：ターミナルベースおよびファイルベースのレポート出力、複数の表示モードに対応
- ✅ 翻訳ワークフロー：翻訳管理のための完全なエクスポート/インポートサイクル機能

### 今後の機能追加予定

- 機械翻訳連携機能：AI を活用した翻訳サービスとの連携
- Web インターフェース：技術知識のないユーザー向けのブラウザベース UI
- 翻訳メモリ機能：過去に翻訳した内容を再利用する機能

(docdiff-getting-help)=

## サポートを受けるには

- 問題報告: バグ報告や機能要望は [GitHub Issues](https://github.com/yourusername/docdiff/issues) に投稿してください
- ディスカッション: 議論に参加したい場合は [GitHub Discussions](https://github.com/yourusername/docdiff/discussions) をご覧ください
- 貢献方法: 貢献に関するガイドラインは {doc}`developer-guide` を参照してください

(docdiff-license)=

## License

docdiff is open source software licensed under the MIT License.
