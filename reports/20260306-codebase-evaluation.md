# VimMo コードベース評価レポート

**日付:** 2026-03-06  
**評価者:** opencode (big-pickle)

---

## 1. テスト網羅率

### 現在のテストケース (6件)

| ファイル | テスト内容 | 網羅度 |
|---------|-----------|--------|
| `01_variables.vmo` | let/const, list, dict, 型注釈 | △ 基本のみ |
| `02_functions.vmo` | 関数定義・呼び出し | △ 単純のみ |
| `03_control_flow.vmo` | if/else, while, for | △ 単純のみ |
| `04_advanced.vmo` | ラムダ, クラス | △ 単純のみ |
| `test_definition.vmo` | LSP定義ジャンプ用 | △ 単純のみ |

### 未テストの主要機能

| 機能 | 重要度 | 备注 |
|------|--------|------|
| async/await | 高 | 非同期処理のテストがない |
| import/モジュール | 中 | インポート文のテストがない |
| パイプライン演算子 | 中 | \|> のテストがない |
| 組み込みメソッド | 中 | map, filter, push, len 等未テスト |
| エラーケース | 高 | パースエラー時の動作未テスト |
| クロージャ | 中 | ラムダ内のクロージャ未テスト |
| 多段if/elseif | 低 | elseif 連鎖のテストがない |

### 評価

- **網羅率:** 約30% (主要機能ベース)
- **問題:** シンタクスハイライト実装前にテストを追加しておくべき

---

## 2. コード設計評価

### 良好 ✓

1. **三者分離:** Lexer → Parser → Codegen の明確な分離
2. **例外設計:** `LexerError`, `ParseError`, `CodegenError` の個別例外
3. **位置情報:** ASTノードに line/col を追加 (LSP対応済み)
4. **型ヒント:** 一部で使用 (Python 3.14+)

### 課題 △

#### 2.1 パーサー (523行)

```
packages/vimmo-core/src/vimmo/parser.py:523
```

- **問題:** 1ファイルに全パーサーロジック (500+行)
- **影響:** 保守性低下、新機能追加時のリスク
- **建議:** 式パーサー部分を `_expr.py` 等に分離

#### 2.2 スコープ管理の重複

- **codegen.py:** `scope_stack` で変数解決
- **symbols.py:** `SymbolTable` で別管理
- **問題:** 二重管理、LSPとcodegenでロジックが異なる可能性
- **建議:** 中央集権的なスコープ管理の導入

#### 2.3 型システムの未実装

- 型注釈をパースはするが、**検証・使用していない**
- 例: `let x: number = "string"` → 警告なし
- **建議:** 型チェック機能の追加 (将来の拡張のため基盤整備)

#### 2.4 定数 再代入チェック

```python
# codegen.py:133-134
if node.name in self._consts:
    raise CodegenError(f"Cannot reassign const '{node.name}'")
```

- 実装されているが、ランタイムエラーは発生しない (VimScript の `const` は read-only ではない)

---

## 3. アーキテクチャ評価

### 現在のアーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│ vimmo-ls (LSP)                                     │
│   ├─ import vimmo.lexer                            │
│   ├─ import vimmo.parser                           │
│   └─ import vimmo_ls.symbols                        │
├─────────────────────────────────────────────────────┤
│ vimmo-core                                         │
│   ├─ lexer.py → tokens                              │
│   ├─ parser.py → AST                               │
│   ├─ codegen.py → VimScript                        │
│   └─ ast_nodes.py                                   │
└─────────────────────────────────────────────────────┘
```

### 課題

#### 3.1 密結合

```python
# server.py:12-14
from vimmo.lexer import Lexer, LexerError
from vimmo.parser import Parser, ParseError
from vimmo_ls.symbols import build_symbol_table
```

- LSP が vimmo-core を直接 import
- **問題:** LSP テストが core テストと分離できない
- **建議:** LSP 用 API 層の整備 (compile, parse を提供)

#### 3.2 パフォーマンス (LSP)

```python
# server.py:46-51
tokens = Lexer(doc.source).tokenize()
program = Parser(tokens).parse()
table = build_symbol_table(params.text_document.uri, program)
```

- **編集ごとに完全パース:** 2000行超のファイルで低速
- **建議:** 
  - 增量パースの検討
  - パーサー自体のパフォーマンス最適化

#### 3.3 テスト戦略

- E2E のみ (Vim 実行必須)
- **問題:** CI/CD で Vim 環境が必要
- **建議:** ユニットテストの追加 (Parser 単品等)

---

## 4. シンタクスハイライト・補完に向けて

### 現状の課題

#### 4.1 トークン種の限界

```python
# lexer.py:11-86
class TokenType(Enum):
    # ... 60+ token types
```

- **問題:** Vim 用シンタクスファイル (.vim) を生成できない
- **解決:** Tree-sitter との連携、または Vim 向け syntax ファイル生成機能を追加

#### 4.2 補間 (Completion) の基盤

- **現在:** Definition のみ実装
- **未実装:** Hover, Completion, References
- **基盤:** シンボルテーブルが存在するが情報が限定的

### 必要な基盤強化

| 機能 | 必要な基盤 | 状態 |
|------|-----------|------|
| シンタクスハイライト | Token ストリーム or Tree-sitter | 要実装 |
| 補完 | シンボルテーブル + 型情報 | 要強化 |
| Hover | シンボルテーブル + 型情報 | 要強化 |
| フォーマット | AST 操作 | 要実装 |

---

## 5. リファクタリング提案

### 優先度高 (次に着手前に推奨)

| # | 項目 | 理由 | 影響範囲 |
|---|------|------|----------|
| 1 | パーサー分割 | 保守性、500行超 | parser.py |
| 2 | テスト追加 | 機能追加前的確odetection | tests/ |
| 3 | LSP API 層 | 密結合解消 | vimmo-core |

### 優先度中 (機能追加後に検討)

| # | 項目 | 理由 | 影響範囲 |
|---|------|------|----------|
| 4 | スコープ管理統合 | 重複解決 | codegen.py, symbols.py |
| 5 | 型システム基盤 | 将来のため | parser.py, ast_nodes.py |
| 6 | 增量パース | パフォーマンス | parser.py |

---

## 6. まとめ

### 現在の強み

- 明確な三者分離 (Lexer/Parser/Codegen)
- 小規模で理解しやすいコードベース
- LSP 基盤已完成 (Definition ジャンプ)
- Docker 開発環境整備済み

### 主な課題

1. **テスト不足:** 主要機能未カバー
2. **密結合:** LSP ↔ Core の依存
3. **保守性:** 500+ 行パーサー
4. **基盤:** 型システム未実装

### 推奨アクション

1. **次に進む前に:** テスト追加 (async, import, パイプライン, 組み込みメソッド)
2. **シンタクスハイライト用:** Tree-sitter 導入または Vim syntax ファイル生成を実装
3. **補完機能用:** シンボルテーブルに型情報を追加

---

## 確認事項

以下の点について追加情報が必要であればお知らせください:

1. **目標環境:** シンタクスハイライトは Vim のみか？ (VS Code も含むか)
2. **Tree-sitter:** 導入を検討しているか？ (または Vim 標準 syntax ファイルで十分か)
3. **型システム:** どの程度の型チェックを導入予定か？ (完全か、部分的なら昭島)
