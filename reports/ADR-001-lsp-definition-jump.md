# ADR 001: LSP 定義ジャンプ機能の実装

**ステータス**: 承認済み  
**日付**: 2026-03-06  
**作成者**: opencode (Claude Pro)

## 決定事項

### 1. ASTに位置情報を追加
- 基底クラス `Node` に `line: Optional[int]`, `col: Optional[int]` を追加
- `@dataclass` をはずし、単純な基底クラスとして実装

### 2. パーサーの修正
- `VarDecl`, `FnDecl`, `ClassDecl`, `Call` パース時にTokenの位置情報を設定
- `Ident` ノード作成時にTokenの位置情報を設定

### 3. シンボルテーブルの構築
- 新規ファイル `packages/vimmo-ls/src/vimmo_ls/symbols.py` に実装
- `SymbolTable` クラス：識別子→定義位置のマッピング
- `build_symbol_table()` 関数：AST walkして定義を収集

### 4. LSPハンドラの実装
- `textDocument/definition` を追加
- カーソル位置の識別子を抽出し、シMBOLテーブルでルックアップ

## 変更されたファイル

| ファイル | 変更 |
|---------|------|
| `packages/vimmo-core/src/vimmo/ast_nodes.py` | 基底クラスにline/col追加 |
| `packages/vimmo-core/src/vimmo/parser.py` | 位置情の設定を追加 |
| `packages/vimmo-ls/src/vimmo_ls/symbols.py` | 新規作成 |
| `packages/vimmo-ls/src/vimmo_ls/server.py` | definition ハンドラ追加 |

## テスト結果
✅ 全テストパス (01_variables, 02_functions, 03_control_flow, 04_advanced, test_definition)
