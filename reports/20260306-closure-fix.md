# 作業サマリー: 09_closure.vmo テスト修正

**日付:** 2026-03-06  
**モデル:** claude-sonnet-4.6

---

## 完了したタスク

### 1. 問題の再評価

`reports/20260307-test-issues.md` の提案（E704 のみ修正）を再評価し、**2 つの根本問題**を特定:

| エラー | 原因 |
|-------|------|
| E704 | `let l:inc = function(...)` — `l:inc` が小文字始まりで funcref 保持不可 |
| E121 | ラムダが `s:` トップレベルにホイストされており、外側の `l:count` をキャプチャできない |

E704 のみ修正しても、呼び出し時に E121 (undefined variable) で依然 FAIL することを確認した上で、根本修正を実施。

### 2. 根本修正の実装 (`codegen.py`)

Vim 8+ の closure 機能を正しく利用する方針を採用:

**① `gen_lambda()` — inline 定義 + `closure` キーワード**

```python
# 変更前: indent_level = 0 に強制ホイスト、closure なし
self.indent_level = 0
self.emit(f"function! {fname}({params})")

# 変更後: 現在の indentation で inline 定義、ネスト時は closure キーワード付与
is_nested = self.function_depth > 0
closure_attr = " closure" if is_nested else ""
self.emit(f"function! {fname}({params}){closure_attr}")
self.indent_level += 1
```

**② `_emit_lambda_fn()` — 重複 emit バグの除去**

旧コードは関数定義を2回 emit していた（1回目: closure 付き、2回目: closure なし上書き）。  
2回目の重複コードブロック（約35行）を削除し、inline emit に統一。

**③ funcref 変数の自動キャピタライズ（E704 対応）**

新規追加したヘルパー:
- `_register_funcref_var(name)` — Lambda を代入する変数名を登録
- `_is_funcref_var(name)` — 登録済みかチェック
- `_cap_funcref_name(name)` — 先頭を大文字化して返す

適用箇所:
- `gen_var_decl()` — `let inc = () => { ... }` 形式
- `gen_stmt()` Assign 分岐 — `inc = () => { ... }` 形式（再代入）
- `_resolve_ident()` — `inc()` 呼び出し等、参照時に一貫してキャピタライズ

**生成コードの変化:**

```vim
" 変更前
function! s:__lambda_0()        ← スクリプトトップに hoisted
  let l:count = (l:count + 1)   ← l:count 未定義 → E121
endfunction
  let l:inc = function("s:__lambda_0")  ← E704

" 変更後
  function! s:__lambda_0() closure   ← inline、外側 l:count をキャプチャ
    let l:count = l:count + 1
    echo l:count
  endfunction
  let l:Inc = function("s:__lambda_0")  ← 大文字始まり、E704 解消
```

---

## 新規作成・変更したファイル

| ファイル | 種別 | 内容 |
|---------|------|------|
| `packages/vimmo-core/src/vimmo/codegen.py` | 変更 | gen_lambda / _emit_lambda_fn / funcref 追跡 |
| `reports/ADR-001-closure-inline-emit.md` | 新規作成 | 設計決定の記録 |
| `reports/20260306-claude-sonnet-4-6-summary.md` | 新規作成 | 本ファイル |

---

## テスト結果

`docker compose run --rm test` で実施:

```
Found 10 test cases.
Running test: 01_variables.vmo     ... PASS
Running test: 02_functions.vmo     ... PASS
Running test: 03_control_flow.vmo  ... PASS
Running test: 04_advanced.vmo      ... PASS
Running test: 05_async.vmo         ... PASS
Running test: 07_pipeline.vmo      ... PASS
Running test: 08_builtins.vmo      ... PASS
Running test: 09_closure.vmo       ... PASS  ← 修正済み (旧: FAIL)
Running test: 10_class.vmo         ... PASS
Running test: test_definition.vmo  ... PASS
----------------------------------------
✅ All tests passed.
```

---

## 次のステップ

- `06_import.vmo` の実装（モジュールパス解決が codegen で未実装のため保留中）
