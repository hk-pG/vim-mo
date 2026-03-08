**モデル:** claude-sonnet-4.6

# 作業サマリー: watch スクリプト実装 (Issue #3)

## 完了したタスク

- `vimmo watch <dir>` コマンドを実装 (Python watchdog 使用)
- `main.py` のスタブを修正し entry point 経由でも動作するよう修正
- ベアインポートをパッケージインポート化（entry point + PYTHONPATH 両対応）

## 新規作成 / 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `packages/vimmo-core/src/vimmo/vimmo.py` | `_compile_file_safe`, `_compile_and_report`, `cmd_watch` を追加; ベアインポートを try/except パッケージインポートに変更 |
| `packages/vimmo-core/src/vimmo/main.py` | スタブを削除し `vimmo.vimmo.main()` に委任 |
| `packages/vimmo-core/src/vimmo/parser.py` | ベアインポートを try/except パッケージインポートに変更 |
| `packages/vimmo-core/src/vimmo/codegen.py` | ベアインポートを try/except パッケージインポートに変更 |
| `packages/vimmo-core/pyproject.toml` | `watchdog>=3.0` を依存に追加 |

## テスト結果

```
✅ All tests passed. (11/11) — docker compose run --rm test
```

## PR

https://github.com/hk-pG/vim-mo/pull/13

## 次のステップ

- PR レビュー・マージ
- Issue #3 クローズ
- Milestone v0.2 の残タスク（LSP Hover/Signature Help）へ
