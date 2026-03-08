---
agent: "agent"
description: "GitHub Issue 着手時の標準手順。調査・設計・TDD Red フェーズまでを実施する。"
---

# Issue 着手プロンプト

Issue 番号: $ISSUE_NUMBER（未指定の場合は会話から特定する）

## Step 1: Issue の内容確認

`gh issue view $ISSUE_NUMBER --repo hk-pG/vim-mo` で Issue の内容を確認する。

- タイトル・本文・Milestone・Labels を把握する
- 完了条件（チェックボックス）を確認する

## Step 2: 現状調査（Explore エージェント推奨）

以下を調査する:

- 変更が必要なファイルを特定する（Lexer/Parser/Codegen/LSP/tests のどれか）
- 関連する既存のテストケースを確認する（`packages/vimmo-core/tests/cases/`）
- 類似の実装パターンを探す（既存コードから学ぶ）
- `reports/` の直近のサマリーを確認し、関連する既知の問題がないかチェックする

## Step 3: 設計判断（Architect が必要か判断する）

以下のいずれかに該当する場合は **Architect エージェントに委任**する:

- 新しい構文・言語機能の追加（AST/Lexer/Parser/Codegen の変更を伴う）
- 既存インターフェースへの破壊的変更の可能性
- 複数モジュールにまたがる変更
- VimScript の制約（E704/E121/E932）が絡む複雑な設計

該当しない場合（バグ修正・ドキュメント更新等）は Step 4 に進む。

### Architect への依頼内容

- 実装方針・影響ファイルの特定
- TDD のテスト仕様（何をテストするか）
- VimScript 生成の変換パターン
- ADR 草案

## Step 4: テスト作成（TDD Red フェーズ）

**テストを先に作成する。**

### E2E テスト（.vmo ファイル）

`packages/vimmo-core/tests/cases/NN_feature.vmo` を作成する:

- `NN` は既存のテスト番号の次の番号（`ls tests/cases/*.vmo` で確認）
- 実装予定の機能を使うコードを書く
- この時点ではコンパイル・実行が失敗することを確認する（Red）

```bash
# Red の確認
PYTHONPATH=packages/vimmo-core/src python packages/vimmo-core/src/vimmo/vimmo.py compile \
  packages/vimmo-core/tests/cases/NN_feature.vmo -o /tmp/test.vim
```

### LSP テスト（必要な場合）

`packages/vimmo-ls/tests/` に pytest テストを追加する（LSP 機能の変更が含まれる場合）。

## Step 5: ブランチ作成とコミット

```bash
git checkout -b feat/issue-$ISSUE_NUMBER-short-description
git add packages/vimmo-core/tests/cases/NN_feature.vmo
git commit -m "test(core): Issue #$ISSUE_NUMBER のテストケース追加 (Red)"
```

## 次のアクション

この時点での状態:

- [ ] Issue の内容と完了条件を把握した
- [ ] 変更が必要なファイルを特定した
- [ ] 必要に応じて Architect に設計を依頼した
- [ ] テストケースを作成し、Red であることを確認した
- [ ] 作業ブランチを作成した

実装（Green フェーズ）に進む準備が整いました。
`complete-issue` プロンプトは実装完了後に使用してください。
