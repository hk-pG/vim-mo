# VimMo

VimMoはTypeScript-like言語をVimScriptにコンパイルするトランスパイラーです。
詳細な言語仕様は [DESIGN.md](DESIGN.md) を参照してください。

```vmo
fn greet(name: string): string {
  return "Hello, " .. name .. "!"
}

let nums = [1, 2, 3, 4, 5]
let doubled = nums |> filter((x) => x % 2 == 0) |> map((x) => x * 2)

echo greet("VimMo")
```

## 前提条件

- Python 3.14+
- Vim（テスト実行時）

## クイックスタート

### コンパイル

```bash
cd packages/vimmo-core
PYTHONPATH=src python src/vimmo/vimmo.py compile input.vmo -o output.vim
```

### その他のCLIコマンド

```bash
# 構文チェックのみ
PYTHONPATH=src python src/vimmo/vimmo.py check input.vmo

# トークン列を表示（デバッグ用）
PYTHONPATH=src python src/vimmo/vimmo.py tokens input.vmo

# ASTを表示（デバッグ用）
PYTHONPATH=src python src/vimmo/vimmo.py ast input.vmo
```

### LSPサーバー（Neovim）

#### インストール

```bash
cd packages/vimmo-ls
pip install -e .
```

#### Neovim設定（AstroNvim）

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
