# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

docdiffは、MyST/reStructuredTextドキュメントの多言語翻訳管理ツールです。文書を構造単位で解析し、翻訳状態を追跡することで、技術ドキュメントの国際化を支援します。

## 開発コマンド

### 依存関係管理とセットアップ
```bash
# 依存関係のインストール (uvを使用)
uv sync

# 開発環境のセットアップ
uv pip install -e .

# CLIツールの実行
uv run docdiff
```

### Sphinxドキュメントのビルド
```bash
# 英語ドキュメントのビルド
uv run sphinx-build -M html docs/en/ docs/en/_build/

# ビルド結果の確認
open docs/en/_build/html/index.html
```

### Python品質チェック
```bash
# コードフォーマット
uv run ruff format .

# リントチェックと自動修正
uv run ruff check . --fix

# 型チェック
uv run mypy .

# テスト実行
uv run pytest tests/

# 全品質チェックを一括実行
uv run ruff format . && uv run ruff check . --fix && uv run mypy . && uv run pytest tests/
```

## アーキテクチャ

### コア設計思想
- レイヤード・アーキテクチャを採用
- ドキュメントを論理的構造単位（セクション、コードブロック、図表など）で分離
- 文字数による機械的な分割は行わない
- 各構造要素の翻訳状態を管理（pending/translated/reviewed/outdated）

### 主要コンポーネント（計画中）
- **DocumentParser**: MyST/reStructuredText文書の構造解析
- **StructureDB**: 解析済み構造の永続化とクエリ
- **ReferenceTracker**: 相互参照の追跡と管理
- **TranslationState**: 翻訳状態の管理

### 技術スタック
- Python 3.12+
- Typer (CLI framework)
- Pydantic (データモデル)
- Sphinx (ドキュメント処理)
- myst-parser (MyST形式のパース)

## 開発指針

### 🚀 破壊的変更の推奨（重要）

**本プロジェクトは既存ユーザーが存在しない新規開発のため、以下の方針を厳守する：**

#### 後方互換性の排除
- 既存ユーザーがいないため、後方互換性の考慮は一切不要
- データマイグレーション・移行パスの実装を厳禁とする
- より良い設計のための破壊的変更を積極的に推奨
- APIやデータ構造の変更時に互換性レイヤーを作らない

#### レガシーコード排除の原則
- 非推奨（deprecated）コードの維持を禁止
- 互換性のためのアダプターやラッパーの実装を禁止
- 常に最新・最適な実装のみを保持
- 不要になったコードは即座に削除（コメントアウトも禁止）
- 「将来のため」「念のため」のコード保持を禁止

#### クリーンアーキテクチャの維持
- 技術的負債をゼロに保つ
- 実験的コードは別ブランチで管理し、mainブランチには持ち込まない
- リファクタリング時は過去の実装を完全に置き換える
- 古い実装との共存期間を設けない
- コードベースは常に「今書くならこう書く」状態を維持

#### 実装判断の優先順位
1. **最適性** - 現時点で最も良い実装を選択
2. **簡潔性** - シンプルで理解しやすいコード
3. **保守性** - 将来の変更が容易な設計
4. ~~互換性~~ - **考慮不要**

**この方針により、常に最新・最適なコードベースを維持し、開発速度と品質を最大化する。**

### コードスタイル
- Python 3.12以上の機能を活用
- 型ヒントを必須とする
- Pydanticモデルを使用したデータ検証

### ドキュメント構造の扱い
- セクションのラベリング（`:name:`）を保持
- ブロック要素の`caption`やname属性を維持
- Sphinxの相互参照システムに対応

### 翻訳管理の原則
- コンテンツ変更はハッシュベースで検知
- 増分更新に対応
- 翻訳単位は論理的な文書構造に基づく
- Pythonのソースコードのコメントは全て英語で記述する

### Git コミット規則
- コミットメッセージは必ず英語で記述する
- Conventional Commits形式に準拠: `[type]: [summary]`
- 使用可能なタイプ:
  - `feat`: 新機能追加
  - `fix`: バグ修正
  - `docs`: ドキュメント変更
  - `style`: コードスタイルの変更（動作に影響しない）
  - `refactor`: リファクタリング
  - `test`: テストの追加・修正
  - `chore`: ビルドプロセスやツールの変更

## Python品質管理

### 品質基準
本プロジェクトでは以下の品質基準を厳守します：

#### 必須基準（マージブロッカー）
- ruffエラー: 0件
- mypy型エラー: 0件
- テスト成功率: 100%
- 構文エラー: 0件

#### 推奨基準
- テストカバレッジ: > 80%
- 型アノテーション率: 100%
- docstring記載率: > 90%
- 複雑度スコア: < 10

### 品質チェック自動化
コード変更時は必ず品質チェックを実行し、すべてのエラーをゼロにしてからコミットしてください。
詳細な品質チェック手順とエラー自動修正については、以下のドキュメントを参照：

**@.claude/commands/python-quality-check.md**

このドキュメントには以下が含まれています：
- 完全自動化された品質チェックフロー
- エラー検出時の自動修正ループ
- 各種エラーの具体的な対処法
- トラブルシューティングガイド

### コミット前チェックリスト
```bash
# コミット前の必須チェック
echo "コミット前チェックリスト:"
echo -n "1. フォーマット完了: "; uv run ruff format . --check && echo "✓" || echo "✗"
echo -n "2. リントエラーなし: "; uv run ruff check . --quiet && echo "✓" || echo "✗"
echo -n "3. 型チェック通過: "; uv run mypy . --no-error-summary 2>/dev/null && echo "✓" || echo "✗"
echo -n "4. テスト全通過: "; uv run pytest tests/ -q 2>/dev/null && echo "✓" || echo "✗"
```