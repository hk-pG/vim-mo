# ADR-001: Multi-line Lambda を inline 定義 + closure キーワードで生成する

**ステータス:** 承認済み  
**日付:** 2026-03-06

---

## 決定事項

`codegen.py` における multi-line lambda（Block body を持つラムダ）の生成戦略を、  
**スクリプトトップレベルへのホイスト** から **囲む関数の内部で inline 定義 + `closure` キーワード** に変更する。

---

## 背景と問題

### 旧戦略（ホイスト）

```vim
function! s:makeCounter()
  let l:count = 0
function! s:__lambda_0()        ← indent 0 にホイスト
  let l:count = (l:count + 1)   ← 独立した l: スコープ（キャプチャなし）
  echo l:count
endfunction
  let l:inc = function("s:__lambda_0")  ← E704: 小文字始まり
  call l:inc()
endfunction
```

2 つの問題が存在していた:

1. **E704 エラー**: `l:inc` のように小文字始まりの `l:` / `s:` 変数は funcref を保持できない
2. **クロージャ意味論の破綻**: ホイストされた `s:__lambda_0` は独自の `l:count` スコープを持ち、外側の `l:count` をキャプチャできない → E121 (undefined variable)

E704 だけを直す（変数名のキャピタライズのみ）では、E121 が残りテストは依然 FAIL する。

---

## 採用した解決策

### 新戦略（inline + closure）

```vim
function! s:makeCounter()
  let l:count = 0
  function! s:__lambda_0() closure   ← inline 定義 + closure キーワード
    let l:count = l:count + 1        ← 外の l:count をキャプチャ
    echo l:count
  endfunction
  let l:Inc = function("s:__lambda_0")  ← E704 対応: 大文字始まり
  call l:Inc()
  call l:Inc()
endfunction
```

- `function_depth > 0` のときは `closure` キーワードを付与し、現在の indentation で emit
- スクリプトトップレベル（`function_depth == 0`）のときは `closure` なしで emit
- funcref を代入する変数名は先頭を大文字化（E704 対応）
- 参照時も `_resolve_ident` でキャピタライズを適用

---

## 変更されたファイル

| ファイル | 変更内容 |
|---------|---------|
| `packages/vimmo-core/src/vimmo/codegen.py` | `gen_lambda()` inline 化、`_emit_lambda_fn()` 重複 emit 除去、funcref 変数追跡・キャピタライズ追加 |

### 主な変更点

- `__init__`: `_script_funcref_vars: set` 追加
- `_register_funcref_var()`, `_is_funcref_var()`, `_cap_funcref_name()` ヘルパー追加
- `gen_lambda()`: Block 分岐を inline emit + `closure` 対応に刷新
- `_emit_lambda_fn()`: 重複していた 2 回目の emit（旧ホイストコード）を削除
- `gen_var_decl()`: Lambda 代入時に funcref 登録 + キャピタライズ
- `gen_stmt()` Assign 分岐: 同上
- `_resolve_ident()`: `_cap_funcref_name()` を通じてキャピタライズを適用

---

## テスト結果

```
Found 10 test cases.
01_variables.vmo   ... PASS
02_functions.vmo   ... PASS
03_control_flow.vmo ... PASS
04_advanced.vmo    ... PASS
05_async.vmo       ... PASS
07_pipeline.vmo    ... PASS
08_builtins.vmo    ... PASS
09_closure.vmo     ... PASS  ← 修正済み
10_class.vmo       ... PASS
test_definition.vmo ... PASS
✅ All tests passed.
```
