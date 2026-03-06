# VimMo テスト問題詳細

**作成日:** 2026-03-07  
**最終更新:** 2026-03-07  
**状況:** 11/11 テストパス（全件解決済み）

---

## 1. 解決済みの問題

### 1.1 09_closure.vmo — E704/E121 エラー（解決済み）

**コミット:** `ac2d50d` `fix(codegen): multi-line lambda を inline 定義 + closure キーワードに変更`

**元のエラーメッセージ:**
```
Vim(let):E704: Funcref variable name must start with a capital: l:inc
```

**解決内容:**

- `_register_funcref_var()` / `_is_funcref_var()` / `_cap_funcref_name()` を追加し、funcref 変数を自動キャピタライズ（`l:inc` → `l:Inc`）
- multi-line lambda をスクリプトトップへのホイストから、囲む関数内の inline 定義に変更（E121 対策）
- `function_depth > 0` のとき `closure` キーワードを付与（E932 対策）
- 設計記録: `reports/ADR-003-closure-inline-emit.md`

---

### 1.2 06_import.vmo — モジュールインポート未実装（解決済み）

**コミット:** `3d43bde` `feat(codegen): import文のインポート名をグローバルスコープで解決`

**解決内容:**

- `Codegen._imported_names` セットを追加
- `gen_import()` でインポート名を `_imported_names` に登録
- `_resolve_ident()` でインポート名はスコーププレフィックスなし（グローバル）で解決
- `06_utils.vim` を追加
- `06_import.vmo` テストケースを追加

---

## 2. テスト一覧 (現在)

| ファイル | 状態 | メモ |
|---------|------|------|
| 01_variables.vmo | ✅ PASS | |
| 02_functions.vmo | ✅ PASS | |
| 03_control_flow.vmo | ✅ PASS | |
| 04_advanced.vmo | ✅ PASS | |
| 05_async.vmo | ✅ PASS | |
| 06_import.vmo | ✅ PASS | `3d43bde` で実装・追加 |
| 07_pipeline.vmo | ✅ PASS | |
| 08_builtins.vmo | ✅ PASS | |
| 09_closure.vmo | ✅ PASS | `ac2d50d` で E704/E121 修正 |
| 10_class.vmo | ✅ PASS | |
| test_definition.vmo | ✅ PASS | LSPテスト |

---

## 3. 技術メモ

### VimScript funcref制約

- 変数名が `g:` で始まる: 大文字小文字OK
- 変数名が `l:` で始まる: **大文字必須**
- 変数名が `s:` で始まる: **大文字必須**
- 変数名が接頭辞なし: **大文字必須**

参考: `:help E704`

### Lambda → VimScript変換（現在のパターン）

1. **Expression body** (`(x) => x * 2`) → Vim ネイティブラムダ `{x -> x * 2}` に変換
2. **Block body** (`() => { ... }`) → 囲む関数内に `function! s:__lambda_N() closure` として inline 定義
3. funcref を保持する変数は `_register_funcref_var()` で登録し `_cap_funcref_name()` でキャピタライズ

---

## 4. 解決履歴

| 日付 | コミット | 内容 |
|------|---------|------|
| 2026-03-06 | `ac2d50d` | `09_closure.vmo` の E704/E121 修正（funcref キャピタライズ + inline lambda）|
| 2026-03-06 | `3d43bde` | `06_import.vmo` の実装（import 文のグローバルスコープ解決）|

---

## 5. 次アクション

- [ ] Tree-sitter grammar.js 作成
- [ ] シンタックスハイライト実装（Neovim / VS Code）
- [ ] LSP 補完機能
- [ ] LSP Hover 機能
- [ ] 型システム基盤
- [ ] コードフォーマッター
