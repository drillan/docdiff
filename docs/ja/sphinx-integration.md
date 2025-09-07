(sphinx-integration)=
# Sphinx統合ガイド

docdiffのSphinxドキュメントシステム統合機能の包括的ガイドです。

(sphinx-integration-overview)=
## 概要

docdiffはSphinxドキュメントプロジェクトとの深い統合を提供し、Sphinx固有の機能を自動的に検出・活用して翻訳管理を改善します。

(sphinx-integration-features)=
## 主要機能

- **自動プロジェクト検出**: conf.pyによるSphinxプロジェクトの識別
- **用語集抽出**: Sphinx用語集ディレクティブの解析
- **参照追跡**: 相互参照とリンクの維持
- **メタデータ保持**: ディレクティブとロールをそのまま保持
- **国際化サポート**: Sphinx国際化機能との互換性

(sphinx-integration-detection)=
## プロジェクト検出

(sphinx-detection-automatic)=
### 自動検出

docdiffはSphinxプロジェクトを自動的に検出します：

```{code-block} python
:name: sphinx-code-project-detection
:caption: Sphinxプロジェクト検出

class ProjectDetector:
    """Sphinxプロジェクトの検出と解析を行います。"""
    
    def detect_sphinx_project(self, path: Path) -> bool:
        """ディレクトリがSphinxプロジェクトかどうかをチェックします。"""
        indicators = [
            path / "conf.py",
            path / "source" / "conf.py",
            path / "_build",
            path / "Makefile"  # Sphinx makefile
        ]
        return any(indicator.exists() for indicator in indicators)
    
    def get_project_config(self, path: Path) -> Dict:
        """Sphinx設定を抽出します。"""
        conf_path = self.find_conf_py(path)
        if conf_path:
            return self.parse_conf_py(conf_path)
        return {}
```

(sphinx-detection-configuration)=
### 設定抽出

docdiffは主要なSphinx設定を読み込みます：

```{code-block} python
:name: sphinx-code-config-extraction
:caption: conf.py設定抽出

# 抽出される設定
config = {
    "project": "docdiff",
    "language": "en",
    "extensions": ["myst_parser", "sphinx.ext.autodoc"],
    "source_suffix": {".rst": None, ".md": "myst"},
    "master_doc": "index",
    "exclude_patterns": ["_build", "**.ipynb_checkpoints"]
}
```

(sphinx-integration-glossary)=
## 用語集管理

(sphinx-glossary-extraction)=
### 用語集用語の抽出

docdiffはSphinx用語集ディレクティブを解析します：

```{code-block} rst
:name: sphinx-code-glossary-rst
:caption: Sphinx用語集の例

.. glossary::

   API
      Application Programming Interface。ソフトウェア
      アプリケーション構築のためのプロトコルとツールのセット。
   
   REST
      Representational State Transfer。分散ハイパーメディア
      システムのアーキテクチャスタイル。
   
   JSON
      JavaScript Object Notation。軽量なデータフォーマット。
```

以下で抽出：

```{code-block} bash
:name: sphinx-code-extract-glossary
:caption: 用語集抽出コマンド

# reStructuredTextから抽出
docdiff extract-glossary docs/ --format rst --output glossary.yml

# MyST Markdownから抽出
docdiff extract-glossary docs/ --format myst --output glossary.yml
```

(sphinx-glossary-myst)=
### MyST用語集サポート

MyST-Parser用語集フォーマット：

````{code-block} markdown
:name: sphinx-code-glossary-myst
:caption: MyST用語集の例

```{glossary}
API
  Application Programming Interface。ソフトウェア
  アプリケーション構築のためのプロトコルとツールのセット。

REST
  Representational State Transfer。分散ハイパーメディア
  システムのアーキテクチャスタイル。

JSON
  JavaScript Object Notation。軽量なデータフォーマット。
```
````

(sphinx-glossary-output)=
### 用語集出力フォーマット

YAML形式で抽出された用語集：

```{code-block} yaml
:name: sphinx-code-glossary-output
:caption: 抽出済み用語集YAML

glossary:
  - term: API
    definition: Application Programming Interface。ソフトウェアアプリケーション構築のためのプロトコルとツールのセット。
    source_file: docs/glossary.rst
    line_number: 4
    references: ["api-reference.rst:12", "user-guide.rst:45"]
    
  - term: REST
    definition: Representational State Transfer。分散ハイパーメディアシステムのアーキテクチャスタイル。
    source_file: docs/glossary.rst
    line_number: 8
    references: ["architecture.rst:67"]
    
  - term: JSON
    definition: JavaScript Object Notation。軽量なデータフォーマット。
    source_file: docs/glossary.rst
    line_number: 12
    references: ["api-reference.rst:89", "developer-guide.rst:123"]
```

(sphinx-integration-references)=
## 相互参照管理

(sphinx-references-tracking)=
### 参照追跡

docdiffはすべてのSphinx相互参照を追跡します：

```{code-block} python
:name: sphinx-code-reference-tracking
:caption: 参照追跡実装

class ReferenceTracker:
    """Sphinx相互参照を追跡します。"""
    
    def track_references(self, content: str) -> Dict[str, List[str]]:
        """コンテンツからすべての参照を抽出します。"""
        references = {
            "doc": [],      # :doc: 参照
            "ref": [],      # :ref: 参照
            "term": [],     # :term: 用語集参照
            "class": [],    # :class: API参照
            "func": [],     # :func: 関数参照
            "mod": [],      # :mod: モジュール参照
        }
        
        # reStructuredTextロールを解析
        for match in re.finditer(r':(\w+):`([^`]+)`', content):
            role_type = match.group(1)
            target = match.group(2)
            if role_type in references:
                references[role_type].append(target)
        
        return references
```

(sphinx-references-preservation)=
### 参照保持

翻訳時に参照が保持されます：

```{code-block} text
:name: sphinx-code-reference-preservation
:caption: 参照保持の例

ソース（英語）:
  See :doc:`user-guide` for details and :term:`API` reference.

翻訳（日本語）:
  詳細は :doc:`user-guide` を参照し、:term:`API` リファレンスを確認してください。

注記: 参照は変更されず、周囲のテキストのみが翻訳されます
```

(sphinx-integration-directives)=
## ディレクティブ処理

(sphinx-directives-preservation)=
### ディレクティブ構造保持

docdiffはSphinxディレクティブ構造を維持します：

```{code-block} rst
:name: sphinx-code-directive-preservation
:caption: ディレクティブ保持

.. note::
   これは重要な注記です。
   
   複数行にわたることができます。

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,3
   
   def hello():
       print("Hello")
       return True

.. toctree::
   :maxdepth: 2
   :caption: 目次:
   
   introduction
   user-guide
   api-reference
```

(sphinx-directives-myst)=
### MySTディレクティブサポート

MyST-Parserディレクティブフォーマット：

````{code-block} markdown
:name: sphinx-code-myst-directives
:caption: MySTディレクティブ

```{note}
これは重要な注記です。

複数行にわたることができます。
```

```{code-block} python
:linenos:
:emphasize-lines: 2,3

def hello():
    print("Hello")
    return True
```

```{toctree}
:maxdepth: 2
:caption: 目次:

introduction
user-guide
api-reference
```
````

(sphinx-integration-i18n)=
## 国際化（i18n）

(sphinx-i18n-workflow)=
### Sphinx i18nワークフロー

Sphinx内蔵i18nとの統合：

```{code-block} bash
:name: sphinx-code-i18n-workflow
:caption: Sphinx i18n統合

# ステップ1: 翻訳可能文字列を抽出（Sphinx）
sphinx-build -b gettext docs/source docs/locale/pot

# ステップ2: AI翻訳用にdocdiffでエクスポート
docdiff export docs/source docs/locale/ja translation.json \
  --include-context --glossary glossary.yml

# ステップ3: AIで翻訳
python translate_with_ai.py translation.json

# ステップ4: インポートして戻す
docdiff import translation_complete.json docs/locale/ja

# ステップ5: ローカライズドキュメントをビルド
sphinx-build -D language=ja docs/source docs/build/ja
```

(sphinx-i18n-po-support)=
### PO/POTファイルサポート（予定）

gettextフォーマットの将来サポート：

```{code-block} bash
:name: sphinx-code-po-support
:caption: PO/POTファイルサポート（近日公開）

# POTフォーマットにエクスポート
docdiff export docs/source translation.pot --format pot

# POファイルからインポート
docdiff import translated.po docs/locale/ja --format po

# 既存翻訳とマージ
docdiff merge existing.po new.po --output merged.po
```

(sphinx-integration-metadata)=
## メタデータ管理

(sphinx-metadata-extraction)=
### メタデータ抽出

docdiffはSphinx固有のメタデータを抽出します：

```{code-block} python
:name: sphinx-code-metadata-extraction
:caption: メタデータ抽出

metadata = {
    "labels": {},      # 参照ラベル
    "names": {},       # 名前付きブロック
    "captions": {},    # 図表キャプション
    "toctree": [],     # 目次
    "index": [],       # インデックスエントリ
    "domains": {       # Sphinxドメイン
        "py": [],      # Pythonドメイン
        "c": [],       # Cドメイン
        "js": [],      # JavaScriptドメイン
    }
}
```

(sphinx-metadata-example)=
### メタデータの例

```{code-block} rst
:name: sphinx-code-metadata-example
:caption: 豊富なメタデータの例

.. _installation-guide:
.. index:: installation, setup, configuration

インストールガイド
==================

.. figure:: images/architecture.png
   :name: fig-architecture
   :caption: システムアーキテクチャ図
   :alt: コンポーネントを示すアーキテクチャ図
   
   この図はシステムコンポーネントを示しています。

.. code-block:: python
   :name: code-example-hello
   :caption: Hello World例
   :linenos:
   
   def hello_world():
       """簡単な挨拶関数。"""
       print("Hello, World!")
```

(sphinx-integration-automation)=
## 自動化機能

(sphinx-automation-hooks)=
### ビルドフック

docdiffをSphinxビルドプロセスと統合：

```{code-block} python
:name: sphinx-code-build-hooks
:caption: conf.pyビルドフック

# conf.py内
def setup(app):
    """Sphinxアプリケーションフックをセットアップします。"""
    
    # ビルド前: 翻訳ステータスをチェック
    app.connect("builder-inited", check_translation_status)
    
    # ビルド後: 翻訳レポートを生成
    app.connect("build-finished", generate_translation_report)
    
def check_translation_status(app):
    """ビルド前に翻訳カバレッジをチェックします。"""
    import subprocess
    result = subprocess.run(
        ["docdiff", "status", "source", "locale/ja"],
        capture_output=True
    )
    print(f"翻訳カバレッジ: {result.stdout}")

def generate_translation_report(app, exception):
    """ビルド後に翻訳レポートを生成します。"""
    if not exception:
        subprocess.run([
            "docdiff", "compare", 
            "source", "locale/ja",
            "--output", "_build/translation-report.md"
        ])
```

(sphinx-automation-makefile)=
### Makefile統合

SphinxのMakefileにdocdiffコマンドを追加：

```{code-block} makefile
:name: sphinx-code-makefile
:caption: Makefile統合

# Sphinx Makefile追加部分

.PHONY: translation-status
translation-status:
	@docdiff status source locale/$(LANG)

.PHONY: export-translation
export-translation:
	@docdiff export source locale/$(LANG) translation.json \
		--include-context --glossary glossary.yml

.PHONY: import-translation
import-translation:
	@docdiff import translation_complete.json locale/$(LANG)

.PHONY: translation-report
translation-report:
	@docdiff compare source locale/$(LANG) \
		--output _build/translation-report.md --html
```

(sphinx-integration-best-practices)=
## ベストプラクティス

(sphinx-practices-structure)=
### プロジェクト構造

推奨Sphinxプロジェクトレイアウト：

```{code-block} text
:name: sphinx-code-project-structure
:caption: 推奨プロジェクト構造

docs/
├── source/                 # ソースドキュメント
│   ├── conf.py            # Sphinx設定
│   ├── index.rst          # マスタードキュメント
│   ├── _static/           # 静的ファイル
│   ├── _templates/        # カスタムテンプレート
│   └── *.rst/*.md         # ドキュメントファイル
├── locale/                # 翻訳
│   ├── pot/              # POTテンプレート
│   ├── ja/               # 日本語翻訳
│   └── zh/               # 中国語翻訳
├── _build/               # ビルド出力
└── .docdiff/            # docdiffキャッシュ
    ├── glossary.yml     # 抽出済み用語集
    └── cache/           # 解析済み構造キャッシュ
```

(sphinx-practices-workflow)=
### 翻訳ワークフロー

1. **プロジェクト構造セットアップ**: ソースとロケールディレクトリを整理
2. **用語集抽出**: 用語データベースを構築
3. **初期エクスポート**: コンテキスト付きで翻訳タスクを作成
4. **AI翻訳**: 最適化されたバッチ処理で処理
5. **インポート・レビュー**: 翻訳を適用してレビュー
6. **ビルド・検証**: ローカライズドキュメントを生成
7. **継続的更新**: 変更を追跡して段階的に更新

(sphinx-integration-troubleshooting)=
## トラブルシューティング

(sphinx-troubleshooting-common)=
### 一般的な問題

| 問題 | 解決策 |
|-------|----------|
| conf.pyが検出されない | パスを確認するか`--sphinx-conf`オプションを使用 |
| 用語集が抽出されない | 用語集ディレクティブフォーマットを確認 |
| 参照が破損 | 対象ドキュメントが存在することを確認 |
| ディレクティブが失われる | パーサー（rst vs myst）を確認 |
| メタデータが欠落 | 最新のdocdiffバージョンに更新 |

(sphinx-troubleshooting-validation)=
### 検証コマンド

```{code-block} bash
:name: sphinx-code-validation
:caption: 検証コマンド

# Sphinxプロジェクトを検証
docdiff validate-sphinx docs/source

# 参照をチェック
docdiff check-references docs/source

# 用語集を確認
docdiff verify-glossary docs/source glossary.yml

# 翻訳付きビルドをテスト
sphinx-build -D language=ja -W docs/source docs/test
```

(sphinx-integration-summary)=
## まとめ

docdiffのSphinx統合は以下を提供します：

- 既存Sphinxプロジェクトとの**シームレスな互換性**
- **自動機能検出**と設定
- 一貫性のための**用語集・参照管理**
- 翻訳全体を通じた**メタデータ保持**
- 自動化のための**ビルドプロセス統合**
- 今後のSphinx機能に対応した**将来性のある**設計

docdiffを活用してSphinxドキュメント翻訳を効率的に管理しましょう！