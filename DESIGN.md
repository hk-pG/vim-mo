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

### 非同期処理（job_start wrapper）
```
async fn fetchFile(path: string): void {
  let result = await job("cat " + path)
  echo result.stdout
}
```

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

## VimScriptへのマッピング

| VimMo | VimScript |
|-------|-----------|
| `let x = 1` | `let l:x = 1` |
| `const x = 1` | `let l:x = 1` (再代入チェックはコンパイル時) |
| `fn f() {}` | `function! s:f() ... endfunction` |
| `async fn` | `function! + job_start()` |
| `(x) => x*2` | `{x -> x*2}` (Vim lambda) |
| `for x in list` | `for x in list ... endfor` |
| `echo val` | `echo val` |
| `class Foo {}` | dict + functions |
