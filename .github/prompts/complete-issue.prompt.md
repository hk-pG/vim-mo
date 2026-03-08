---
agent: "agent"
description: "GitHub Issue 完了時の標準手順。テスト確認・ドキュメント更新・記録・PR 作成を実施する。"
---

# Issue 完了プロンプト

Issue 番号: $ISSUE_NUMBER（未指定の場合は会話から特定する）

## Step 1: テスト確認（Green の確認）

```bash
# E2E テスト全件実行
docker compose run --rm test

# LSP テスト（LSP 機能を変更した場合）
cd packages/vimmo-ls && pip install -e ".[test]" -q && pytest tests/ -v
```

- 全テストが PASS することを確認する
- 新規追加したテストケースも含めて PASS であることを確認する
- FAIL がある場合は実装に戻る（完了プロンプトを中断）

## Step 2: DESIGN.md の更新チェック

**設計意図が変わった場合のみ** DESIGN.md を更新する。以下の基準で判断:

| 変更の種類                   | DESIGN.md 更新               |
| ---------------------------- | ---------------------------- |
| 新しい構文・演算子の追加     | ✅ 必要                      |
| 新しい組み込みメソッドの追加 | ✅ 必要                      |
| バグ修正（動作は仕様通り）   | ❌ 不要                      |
| パフォーマンス改善           | ❌ 不要                      |
| LSP 機能の追加               | △ LSP セクションがあれば更新 |

更新する場合:

- `DESIGN.md` の該当セクションに VimMo 構文例・VimScript 変換例を追記する
- 未実装の機能には `> **未実装/将来予定:**` の注記を付ける
- 制限事項には `> **制限:**` の注記を付ける

## Step 3: ADR の作成（設計変更があった場合）

以下のいずれかに該当する場合は ADR を作成する:

- 新しい言語機能・構文の設計決定をした
- 複数の実装方針を検討してトレードオフを判断した
- VimScript の制約への対応方針を決定した

```bash
# 次の ADR 番号を確認
ls reports/ADR-*.md | tail -1

# ADR ファイルを作成（例: ADR-007）
touch reports/ADR-007-feature-name.md
```

ADR の内容:

```markdown
# ADR-NNN: タイトル

**ステータス:** 承認済み
**日付:** YYYY-MM-DD

## 背景

なぜこの決定が必要だったか

## 決定事項

何を決定したか

## 変更されたファイル

- `path/to/file.py`

## テスト結果

✅ 全 N テスト PASS
```

## Step 4: reports/ サマリーの記録

```bash
# 本日の日付でファイル作成
touch reports/YYYYMMDD-issue-$ISSUE_NUMBER-topic.md
```

サマリーの内容:

```markdown
**モデル:** claude-sonnet-4.6

## 完了した Issue

- #$ISSUE_NUMBER タイトル

## 変更したファイル

- `path/to/changed/file.py` — 変更内容の一行説明

## テスト結果

✅ 全 N テスト PASS（E2E + LSP ユニットテスト）

## 次のステップ

- 関連する Issue や残課題があれば記載
```

## Step 5: コミットと PR 作成

```bash
# 変更を全てステージ
git add -A

# コミット（Conventional Commits 形式）
git commit -m "feat(scope): Issue #$ISSUE_NUMBER の内容を一行で説明"

# PR 作成
gh pr create \
  --repo hk-pG/vim-mo \
  --title "feat: Issue #$ISSUE_NUMBER タイトル" \
  --body "## 概要
$(gh issue view $ISSUE_NUMBER --json title,body -q '.body')

## 変更内容
- 変更点を箇条書きで

## テスト
- [x] E2E テスト全件 PASS
- [x] LSP テスト PASS（該当する場合）

Closes #$ISSUE_NUMBER" \
  --assignee @me
```

## Step 6: Issue の完了チェックボックスを更新

```bash
gh issue view $ISSUE_NUMBER --repo hk-pG/vim-mo
```

Issue 本文のチェックボックスが全て完了していることを確認する。
Epic Issue（親 Issue）があれば、対応するチェックボックスも更新する。

## 完了チェックリスト

- [ ] 全テスト PASS を確認した
- [ ] DESIGN.md を更新した（不要な場合はスキップ）
- [ ] ADR を作成した（設計変更がない場合はスキップ）
- [ ] reports/ にサマリーを記録した
- [ ] コミットと PR を作成した
- [ ] Issue のチェックボックスを確認した
