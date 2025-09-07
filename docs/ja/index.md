(docdiff-docs)=

# docdiff ドキュメント

(docdiff-overview)=

## 概要

docdiff は、MyST および reStructuredText 形式のドキュメントに特化した、強力な多言語翻訳管理ツールです。高度な文書構造解析機能と翻訳進捗管理機能を備えており、技術文書の国際化プロセスを効率化します。

(docdiff-key-features)=

## 主な機能

- **インテリジェントな構造解析**: 機械的なテキスト分割ではなく、文書を論理的な構造単位（セクション、コードブロック、表、図など）に解析
- **AI 翻訳最適化**: 適応的バッチ最適化により81%の効率性を実現し、API呼び出しを69%削減
- **高度な比較エンジン**: 複数回のマッチング処理を行うアルゴリズムを採用し、完全一致・あいまい一致・欠落ノードの検出が可能
- **Sphinx統合機能**: 自動用語集抽出と相互参照追跡により、一貫性のある翻訳を実現
- **豊富な可視化機能**: ツリービュー、メタデータグループ化、左右並列比較、統計表示など、複数の表示モードを搭載
- **柔軟なエクスポート/インポート**: 階層化JSON（スキーマv1.0）、CSV、XLSX、XLIFF 2.1対応でシームレスなワークフローを実現
- **文脈対応翻訳**: 文書階層を保持し、周辺コンテキストを含めてより良いAI翻訳を実現
- **メタデータ対応処理**: ラベル、名称、キャプション、その他の構造メタデータを保持・追跡
- **Git連携対応レポート**: 詳細表示・GitHub風・コンパクト表示など複数スタイルのMarkdown出力でバージョン管理と統合
- **段階的更新処理**: ハッシュ値に基づくコンテンツ検出により、文書変更を効率的に処理
- **パフォーマンス最適化**: インテリジェントなトークン推定とバッチ処理により、14,000以上のノード/秒で処理

(docdiff-quick-start)=

## クイックスタート

```{code-block} bash
:name: docdiff-code-quick-start
:caption: クイックスタートコマンド
:linenos:

# docdiffのインストール
uv sync
uv pip install -e .

# 言語間でドキュメントを比較
docdiff compare docs/en docs/ja

# 詳細なMarkdownレポートを生成
docdiff compare docs/en docs/ja --output report.md

# AI翻訳向けエクスポート（最適化バッチ処理）
docdiff export docs/en docs/ja translation.json \
  --include-context --batch-size 1500 \
  --glossary glossary.yml

# 翻訳タスクをCSVにエクスポート
docdiff export docs/en docs/ja tasks.csv --format csv

# 完了した翻訳をインポート
docdiff import translation_complete.json docs/ja
```

(docdiff-documentation-contents)=

## ドキュメントの内容

```{toctree}
:caption: 'ユーザードキュメント:'
:maxdepth: 2

user-guide
cli-reference
ai-translation
sphinx-integration
architecture
```

```{toctree}
:caption: '開発者ドキュメント:'
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

- **✅ 文書構造解析**: メタデータを保持した高度なMyST/reStructuredTextパーシング機能
- **✅ AI翻訳最適化**: 適応的バッチ処理により81%の効率性を実現し、API呼び出しを69%削減
- **✅ Sphinx統合**: 自動用語集抽出と相互参照追跡機能
- **✅ 翻訳範囲分析**: ファジーマッチングに対応した包括的な比較エンジン
- **✅ 複数のエクスポート形式**: 階層化JSON（v1.0）、CSV、XLSX、XLIFF 2.1、Markdownレポート
- **✅ 文脈対応エクスポート**: 設定可能なコンテキストウィンドウで文書階層を保持
- **✅ 豊富な可視化機能**: ターミナルベースおよびファイルベースのレポート出力、複数の表示モード
- **✅ 翻訳ワークフロー**: 翻訳管理のための完全なエクスポート/インポートサイクル
- **✅ パフォーマンス最適化**: 最小限のメモリ使用量で14,000以上のノード/秒を処理

### 今後の機能追加予定

- **並列バッチ処理**: 高速翻訳のための同時API呼び出し機能
- **Webインターフェース**: 技術知識のないユーザー向けのブラウザベースUI
- **翻訳メモリ**: 以前に翻訳されたコンテンツの再利用機能
- **POT/PO形式サポート**: 完全なSphinx i18n統合

(docdiff-getting-help)=

## サポートを受けるには

- 問題報告: バグ報告や機能要望は [GitHub Issues](https://github.com/yourusername/docdiff/issues) に投稿してください
- ディスカッション: 議論に参加したい場合は [GitHub Discussions](https://github.com/yourusername/docdiff/discussions) をご覧ください
- 貢献方法: 貢献に関するガイドラインは {doc}`developer-guide` を参照してください

(docdiff-license)=

## ライセンス

docdiff は MIT ライセンスのもとで公開されているオープンソースソフトウェアです。
