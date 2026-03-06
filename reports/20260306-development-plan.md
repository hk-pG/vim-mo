# VimMo 開発計画書

**作成日:** 2026-03-06  
**期間:** 2026-03-06 〜 (完了まで)

---

## 1. 現状

### 1.1 完了済み

| 機能 | 状態 | ファイル |
|------|------|----------|
| Lexer | 完了 | `lexer.py` |
| Parser | 完了 | `parser.py` |
| Codegen | 完了 | `codegen.py` |
| LSP (Definition) | 完了 | `server.py`, `symbols.py` |
| Docker環境 | 完了 | `Dockerfile`, `docker-compose.yml` |
| AST 位置情報 | 完了 | `ast_nodes.py` |
| コア機能テスト | 完了 | 09_*.vmo (5テスト追加) |

### 1.2 テスト状況

**現在:** 10テスト (.vmo ファイル)

```
tests/cases/
├── 01_variables.vmo
├── 02_functions.vmo
├── 03_control_flow.vmo
├── 04_advanced.vmo
├── 05_async.vmo
├── 07_pipeline.vmo
├── 08_builtins.vmo
├── 09_closure.vmo      # 失敗 (VimScript制約)
├── 10_class.vmo
└── test_definition.vmo
```

**未カバー:** import (パス問題)

---

## 2. 目標

### 2.1 短期目標 (今回)

- [ ] コア機能テストの追加 (6ファイル)
- [ ] Tree-sitter パーサー基盤作成
- [ ] シンタクスハイライト実装

### 2.2 中期目標

- [ ] LSP 補完機能
- [ ] LSP Hover機能
- [ ] 診断機能の改善

### 2.3 長期目標

- [ ] 型システム基盤
- [ ] フォーマット機能

---

## 3. タスク一覧

### Phase 1: テスト追加 (本次)

| # | タスク | テストファイル | 状態 |
|---|--------|---------------|------|
| 1.1 | async/await テスト追加 | `05_async.vmo` | ✅ |
| 1.2 | import テスト追加 | `06_import.vmo` | ❌ (パス問題) |
| 1.3 | パイプライン演算子テスト追加 | `07_pipeline.vmo` | ✅ |
| 1.4 | 組み込みメソッドテスト追加 | `08_builtins.vmo` | ✅ |
| 1.5 | クロージャテスト追加 | `09_closure.vmo` | ❌ (Vim制約) |
| 1.6 | クラステスト追加 | `10_class.vmo` | ✅ |
| 1.7 | 全テスト実行・確認 | - | ✅ |

### Phase 1.5: Docker テスト環境 (本次追加)

| # | タスク | 状態 |
|---|--------|------|
| 1.8 | docker-compose.yml に test サービス追加 | ✅ |
| 1.9 | Docker環境で全テスト実行 | ✅ |

**結果:** 9/10 テストパス (06_import は codegen 修正必要、09_closure は VimScript 制約)

### Phase 2: Tree-sitter 基盤構築

| # | タスク | 状態 |
|---|--------|------|
| 2.1 | tree-sitter-cli 導入 | ⬜ |
| 2.2 | grammar.js 作成 | ⬜ |
| 2.3 | パーサー生成 | ⬜ |
| 2.4 | highlights.scm 作成 | ⬜ |
| 2.5 | Neovim 設定 | ⬜ |

### Phase 3: シンタクスハイライト実装

| # | タスク | 状態 |
|---|--------|------|
| 3.1 | ハイライトQuery作成 | ⬜ |
| 3.2 | カラーテーマ対応 | ⬜ |
| 3.3 | 動作確認 | ⬜ |

---

## 4. 詳細設計

### 4.1 テスト追加 (Phase 1)

#### 1.1 `05_async.vmo` - 非同期処理

```vmo
async fn fetchData(): void {
  let result = await job("echo 'hello'")
  echo result
}

fn main(): void {
  fetchData()
}
```

#### 1.2 `06_import.vmo` - モジュールインポート

```vmo
import { helper } from "./utils"
echo helper()
```

※ `utils.vim` も作成 (対応する expected 出力)

#### 1.3 `07_pipeline.vmo` - パイプライン演算子

```vmo
let nums = [1, 2, 3, 4, 5]
let result = nums 
  |> filter((x) => x > 2) 
  |> map((x) => x * 10)
echo result
```

#### 1.4 `08_builtins.vmo` - 組み込みメソッド

```vmo
let arr = [1, 2, 3]
arr.push(4)
echo arr.len()
echo arr.pop()

let filtered = arr.filter((x) => x > 2)
echo filtered

let mapped = arr.map((x) => x * 2)
echo mapped

let d = {a: 1, b: 2}
echo d.keys()
echo d.values()
echo d.has("a")
```

#### 1.5 `09_closure.vmo` - クロージャ

```vmo
fn makeCounter(): void {
  let count = 0
  let inc = () => {
    count = count + 1
    echo count
  }
  inc()
  inc()
}
makeCounter()
```

#### 1.6 `10_class.vmo` - クラス

```vmo
class Math {
  static fn add(a: number, b: number): number {
    return a + b
  }
}
echo Math.add(1, 2)

class Counter {
  let count = 0
  fn increment(): void {
    self.count = self.count + 1
  }
  fn get(): number {
    return self.count
  }
}
let c = new Counter()
c.increment()
echo c.get()
```

### 4.2 Tree-sitter 導入 (Phase 2)

#### ディレクトリ構成

```
packages/
├── tree-sitter-vimmo/       # 新規
│   ├── grammar.js           # 言語定義
│   ├── src/
│   │   ├── parser.c         # 生成
│   │   └── scanner.c        # 任意
│   ├── queries/
│   │   ├── highlights.scm  # ハイライト
│   │   └── folds.scm       # 折り返し
│   └── package.json
└── ...
```

#### grammar.js 要件

Tree-sitter の JavaScript DSL で VimMo の文法定义:

- 識別子、キーワード
- リテラル (数値、文字列、真偽値、null、配列、辞書)
- 式 (二項演算子、ラムダ、パイプライン)
- 文 (変数宣言、関数定義、制御構文、クラス)
- コメント

#### ハイライトQuery例

```scm
; keywords
[
  "fn"
  "let"
  "const"
  "if"
  "else"
  "for"
  "while"
  "return"
  "class"
  "new"
  "self"
  "async"
  "await"
  "import"
] @keyword

; functions
(fn_decl name: (ident) @function)

; types
(type: (type_identifier) @type)

; strings
(string) @string

; numbers
(number) @number
```

---

## 5. 進捗管理

### マイルストーン

| マイルストーン | 内容 | 完了条件 |
|--------------|------|----------|
| M1 | テスト追加完了 | 6テスト追加・全テストパス |
| M2 | Tree-sitter基盤完了 | grammar.js作成・パーサー生成 |
| M3 | シンタクスハイライト完了 | Neovimでhighlighting動作 |

### 作業ログ

作業開始時に記録:

```
## YYYY-MM-DD

### 作業内容
- タスク: xxx

### 成果
- 作成: xxx
- 変更: xxx

### 次回作業
- タスク: xxx
```

---

## 6. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| テスト追加で既存機能壊す | 高 | 追加前後で全テスト実行 |
| Tree-sitter grammar 複雑化 | 中 | 簡易なサブセットから開始 |
| クロージャのVim表現 | 中 | 現時点では skip または限定対応 |

---

## 7. 参照資料

- Tree-sitter 公式: https://tree-sitter.github.io/tree-sitter/
- nvim-treesitter: https://github.com/nvim-treesitter/nvim-treesitter
- 既存パーサー: `packages/vimmo-core/src/vimmo/parser.py`
