**モデル:** Claude Sonnet 4.6

# デバッグ記録: vimmo-ls Neovim LSP 修正

**日付**: 2026-03-08  
**ステータス**: 解決済み ✅

---

## 解決した問題一覧

### 問題1: `Workspace.get_document` AttributeError（→ 解決済み）

**原因**: pygls 2.x で `ls.workspace.get_document(uri)` が廃止  
**修正**: 全3箇所を `ls.workspace.text_documents.get(uri)` に変更し、`None` チェックを追加  
**ファイル**: `packages/vimmo-ls/src/vimmo_ls/server.py`

### 問題2: `show_message` / `publish_diagnostics` AttributeError（→ 解決済み）

**原因**: `pygls.lsp.server.LanguageServer` にこれらのメソッドが存在しない  
**修正**:
- import を `pygls.server.LanguageServer` 優先・`pygls.lsp.server` フォールバックに変更
- `_show_message()` / `_publish_diagnostics()` 互換ラッパーを追加
- `_publish_diagnostics` は `ls.protocol.notify("textDocument/publishDiagnostics", ...)` 経由で動作  
**ファイル**: `packages/vimmo-ls/src/vimmo_ls/server.py`

### 問題3: 定義ジャンプが効かない（→ 解決済み）

**原因1**: Lexer の `line` / `col` が 1-ベース、LSP の `position` は 0-ベース → シンボル登録時の比較がすべてズレていた  
**修正**: `_to_lsp_line()` / `_to_lsp_col()` ヘルパーを追加し全シンボル登録箇所で変換  

**原因2**: `ClassDecl` の `_walk` でフィールド・メソッドを再帰処理していなかった → クラスフィールドが `definitions` に未登録  
**修正**: `ClassDecl` ブロックに `node.fields` / `node.methods` を `_walk` するループを追加  

**原因3**: `FnDecl` の `body` を `_walk` していなかった → 関数内ローカル変数が未登録  
**修正**: `FnDecl` ブロックに `_walk(node.body, table)` を追加  

**ファイル**: `packages/vimmo-ls/src/vimmo_ls/symbols.py`

### 問題4: 診断（構文エラー赤線）が届かない（→ 解決済み）

**原因**: pygls 2.x では `ls.publish_diagnostics()` が削除され、`ls.protocol.notify()` が正しい API  
**修正**: `_publish_diagnostics` ラッパーを `ls.protocol.notify("textDocument/publishDiagnostics", params)` 優先に変更  
**ファイル**: `packages/vimmo-ls/src/vimmo_ls/server.py`

---

## 変更ファイル一覧

| ファイル | 内容 |
|---|---|
| `packages/vimmo-ls/src/vimmo_ls/server.py` | `get_document` 修正、`_show_message` / `_publish_diagnostics` 互換ラッパー追加、デバッグログ整備 |
| `packages/vimmo-ls/src/vimmo_ls/symbols.py` | 1-ベース→0-ベース変換、ClassDecl フィールド/メソッド登録、FnDecl body walk 追加 |
| `packages/vimmo-ls/tests/test_build_symbol_table.py` | 期待値を 0-ベースに修正 |
| `.gitignore` | `vimmo-ls.log` を除外に追加 |

## テスト結果

全39件 PASS

## 最終動作確認（ログより）

| 機能 | 状態 |
|---|---|
| キーワード・変数・関数補完 | ✅ |
| `.` によるメソッド/フィールド補完 | ✅ |
| 定義ジャンプ (`gd`) | ✅ |
| 診断（構文エラー赤線） | ✅ |
