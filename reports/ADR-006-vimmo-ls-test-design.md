# ADR-006: vimmo-ls テスト設計

**ステータス**: 草案  
**日付**: 2026-03-08  
**対象モジュール**: `packages/vimmo-ls`

---

## 背景

`vimmo-ls` には現在テストが存在しない。`symbols.py` の `SymbolTable`・`build_symbol_table` および `server.py` の純粋関数 (`_get_member_items`, `_get_ident_at_position`) はロジックが独立しており、後追いテストの追加が可能な状態にある。

## 決定事項

1. `packages/vimmo-ls/tests/` に pytest テストスイートを新設する。
2. **AST ノード直接構築**を主な入力戦略とし、数件の統合テスト（ソースパース経由）を補完的に追加する。
3. PYTHONPATH 設定は `conftest.py` で明示的に行う（pyproject.toml の相対パス設定は脆弱なため）。

## 却下した選択肢

- `pyproject.toml` の `pythonpath` のみで解決: `../../vimmo-core/src/vimmo` という相対パスは pytest の実行ディレクトリに依存し、CI 環境で壊れやすい。
- ソースパース一本化: lexer/parser に変更があった場合に symbol table のテストが無関係な理由で壊れる。

## 前提条件

- `packages/vimmo-ls` が `pip install -e packages/vimmo-ls` または等価な形でインストール済み
- `pygls`・`lsprotocol` が利用可能（vimmo-ls の依存として解決済み）
- Docker 環境では vimmo-core も editable install されていること

## 変更されるファイル

- `packages/vimmo-ls/pyproject.toml` — pytest 依存と testpaths 設定を追加
- `packages/vimmo-ls/tests/__init__.py` — 新規作成（空）
- `packages/vimmo-ls/tests/conftest.py` — 新規作成（PYTHONPATH セットアップ）
- `packages/vimmo-ls/tests/test_symbol_table.py` — 新規作成
- `packages/vimmo-ls/tests/test_build_symbol_table.py` — 新規作成
- `packages/vimmo-ls/tests/test_server_helpers.py` — 新規作成
