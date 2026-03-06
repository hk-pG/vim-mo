# VimMo テスト問題詳細

**作成日:** 2026-03-07  
**状況:** 9/10 テストパス

---

## 1. 失敗しているテスト

### 1.1 09_closure.vmo - Vim Runtime Error

**エラーメッセージ:**
```
Vim(let):E704: Funcref variable name must start with a capital: l:inc
```

**原因:** VimScriptの言語仕様制約

VimScriptでは、関数参照(funcref)を保持する変数名は必ず大文字で始まる必要があります。これはVimの慣習で、変数と関数を区別するためのものです。

**問題のコード (codegen.py:118-121):**
```python
elif isinstance(node, Assign):
    target = self.gen_expr(node.target)
    val = self.gen_expr(node.value)
    self.emit(f"let {target} = {val}")
```

**生成されているVimScript:**
```vim
let l:inc = function("s:__lambda_0")  " エラー: l:inc は小文字開始
call l:inc()
```

**期待されるVimScript:**
```vim
let l:Inc = function("s:__lambda_0")  " OK: l:Inc は大文字開始
call l:Inc()
```

**修正方針:**

アプローチ1: Assign処理でfuncrefを検出
```python
elif isinstance(node, Assign):
    target = self.gen_expr(node.target)
    val = self.gen_expr(node.value)
    # funcrefの場合、変数名をキャピタライズ
    if 'function("' in val and target.startswith('l:'):
        target = target[:2] + target[2].upper() + target[3:]
    self.emit(f"let {target} = {val}")
```

アプローチ2: 変数名の決定を分離
- `gen_var_decl` と `gen_assign` で変数名生成を共通化
- 変数用途(funcref/通常値)に応じて命名ルールを適用

---

## 2. 未作成のテスト

### 2.1 06_import.vmo

開発計画には記載されているが、テストファイルが存在しない。

**予定されていた内容:**
```vmo
import { helper } from "./utils"
echo helper()
```

**問題:** モジュールパスの解決がcodegenで未実装

---

## 3. テスト一覧 (現在)

| ファイル | 状態 | メモ |
|---------|------|------|
| 01_variables.vmo | ✅ PASS | |
| 02_functions.vmo | ✅ PASS | |
| 03_control_flow.vmo | ✅ PASS | |
| 04_advanced.vmo | ✅ PASS | |
| 05_async.vmo | ✅ PASS | |
| 06_import.vmo | ❌ 未作成 | codegen要修正 |
| 07_pipeline.vmo | ✅ PASS | |
| 08_builtins.vmo | ✅ PASS | |
| 09_closure.vmo | ❌ FAIL | E704 エラー |
| 10_class.vmo | ✅ PASS | |
| test_definition.vmo | ✅ PASS | LSPテスト |

---

## 4. 技術メモ

### VimScript funcref制約

- 変数名が `g:` で始まる: 大文字小文字OK
- 変数名が `l:` で始まる: **大文字必須**
- 変数名が `s:` で始まる: **大文字必須**
- 変数名が接頭辞なし: **大文字必須**

参考: `:help E704`

### Lambda → VimScript変換

現在のパターン:
1. ラムダが変数に代入される → 名前付き関数として生成
2. `function("s:__lambda_N")` でfuncref作成
3. 変数名は元の識別子そのまま → 小文字なのでエラー

### 対応が必要な箇所

1. `codegen.py:118-121` - Assign文の変数名処理
2. 他のfuncref代入箇所も確認が必要

---

## 5. 次アクション

- [ ] 09_closure.vmo の修正実装
- [ ] 修正後、全テスト実行してパス確認
- [ ] 06_import.vmo の実装（必要に応じて）
