# ADR-005: Neovim nvim-treesitter シンタクスハイライト修正

## ステータス

承認済み

## 背景

`packages/tree-sitter-vimmo/` として Tree-sitter グラマーを実装済みだったが、Neovim で `.vmo` ファイルを開いてもシンタクスハイライトが効いていなかった。調査の結果、以下の3つの問題が発覚した。

## 問題点

### 問題1: queries/ のサブディレクトリ不在

nvim-treesitter はクエリファイルを `$RUNTIMEPATH/queries/{lang}/highlights.scm` のパスで探す。しかし既存の構造は `queries/highlights.scm`（lang サブディレクトリなし）だったため、Neovim にクエリが認識されなかった。

### 問題2: runtimepath 未登録

`/app/packages/tree-sitter-vimmo` が Neovim の runtimepath に含まれていなかったため、クエリファイル自体が検索対象外だった。

### 問題3: highlights.scm の無効なクエリパターン

以下の2種類のクエリが Neovim の tree-sitter で Invalid/Impossible pattern エラーを引き起こしていた:

1. `(break_statement "break" @keyword)` — grammar.js で `break_statement` は子ノードなしのリテラルトークンのため、`"break"` 子ノード参照が Invalid
2. `(binary_expression operator: _ @operator)` — `binary_expression` は `operator` フィールドを定義していないため、フィールド参照が Impossible

## 決定事項

### 対応1: `queries/vimmo/` サブディレクトリを追加

`queries/highlights.scm` / `queries/locals.scm` を `queries/vimmo/` にも配置（元ファイルは互換性のため残存）。

### 対応2: runtimepath への追加

`docker/lua/plugins/treesitter.lua` に `vim.opt.runtimepath:append("/app/packages/tree-sitter-vimmo")` を追加。

### 対応3: クエリパターンを修正

- `(break_statement) @keyword` / `(continue_statement) @keyword` — ノード自体にキャプチャ
- 演算子を `[ "|>" "=>" "||" ... ] @operator` のトークンリスト形式に変更

## 変更されたファイル

- `packages/tree-sitter-vimmo/queries/vimmo/highlights.scm` (新規)
- `packages/tree-sitter-vimmo/queries/vimmo/locals.scm` (新規)
- `packages/tree-sitter-vimmo/queries/highlights.scm` (クエリパターン修正)
- `docker/lua/plugins/treesitter.lua` (runtimepath 追加)
- `Dockerfile` (lazy.nvim headless sync + TSInstall をビルドに含める)

## テスト結果

Neovim で `example_plugin.vmo` を開き、シンタクスハイライトが正常に動作することを確認。
