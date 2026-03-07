# ADR-004: シンタクスハイライト実装（VS Code + Neovim）

## ステータス

承認済み（更新: Neovim Tree-sitter サポート追加）

## 背景

VimMo は `.vmo` 拡張子を持つ TypeScript 風言語。Neovim 上での動作を前提としているため、TextMate 文法（VS Code 専用）だけでなく、Neovim が採用している Tree-sitter グラマーも必要とされていた。

初回実装（VS Code 向け TextMate 文法）に対し「Tree-sitter で動作するか」という指摘を受け、`packages/tree-sitter-vimmo/` として Tree-sitter グラマーを追加した。

## 決定事項

### 1. VS Code 向け: TextMate 文法（`packages/vscode-vimmo/`）

`package.json` には既に参照が記述されていたが、ファイルが欠落していたため以下を追加:

- `syntaxes/vimmo.tmLanguage.json` — TextMate 文法（スコープ名 `source.vmo`）
- `language-configuration.json` — ブラケット補完・インデント・コメント設定

### 2. Neovim 向け: Tree-sitter グラマー（`packages/tree-sitter-vimmo/`）

nvim-treesitter と統合するための Tree-sitter グラマーパッケージを新設:

- `grammar.js` — 言語文法定義（`tree-sitter generate` でパーサーを再生成可能）
- `src/parser.c` — コンパイル済みCパーサー（コミット済みのため再コンパイル不要）
- `queries/highlights.scm` — Neovim ハイライトクエリ
- `queries/locals.scm` — スコープ・定義・参照クエリ
- `README.md` — nvim-treesitter セットアップ手順

## 文法カバレッジ

Tree-sitter グラマーは全テストケース（`packages/vimmo-core/tests/cases/*.vmo`）をエラーなくパース。

## 変更されたファイル

- `packages/vscode-vimmo/syntaxes/vimmo.tmLanguage.json` (新規)
- `packages/vscode-vimmo/language-configuration.json` (新規)
- `packages/tree-sitter-vimmo/` (新規パッケージ)

## テスト結果

```
01_variables.vmo: 0 error(s)
02_functions.vmo: 0 error(s)
03_control_flow.vmo: 0 error(s)
04_advanced.vmo: 0 error(s)
05_async.vmo: 0 error(s)
06_import.vmo: 0 error(s)
07_pipeline.vmo: 0 error(s)
08_builtins.vmo: 0 error(s)
09_closure.vmo: 0 error(s)
10_class.vmo: 0 error(s)
test_definition.vmo: 0 error(s)
```

