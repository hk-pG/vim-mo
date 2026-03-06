# GitHub Copilot Instructions

まず **`AGENTS.md`** を参照してください。プロジェクトの開発標準（テスト実行・コード規約・VimScript制約・コミット規約等）がまとめられています。

---

## Build & Test

```bash
# テスト実行（Docker 推奨）
docker compose run --rm test

# 単一ファイルのコンパイル確認
docker compose run --rm vimmo python packages/vimmo-core/src/vimmo/vimmo.py compile <file.vmo> -o /tmp/out.vim

# デバッグ用ダンプ
PYTHONPATH=packages/vimmo-core/src python packages/vimmo-core/src/vimmo/vimmo.py tokens <file.vmo>
PYTHONPATH=packages/vimmo-core/src python packages/vimmo-core/src/vimmo/vimmo.py ast <file.vmo>
```

テストランナー (`tests/run_tests.py`) は `.vmo` をコンパイルして Vim/Neovim で実行し、exit code だけをチェックする。`.vim` ファイルは毎回上書き再生成される（期待値との diff 比較はしない）。

## Architecture

```
.vmo source
  └─ Lexer (lexer.py)        → List[Token]
       └─ Parser (parser.py) → AST (ast_nodes.py の @dataclass)
            └─ Codegen (codegen.py) → VimScript 文字列
```

- `vimmo.py` が CLI エントリポイントとしてパイプラインを統括
- `vimmo-ls/` は pygls ベースの LSP サーバー（リアルタイム診断・定義ジャンプ）
- `vscode-vimmo/` は VS Code 拡張（文法ハイライト + LSP クライアント）

## Codegen の主要パターン

**スコープ管理**

`function_depth == 0` → スクリプトスコープ (`s:`)、`> 0` → ローカルスコープ (`l:`)。
`scope_stack` の各エントリは `{'kind': 'fn'|'lambda', 'params': set, 'funcref_vars': set}`。

**Lambda の生成戦略**

- Block body (`() => { ... }`) → 囲む関数の内部に `function! s:__lambda_N() closure` として inline 定義（ネスト時のみ `closure`）。外側の `l:` 変数をキャプチャできる。
- Expression body (`(x) => x * 2`) → Vim ネイティブラムダ `{x -> x * 2}` に変換。

**Funcref 変数の命名規則 (E704 対応)**

`l:`/`s:` スコープで funcref を保持する変数は大文字始まりが必要（VimScript 仕様）。
`_register_funcref_var()` で登録 → `_cap_funcref_name()` で `inc` → `Inc` に自動変換。

**非同期 (`await job(...)`)**

コールバック用のヘルパー関数 (`__job_N_out`, `__job_N_exit`) を自動生成し、スピンウェイトループで結果を待つ。

## VimScript の既知の制約

| エラー | 原因 | 対処 |
|--------|------|------|
| E704 | `l:inc = function(...)` — 小文字始まりの funcref 変数 | `_cap_funcref_name()` で自動キャピタライズ |
| E121 | トップレベルにホイストされたラムダが外側の `l:` 変数を参照 | inline 定義 + `closure` キーワード |
| E932 | トップレベル関数に `closure` を付けた | `function_depth == 0` のとき `closure` を省略 |

## テストケースの追加

1. `packages/vimmo-core/tests/cases/NN_name.vmo` を作成
2. `docker compose run --rm test` で全テスト実行
3. Vim runtime error がなければ PASS

## ADR・作業サマリー (`reports/`)

`reports/` ディレクトリには以下の2種類のファイルを記録する:

| ファイル名パターン | 内容 | タイミング |
|-----------------|------|---------|
| `ADR-NNN-{name}.md` | 重要な設計決定の記録（背景・決定事項・変更ファイル・テスト結果）。NNN は3桁ゼロ埋め、既存ファイルを確認して次番号を使う | 設計変更を行ったとき |
| `YYYYMMDD-{topic}.md` | 作業サマリー（完了タスク・変更ファイル一覧・テスト結果・次のステップ）。モデル名はファイル内の先頭に記載 | 作業完了時 |

詳細フォーマットは `AGENTS.md` の「ADR」「作業完了時の記録」セクションを参照。
