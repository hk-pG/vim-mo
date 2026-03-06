# VimMo

VimMoはTypeScript-like言語をVimScriptにコンパイルするトランスペイラーです。

## クイックスタート

### コンパイル

```bash
cd packages/vimmo-core
PYTHONPATH=src python src/vimmo/vimmo.py compile input.vmo -o output.vim
```

### LSPサーバー（Neovim）

#### インストール

```bash
cd packages/vimmo-ls
pip install -e .
```

#### Neovim設定 (AstroNvim)

`lua/plugins/astrolsp.lua` に以下を追加:

```lua
require("lspconfig").vimmo.setup({
  cmd = { "python", "-m", "vimmo_ls.server" },
  filetypes = { "vimmo" },
})
```

#### ファイルタイプ設定 (任意)

`lua/plugins/astrocoder.lua` または個人設定ファイルに:

```lua
vim.filetype.add({
  extension = {
    vmo = "vimmo",
  },
})
```

#### 機能

- 診断（エラーハイライト）
- 定義ジャンプ (Go to Definition)

## テスト

```bash
python tests/run_tests.py
```
