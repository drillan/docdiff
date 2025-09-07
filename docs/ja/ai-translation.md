(ai-translation)=
# AI翻訳ガイド

コスト効率的で高品質な文書翻訳のための、docdiffのAI翻訳最適化機能を使用する完全ガイド。

(ai-translation-overview)=
## 概要

docdiffは、インテリジェントなバッチ最適化により、文脈の保持と用語集の強制を通じて翻訳品質を維持しながら、コストを約70%削減するAI駆動翻訳を革新します。

(ai-translation-key-benefits)=
## 主な利点

- **81%のバッチ効率**: 各バッチでの最適なトークン利用
- **69%のAPI呼び出し削減**: 数百回から数十回の呼び出しへ
- **約70%のコスト削減**: 翻訳費用の大幅な削減
- **品質向上**: 用語の一貫性を保つ文脈対応翻訳
- **高速処理**: 並列バッチ処理機能

(ai-translation-how-it-works)=
## 仕組み

(ai-translation-algorithm)=
### 最適化アルゴリズム

```{code-block} text
:name: ai-text-optimization-flow
:caption: バッチ最適化フロー

┌─────────────────────┐
│ 497個の文書ノード    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  トークン推定        │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ インテリジェント統合 │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ セクション境界       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  文脈追加           │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 40個の最適化バッチ   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   81%の効率         │
└─────────────────────┘
```

AdaptiveBatchOptimizerは以下の手順に従います：

1. **トークン推定**: 各ノードの正確なトークン数を計算
2. **インテリジェント統合**: 小さなノードを組み合わせて最適なバッチサイズに到達
3. **境界の尊重**: 意味的単位を一緒に保持
4. **文脈の充実**: より良い翻訳のために周囲のノードを追加
5. **バッチ作成**: 500-2000トークンの最適化されたバッチを生成

(ai-translation-performance)=
### パフォーマンス比較

```{code-block} text
:name: ai-code-performance-comparison
:caption: 最適化前後の比較

従来のアプローチ（API呼び出しあたり1ノード）:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ノード数:        497
API呼び出し:     497
平均トークン:    45（呼び出しあたり）
効率:           2.2%
総コスト:       $$$$（ベースライン）

最適化アプローチ（適応バッチング）:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ノード数:        497
API呼び出し:     40
平均トークン:    1,532（呼び出しあたり）
効率:           81%
総コスト:       $（約70%削減）
```

(ai-translation-quickstart)=
## クイックスタート

(ai-translation-basic-usage)=
### 基本使用方法

自動最適化によるAI翻訳用の文書をエクスポート：

```{code-block} bash
:name: ai-code-basic-export
:caption: 基本的なAI翻訳エクスポート

# デフォルト最適化でエクスポート
docdiff export docs/en docs/ja translation.json

# 出力には以下が含まれます:
# - 階層的JSON構造（スキーマv1.0）
# - 最適化されたバッチ（81%効率）
# - 文書階層の保持
# - 自動トークン推定
```

(ai-translation-advanced-usage)=
### 高度な使用方法

特定のニーズに合わせて最適化を微調整：

```{code-block} bash
:name: ai-code-advanced-export
:caption: 高度なAI翻訳エクスポート

# すべての機能を使った完全最適化
docdiff export docs/en docs/ja translation.json \
  --include-context \           # 周囲の文脈を追加
  --context-window 5 \          # 前後5ノード
  --batch-size 1500 \          # 目標バッチサイズ
  --glossary terms.yml \       # 用語の一貫性
  --verbose                    # 最適化レポートを表示
```

(ai-translation-configuration)=
## 設定

(ai-translation-batch-sizes)=
### バッチサイズの選択

AIモデルに最適なバッチサイズを選択：

| モデル | 推奨サイズ | 範囲 | 備考 |
|-------|-----------|------|------|
| GPT-4 | 1500トークン | 1000-2000 | 最適なバランス |
| GPT-3.5 | 2000トークン | 1500-2500 | より高いスループット |
| Claude | 1500トークン | 1000-2000 | 品質重視 |
| カスタム | 1000トークン | 500-1500 | 保守的 |

(ai-translation-context-windows)=
### 文脈ウィンドウ設定

文脈は翻訳品質を向上させます：

- **最小（1-2ノード）**: 高速、基本的な文脈
- **標準（3-5ノード）**: ほとんどのコンテンツに推奨
- **拡張（6-10ノード）**: 複雑な技術文書

(ai-translation-glossary)=
## 用語集管理

(ai-translation-create-glossary)=
### 用語集の作成

翻訳間での用語の一貫性を確保：

```{code-block} yaml
:name: ai-code-glossary-yaml
:caption: glossary.yml例

# 一貫性を保つ技術用語
terms:
  - term: API
    definition: Application Programming Interface
    translation: API  # 原文を保持
    maintain_original: true
    
  - term: docdiff
    definition: Document diff and translation tool
    maintain_original: true
    
  - term: batch optimization
    definition: Process of grouping items efficiently
    translation: バッチ最適化
    maintain_original: false
    
  - term: token
    definition: Unit of text for AI processing
    translation: トークン
    aliases: [tokens, tokenize, tokenization]
```

(ai-translation-extract-glossary)=
### Sphinxからの抽出

既存の文書から用語集を自動抽出：

```{code-block} bash
:name: ai-code-extract-glossary
:caption: Sphinx用語集の抽出

# Sphinx文書から用語集用語を抽出
docdiff extract-glossary docs/en --output glossary.yml

# 既存の用語集とマージ
docdiff merge-glossary existing.yml extracted.yml --output combined.yml
```

(ai-translation-integration)=
## AIサービスとの統合

(ai-translation-openai)=
### OpenAI GPT統合

```{code-block} python
:name: ai-code-openai-integration
:caption: OpenAI統合例

import json
import openai
from pathlib import Path

# 最適化されたバッチを読み込み
with open("translation.json") as f:
    data = json.load(f)

# 各バッチを処理
for batch in data["translation_batches"]:
    # 文脈付きプロンプトを準備
    prompt = f"""
    技術文書を{data['metadata']['source_lang']}から{data['metadata']['target_lang']}に翻訳してください。
    フォーマットと技術的精度を保ってください。
    
    バッチ {batch['batch_id']} （{batch['section_range']}）:
    推定トークン数: {batch['estimated_tokens']}
    
    翻訳するコンテンツ:
    {get_batch_content(batch['node_ids'])}
    """
    
    # OpenAIに送信
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # 一貫性のため低めに設定
        max_tokens=batch['estimated_tokens'] * 2
    )
    
    # 翻訳を保存
    save_translation(batch['batch_id'], response.choices[0].message.content)
```

(ai-translation-metrics)=
## メトリクスの理解

(ai-translation-optimization-report)=
### 最適化レポート

`--verbose`使用時の詳細メトリクス：

```{code-block} text
:name: ai-code-optimization-report
:caption: サンプル最適化レポート

適応バッチ最適化レポート
===================================
総ノード数:         497
総バッチ数:         40
バッチ効率:         81.0%

トークン統計:
  平均:             1532トークン/バッチ
  最小:             502トークン
  最大:             1998トークン
  目標:             1500-2000トークン

最適化結果:
  API呼び出し削減:  457回 (92.0%削減)
  トークン オーバーヘッド: 8.0%（優秀）
  コスト削減:       約70%
  
ファイルグループ:
  index.md:          3バッチ
  user-guide.md:     8バッチ
  architecture.md:   12バッチ
  api-reference.md:  10バッチ
  developer-guide.md: 7バッチ

ステータス: ✅ 最適
```

(ai-translation-efficiency-levels)=
### 効率レベル

- **✅ 最適（80%+）**: 優秀なバッチ利用
- **⚠️ 準最適（60-79%）**: 良いが改善可能
- **❌ 不良（60%未満）**: 設定調整が必要

(ai-translation-best-practices)=
## ベストプラクティス

(ai-translation-tips)=
### 最適化のヒント

1. **技術文書には文脈を使用**: 周囲の3-5ノードを含める
2. **用語集を維持**: 言語間での用語の一貫性を保つ
3. **類似コンテンツをバッチ化**: 関連するセクションを一緒にグループ化
4. **メトリクスを監視**: 効率を追跡してバッチサイズを調整
5. **小さなセットでテスト**: 完全翻訳前に品質を検証

(ai-translation-common-issues)=
### 一般的な問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 低効率 | バッチサイズが大きすぎる | `--batch-size`を削減 |
| API呼び出し数が多い | バッチサイズが小さすぎる | `--batch-size`を増加 |
| 品質が悪い | 文脈が不足 | `--include-context`を使用 |
| 用語が一貫しない | 用語集なし | `--glossary`を追加 |
| フォーマットが破損 | パーサーの問題 | ソースフォーマットを確認 |

(ai-translation-workflow-example)=
## 完全ワークフロー例

```{code-block} bash
:name: ai-code-complete-workflow
:caption: エンドツーエンドAI翻訳ワークフロー

# ステップ1: 現在の状態を分析
docdiff compare docs/en docs/ja --output status.md

# ステップ2: ソースから用語集を抽出
docdiff extract-glossary docs/en --output terms.yml

# ステップ3: 完全最適化でエクスポート
docdiff export docs/en docs/ja translation.json \
  --include-context \
  --context-window 5 \
  --batch-size 1500 \
  --glossary terms.yml \
  --verbose

# ステップ4: AI翻訳サービスに送信
python translate_with_ai.py translation.json

# ステップ5: 完了した翻訳をインポート
docdiff import translation_complete.json docs/ja

# ステップ6: 結果を検証
docdiff compare docs/en docs/ja --output final_status.md
```

(ai-translation-cost-calculator)=
## コスト計算機

削減額を推定：

```{code-block} python
:name: ai-code-cost-calculator
:caption: 翻訳コスト計算機

def calculate_savings(nodes: int, avg_node_size: int = 200):
    """最適化によるコスト削減を計算する。"""
    
    # 従来のアプローチ
    traditional_calls = nodes
    traditional_tokens = nodes * avg_node_size
    traditional_cost = traditional_calls * 0.002  # 呼び出しあたり$0.002
    
    # 最適化アプローチ
    optimized_calls = nodes // 12  # 約92%削減
    optimized_tokens = traditional_tokens  # 総トークン数は同じ
    optimized_cost = optimized_calls * 0.002
    
    savings = traditional_cost - optimized_cost
    savings_percent = (savings / traditional_cost) * 100
    
    print(f"従来: ${traditional_cost:.2f} ({traditional_calls}回の呼び出し)")
    print(f"最適化: ${optimized_cost:.2f} ({optimized_calls}回の呼び出し)")
    print(f"削減額: ${savings:.2f} ({savings_percent:.0f}%)")
    
# 例: 500ノードの文書
calculate_savings(500)
# 出力:
# 従来: $1.00 (500回の呼び出し)
# 最適化: $0.08 (41回の呼び出し)
# 削減額: $0.92 (92%)
```

(ai-translation-summary)=
## まとめ

docdiffのAI翻訳最適化は以下を提供します：

- インテリジェントバッチングによる**大幅なコスト削減**
- 文脈保持による**より良い翻訳品質**
- 用語集管理による**一貫した用語**
- 大規模での**本番対応**パフォーマンス
- 任意のAI翻訳サービスとの**簡単な統合**

docdiffの高度な最適化で今日から翻訳コストの節約を始めましょう！