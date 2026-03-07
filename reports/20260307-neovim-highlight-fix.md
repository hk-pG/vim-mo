**モデル:** claude-sonnet-4.6

# 20260307 - neovim-highlight-fix

## 完了したタスク

Neovim nvim-treesitter によるシンタクスハイライトが動作しなかった問題を修正した。

## 原因と修正内容

| 問題 | 修正 |
|------|------|
| クエリが `queries/vimmo/` サブディレクトリに存在しなかった | `queries/vimmo/highlights.scm` / `locals.scm` を新規作成 |
| `/app/packages/tree-sitter-vimmo` が runtimepath 未登録 | `treesitter.lua` に `vim.opt.runtimepath:append(...)` を追加 |
| `(break_statement "break" @keyword)` — Invalid node type | `(break_statement) @keyword` に修正 |
| `(binary_expression operator: _ @operator)` — Impossible pattern | トークンリスト `[ "||" "&&" ... ] @operator` に変更 |
| 初回 Neovim 起動でプラグイン未インストール | Dockerfile に `nvim --headless "+Lazy! sync"` と `TSInstall! vimmo` を追加 |

## 新規作成/変更したファイル

| ファイル | 変更種別 |
|---------|---------|
| `packages/tree-sitter-vimmo/queries/vimmo/highlights.scm` | 新規作成 |
| `packages/tree-sitter-vimmo/queries/vimmo/locals.scm` | 新規作成 |
| `packages/tree-sitter-vimmo/queries/highlights.scm` | クエリパターン修正 |
| `docker/lua/plugins/treesitter.lua` | runtimepath 追加 |
| `Dockerfile` | lazy.nvim + TSInstall headless 実行を追加 |
| `reports/ADR-005-neovim-treesitter-highlight.md` | ADR 新規作成 |

## テスト結果

Neovim で `example_plugin.vmo` を開き、シンタクスハイライトが正常に動作することを確認 ✅

## 次のステップ

- VS Code Extension Development Host での TextMate ハイライト確認
- Marketplace 公開準備
