# AI Workspace Directory

このディレクトリはAI（Claude Code等）が作業時に使用する専用領域です。

## ⚠️ 重要事項
- **このディレクトリ内のファイルはすべてGit管理対象外です**
- **一時的な作業ファイルのみを配置してください**
- **恒久的なファイルは適切な場所に移動してください**

## 📁 ディレクトリ構造

```
.ai-workspace/
├── README.md          # このファイル（削除禁止）
├── tmp/              # 一時ファイル用
├── reports/          # 生成レポート用
├── experiments/      # 実験・テスト用
└── scripts/          # 一時スクリプト用
```

### 各ディレクトリの用途

| ディレクトリ | 用途 | 例 |
|------------|------|-----|
| `tmp/` | 一時的な作業ファイル | `output.txt`, `data.json` |
| `reports/` | 生成されたレポート | `translation-status.md`, `analysis.csv` |
| `experiments/` | テスト・実験用のファイル/ディレクトリ | `test_readme/`, `sample_data/` |
| `scripts/` | 一時的なスクリプト | `analyze.py`, `convert.sh` |

## 🧹 クリーンアップ

定期的に以下のコマンドで整理可能：

```bash
# すべての一時ファイルを削除（このREADME.mdは保持）
find .ai-workspace -type f -not -name "README.md" -delete
find .ai-workspace -type d -empty -delete
```

特定のディレクトリのみクリーンアップ：

```bash
# tmpディレクトリのみクリア
rm -rf .ai-workspace/tmp/*

# reportsディレクトリのみクリア
rm -rf .ai-workspace/reports/*
```

## 📝 使用例

### 一時ファイルの作成
```bash
# ❌ 悪い例（プロジェクトルートに作成）
echo "test" > test_output.txt

# ✅ 良い例（AI workspaceに作成）
echo "test" > .ai-workspace/tmp/output.txt
```

### テスト用ディレクトリの作成
```bash
# ❌ 悪い例
mkdir test_readme

# ✅ 良い例
mkdir -p .ai-workspace/experiments/test_readme
```

### レポートの生成
```bash
# ❌ 悪い例
docdiff compare . . --output translation-report.md

# ✅ 良い例
docdiff compare . . --output .ai-workspace/reports/translation-report.md
```

## 🚨 注意事項

1. **このディレクトリはGit管理対象外です** - 重要なファイルは保存しないでください
2. **定期的にクリーンアップされる可能性があります**
3. **恒久的に必要なファイルは適切な場所に移動してください**：
   - ドキュメント → `docs/`
   - テストファイル → `tests/`
   - ソースコード → `src/`
   - サンプル → `samples/`

## 💡 Tips

- 作業開始時に `ls -la .ai-workspace/*/` で既存ファイルを確認
- 作業終了時に不要なファイルをクリーンアップ
- 大きなファイルは特に注意して管理（ディスク容量の無駄遣いを防ぐ）

---

このディレクトリは開発効率を向上させ、プロジェクトルートをクリーンに保つために設計されています。