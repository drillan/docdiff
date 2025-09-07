---
substitutions:
  date: '{sub-ref}`today`'
  project: DocDiff
  version: 1.0.0
---

(quickstart-guide)=

# クイックスタートガイド

このガイドでは、すばやく始めるために必要な基本的な機能をカバーしています。
システムの基本を学ぶために従ってください。

```{contents} 目次
:depth: 2
:local: true
```

(quickstart-installation)=

## インストール

(quickstart-prerequisites)=

### 前提条件

インストール前に、以下を確認してください：

- Python 3.8以上
- pipパッケージマネージャー
- Git（開発インストール用）

(quickstart-basic-installation)=

### 基本インストール

最も簡単な方法はpip経由でインストールすることです:

```
pip install docdiff
```

インストールを確認:

```
docdiff --version
```

(quickstart-development-installation)=

### 開発インストール

開発作業のために、クローンして編集可能モードでインストール：

```{code-block} bash
:caption: "\u958B\u767A\u30BB\u30C3\u30C8\u30A2\u30C3\u30D7"
:emphasize-lines: 3

git clone https://github.com/example/docdiff.git
cd docdiff
pip install -e .  # これが重要な行です
```

(quickstart-configuration)=

## 設定

(quickstart-initial-setup)=

### 初期セットアップ

設定ファイルを作成：

```{code-block} yaml
:caption: config.yaml
:name: basic-config

# 基本設定
parser:
  format: restructuredtext
  strict: false

output:
  format: json
  pretty: true

cache:
  enabled: true
  directory: ~/.docdiff/cache
```

(quickstart-environment-variables)=

### 環境変数

環境変数も使用できます：

```{eval-rst}
.. list-table:: 環境変数
   :widths: 25 25 50
   :header-rows: 1

   * - 変数
     - デフォルト
     - 説明
   * - DOCDIFF_CONFIG
     - ./config.yaml
     - 設定ファイルへのパス
   * - DOCDIFF_CACHE
     - ~/.docdiff
     - キャッシュディレクトリの場所
   * - DOCDIFF_LOG_LEVEL
     - INFO
     - ログレベル（DEBUG、INFO、WARNING、ERROR）
```

(quickstart-basic-usage)=

## 基本的な使い方

(quickstart-parsing-documents)=

### ドキュメントの解析

単一のドキュメントを解析:

```
docdiff parse document.rst
```

ディレクトリを解析:

```
docdiff parse /path/to/docs/
```

:::{note}
パーサーはファイル拡張子に基づいてドキュメント形式を自動的に検出します
（reStructuredTextは.rst、Markdownは.md）。
:::

(quickstart-comparing-documents)=

### ドキュメントの比較

2つのバージョンを比較：

```bash
docdiff compare old.rst new.rst
```

ディレクトリを比較：

```bash
docdiff compare docs/v1/ docs/v2/
```

(quickstart-working-with-lists)=

## リストの操作

(quickstart-bullet-lists)=

### 箇条書きリスト

シンプルな箇条書きリスト：

- 最初の項目
- 2番目の項目
- 複数行にまたがる長い説明を持つ
  3番目の項目
- 4番目の項目

ネストされた箇条書きリスト：

- メイン項目1

  - サブ項目1.1
  - サブ項目1.2

- メイン項目2

  - サブ項目2.1

    - サブサブ項目2.1.1
    - サブサブ項目2.1.2

(quickstart-numbered-lists)=

### 番号付きリスト

シンプルな番号付きリスト：

1. 最初のステップ
2. 2番目のステップ
3. 3番目のステップ

サブ項目付き：

1. 準備

   1. 材料を集める
   2. 指示を読む
   3. 作業スペースを設定

2. 実行

   1. ステップバイステップガイドに従う
   2. 進捗を監視
   3. 必要に応じて調整

3. クリーンアップ

   1. ツールを保管
   2. 結果を文書化

(quickstart-definition-lists)=

### 定義リスト

パーサー

: ドキュメント構造を分析するコンポーネント

アナライザー

: 解析されたノードを処理して情報を抽出

レポーター

: 分析から人間が読める出力を生成

(quickstart-code-examples)=

## コード例

(quickstart-inline-code)=

### インラインコード

短いスニペットには `インラインコード` を使用、例えば `variable_name` や `function()`。

(quickstart-code-blocks)=

### コードブロック

Python例：

```{code-block} python
:emphasize-lines: 4,5
:linenos: true

def fibonacci(n):
    """n番目のフィボナッチ数を計算。"""
    if n <= 1:
        return n  # ベースケース
    return fibonacci(n-1) + fibonacci(n-2)  # 再帰ケース

# 使用例
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

JavaScript例：

```{code-block} javascript
:caption: async-example.js

async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('エラー:', error);
        throw error;
    }
}
```

(quickstart-literal-blocks)=

### リテラルブロック

ダブルコロンを使用したシンプルなリテラルブロック:

```
これはリテラルブロックです。
すべての空白が保持されます。
    インデントを含めて。
```

(quickstart-admonitions)=

## 注意事項

(quickstart-information-notes)=

### 情報ノート

:::{note}
これは、理解に重要ではないが役立つかもしれない
追加情報を提供するノートです。
:::

:::{tip}
時間を節約したりワークフローを改善できる
役立つヒントです。
:::

(quickstart-warnings-and-cautions)=

### 警告と注意

:::{warning}
これは遭遇する可能性のある潜在的な問題や
問題についての警告です。
:::

:::{caution}
意図しない結果をもたらす可能性があるため、
この操作を実行する際は注意してください。
:::

:::{danger}
このアクションは危険であり、データの損失や
システムの損傷をもたらす可能性があります。
:::

(quickstart-other-admonitions)=

### その他の注意事項

:::{important}
この情報は適切なシステム動作にとって重要です。
:::

:::{attention}
この情報に特に注意を払ってください。
:::

:::{hint}
これは一般的な問題を解決するのに役立つかもしれません。
:::

:::{error}
これはエラー条件とその解決方法を説明しています。
:::

(quickstart-tables)=

## テーブル

(quickstart-simple-table)=

### シンプルなテーブル

```{eval-rst}
.. table:: 機能比較
   :widths: auto

   ===============  =========  =========  =========
   機能             ベーシック  プロ       エンタープライズ
   ===============  =========  =========  =========
   ユーザー         5          50         無制限
   ストレージ       10GB       100GB      1TB
   サポート         メール     電話       24/7
   APIアクセス      なし       あり       あり
   カスタムドメイン なし       あり       あり
   ===============  =========  =========  =========
```

(quickstart-csv-table)=

### CSVテーブル

```{eval-rst}
.. csv-table:: パフォーマンスメトリクス
   :header: "操作", "時間 (ms)", "メモリ (MB)", "CPU (%)"
   :widths: 30, 20, 20, 20

   "解析", "45", "12.3", "25"
   "分析", "120", "45.6", "60"
   "生成", "30", "8.9", "15"
   "エクスポート", "15", "5.2", "10"
```

(quickstart-list-table)=

### リストテーブル

```{eval-rst}
.. list-table:: コマンドオプション
   :widths: 15 30 55
   :header-rows: 1
   :stub-columns: 1

   * - オプション
     - タイプ
     - 説明
   * - -v, --verbose
     - フラグ
     - 詳細出力を有効化
   * - -o, --output
     - 文字列
     - 出力ファイルパスを指定
   * - -f, --format
     - 選択
     - 出力形式（json、yaml、xml）
   * - --config
     - パス
     - 設定ファイルへのパス
```

(quickstart-cross-references)=

## 相互参照

(quickstart-internal-links)=

### 内部リンク

- {ref}`quickstart-guide` を参照（このページ）
- 設定の詳細は {ref}`basic-config` を確認
- 完全なインデックスは {ref}`main-index` をレビュー

(quickstart-document-links)=

### ドキュメントリンク

- {doc}`index` ページを読む
- {doc}`advanced` 機能を探索
- {doc}`api/index` のAPIドキュメント

(quickstart-footnotes)=

## 脚注

これは脚注付きの文です [^f1]。

自動的に番号付けされる番号付き脚注も使用できます [^footnote-1]。

引用は異なる構文を使用しますが似ています [^cite_cit2024]。

[^f1]: これは下部に表示される脚注テキストです。

[^footnote-1]: この脚注は自動的に番号付けされます。

[^cite_cit2024]: 例の引用、「作品のタイトル」、2024年。

(quickstart-images-and-figures)=

## 画像と図

(quickstart-simple-image)=

### シンプルな画像

```{image} _static/diagram.png
:align: center
:alt: "\u30B7\u30B9\u30C6\u30E0\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u56F3"
:width: 400px
```

(quickstart-figure-with-caption)=

### キャプション付きの図

:::{figure} _static/diagram.png
:align: center
:alt: "\u8A73\u7D30\u306A\u30B7\u30B9\u30C6\u30E0\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\
:  \u30E3"
:name: fig-architecture
:width: 500px

**図1:** すべてのコンポーネントとその相互作用を示す
完全なシステムアーキテクチャ。双方向のデータフローに注目してください。
:::

(quickstart-substitutions)=

## 置換

このドキュメントは {{ project }} バージョン {{ version }} 用で、{{ date }} に生成されました。

(quickstart-raw-output)=

## 生の出力

```{raw} html
<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
    <strong>HTMLノート:</strong> このコンテンツはHTML出力でのみ表示されます。
</div>
```

(quickstart-include-files)=

## ファイルのインクルード

他のファイルをインクルードできます：

% commented out as the file doesn't exist
% .. include:: ../README.rst
%    :start-line: 10
%    :end-line: 20

(quickstart-summary)=

## まとめ

以下の基本を学びました：

1. インストールと設定
2. 基本的なドキュメント操作
3. 様々なテキストフォーマットオプション
4. コードブロックと例
5. テーブルとリスト
6. 相互参照とリンク
7. 注意事項とノート

(quickstart-next-steps)=

### 次のステップ

- より多くの機能については {doc}`advanced` ガイドを試す
- 詳細なAPIドキュメントは {doc}`api/reference` を探索
- サポートのためにコミュニティフォーラムに参加

______________________________________________________________________

*最終更新: 2024年1月*

