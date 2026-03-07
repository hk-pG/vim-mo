# tree-sitter-vimmo

[Tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar for the [VimMo](https://github.com/hk-pG/vim-mo) language (`.vmo` files).

## Neovim (nvim-treesitter) のセットアップ

### 1. nvim-treesitter のインストール

[nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter) を使って Tree-sitter 対応エディタに登録します。
`lazy.nvim` の例:

```lua
require("nvim-treesitter.configs").setup({
  ensure_installed = { "vimmo" },   -- 下の手順でカスタム登録後に使用可能
})
```

### 2. カスタムグラマーの登録

Neovim の設定ファイル（`init.lua` 等）に以下を追記します:

```lua
local parser_config = require("nvim-treesitter.parsers").get_parser_configs()
parser_config.vimmo = {
  install_info = {
    url = "https://github.com/hk-pG/vim-mo",
    -- サブディレクトリを指定
    subdirectory = "packages/tree-sitter-vimmo",
    files = { "src/parser.c" },
  },
  filetype = "vmo",
}

-- .vmo ファイルタイプを vimmo として認識させる
vim.filetype.add({ extension = { vmo = "vmo" } })
```

### 3. パーサーのインストール

Neovim を起動後:

```vim
:TSInstall vimmo
```

これでシンタクスハイライト・`nvim-treesitter` の各機能（折り畳み、インデント、テキストオブジェクト等）が有効になります。

## ローカルビルド（開発者向け）

```bash
cd packages/tree-sitter-vimmo
npm install
npm run build   # tree-sitter generate を実行して src/parser.c を再生成
```

`tree-sitter-cli` が必要です（`npm install -g tree-sitter-cli`）。

## 対応機能

| ファイル | 内容 |
|---------|------|
| `grammar.js` | 言語文法定義 |
| `src/parser.c` | コンパイル済みパーサー（C） |
| `queries/highlights.scm` | シンタクスハイライトクエリ |
| `queries/locals.scm` | スコープ・定義・参照クエリ |
