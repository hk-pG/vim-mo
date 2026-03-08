# VimMo Language Design

## 概要
VimMo（Vim Modern）は、TypeScript風の文法でVimプラグインを開発できる言語。
トランスパイラがVimScript（.vim）を出力する。

## 文法仕様

### 変数宣言
```
let x = 10
const name = "hello"
let items: list = [1, 2, 3]
let map: dict = {key: "value"}
```

### 型注釈
- number, string, bool, list, dict, any, void

> **注意（現在の実装）：** 型注釈は構文としてパース・保存されますが、**コンパイル時・実行時のいずれの型チェックも行われません**。型注釈は現時点では文書化目的のアノテーションとして機能します。将来的な型チェック機能の実装を予定しています。

### コメント

```vimmo
// これは行コメントです
let x = 10  // 行末コメントも使用可
```

`//` 以降の内容は行末まで無視されます。ブロックコメント（`/* */`）は**サポートされていません**。

### 関数
```
fn greet(name: string): string {
  return "Hello, " + name
}
```

### ラムダ/クロージャ
```
let double = (x) => x * 2
let add = (a, b) => {
  return a + b
}
let nums = [1, 2, 3]
let doubled = nums.map((x) => x * 2)
```

ラムダのボディ種別によって生成コードが異なります：

| VimMo | VimScript | 説明 |
|-------|-----------|------|
| `(x) => x * 2` | `{x -> x * 2}` | **式ボディ** — Vim ネイティブラムダ |
| `(x) => { return x * 2 }` | `function! s:__lambda_N(x) [closure]` | **ブロックボディ** — 名前付き関数を生成 |

ブロックボディのラムダが関数内で定義された場合、`closure` キーワードが付与され、外側の `l:` 変数をキャプチャできます（Vim 8+ / Neovim 必須）。

### 非同期処理（job_start wrapper）
```
async fn fetchFile(path: string): void {
  let result = await job("cat " + path)
  echo result.stdout
}
```

> `await job(cmd)` の戻り値は `{ stdout: list<string>, stderr: list<string>, exit: number }` の辞書。
> 各出力行はリストの要素として格納される。文字列として使う場合は `result.stdout.join("\n")` を使用すること。

### 制御構文
```
if cond {
  ...
} else if cond2 {
  ...
} else {
  ...
}

for item in items {
  ...
}

while cond {
  ...
}
```

#### ループ制御

```vimmo
for item in items {
  if item == 0 {
    continue
  }
  if item > 10 {
    break
  }
  echo item
}
```

`break` と `continue` は VimScript の同名命令に変換されます。

### パイプライン演算子
```
let result = items |> filter((x) => x > 0) |> map((x) => x * 2)
```

### クラス（辞書ベース）
```
class Counter {
  let count: number = 0

  fn increment(): void {
    self.count += 1
  }

  fn get(): number {
    return self.count
  }
}
```

#### インスタンス化

`new ClassName(args...)` は VimScript で `s:ClassName_new(args...)` 関数呼び出しに変換されます。

> **未実装：** `static` メソッドは現在サポートされていません。クラスに属さないスクリプトレベルの関数（`fn`）を代替として使用してください。

### Vim固有ヘルパー
```
autocmd("BufWritePre", "*.py", () => {
  echo "saving..."
})

command("MyCmd", (args) => {
  echo args
})

map("n", "<leader>f", () => {
  // ...
})
```

### インポート
```
import { myFunc } from "./utils"
```

> **制限：** 現在の実装は `source` 命令を使用するため、インポートパスは実行時の VimScript ファイルからの相対パスになります。型チェックやシンボル解決はコンパイル時には行われません。

## VimScriptへのマッピング

| VimMo | VimScript |
|-------|-----------|
| `let x = 1`（スクリプトレベル） | `let s:x = 1` |
| `let x = 1`（関数内）           | `let l:x = 1` |
| `const x = 1` | `let s:x = 1`（スクリプト）/ `let l:x = 1`（関数内） | 再代入チェックはコンパイル時のみ。VimScript の `lockvar` は使用しないため、実行時の書き換えは防止されない |
| `fn f() {}` | `function! s:f() ... endfunction` |
| `async fn` | `function! + job_start()` |
| `(x) => x*2` | `{x -> x*2}` (Vim lambda) |
| `for x in list` | `for x in list ... endfor` |
| `echo val` | `echo val` |
| `class Foo {}` | dict + functions |

## 組み込みメソッド

### リスト（list）

| VimMo | VimScript | 説明 |
|-------|-----------|------|
| `arr.push(val)` | `add(arr, val)` | 末尾に要素を追加 |
| `arr.pop()` | `remove(arr, -1)` | 末尾の要素を取り出す |
| `arr.len()` | `len(arr)` | 要素数を返す |
| `arr.filter((x) => cond)` | `filter(copy(arr), cb)` | 条件に一致する要素を返す |
| `arr.map((x) => expr)` | `map(copy(arr), cb)` | 各要素を変換して返す |
| `arr.join(sep)` | `join(arr, sep)` | 文字列に変換して結合 |

### 文字列（string）

| VimMo | VimScript | 説明 |
|-------|-----------|------|
| `str.split(sep)` | `split(str, sep)` | 文字列を分割してリストを返す |
| `str.len()` | `len(str)` | 文字数を返す |

### 辞書（dict）

| VimMo | VimScript | 説明 |
|-------|-----------|------|
| `d.keys()` | `keys(d)` | キーの一覧リストを返す |
| `d.values()` | `values(d)` | 値の一覧リストを返す |
| `d.has(key)` | `has_key(d, key)` | キーの存在確認 |

> **注意：** `filter()` と `map()` のコールバックには Vim ネイティブラムダ（`{x -> expr}`）が渡されます。ブロックボディのラムダを渡す場合は名前付き関数（`s:__lambda_N`）が生成されます。
