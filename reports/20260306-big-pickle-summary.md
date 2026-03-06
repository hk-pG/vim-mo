# VimMo 作業サマリー

**日付:** 2026-03-06  
**担当:** opencode (big-pickle)

## 完了したタスク

### LSP 定義ジャンプ機能の実装
- ADR 001 を作成して設計を記録
- ASTに位置情報を追加 (line, col)
- パーサーで位置情報を設定
- シンボルテーブルを実装 (symbols.py)
- LSP definition ハンドラを追加
- テスト作成・通過確認

## 新規作成/変更したファイル

| ファイル | 変更 |
|---------|------|
| `packages/vimmo-core/src/vimmo/ast_nodes.py` | Node基底クラスに位置情報追加 |
| `packages/vimmo-core/src/vimmo/parser.py` | 位置情報設定を追加 |
| `packages/vimmo-ls/src/vimmo_ls/symbols.py` | 新規作成 |
| `packages/vimmo-ls/src/vimmo_ls/server.py` | definition ハンドラ追加 |
| `packages/vimmo-core/tests/cases/test_definition.vmo` | 新規作成 |
| `reports/ADR-001-lsp-definition-jump.md` | ADR 新規作成 |
| `AGENTS.md` | ADR/作業記録ルールを追記 |

## テスト結果

✅ 全テストパス (5件)
- 01_variables.vmo
- 02_functions.vmo
- 03_control_flow.vmo
- 04_advanced.vmo
- test_definition.vmo

## 次のステップ

- ホバー機能の実装 (型情報表示)
- より詳細なシンボルテーブル (、スコープ対応)
