# AGENTS.md - Agent Guidelines for VimMo

This file provides guidelines for agentic coding agents working in this repository.

## Project Overview

VimMo is a transpiler that compiles a TypeScript-like language (.vmo files) to VimScript (.vim files). The project is a Python monorepo with the following structure:

```
vim-mo/
├── packages/
│   ├── vimmo-core/          # Main transpiler (lexer, parser, codegen)
│   ├── vimmo-ls/            # Language Server Protocol implementation
│   └── vscode-vimmo/        # VS Code extension
├── tests/                   # Test runner
└── examples/                # Example VimMo code
```

## Build/Lint/Test Commands

### Prerequisites
- Python 3.14+
- Vim installed (for running tests)

### Running All Tests (Docker — 推奨)

テストは **Docker を使って実行する**。ホスト環境の Python バージョンや `vim` コマンドへの依存を避けられる。

```bash
docker compose run --rm test
```

内部では Neovim (`nvim`) を `vim` として symlink して使用している。

### Running All Tests (ホスト環境)

Docker が使えない場合:

```bash
cd /Users/hk-p/repo/vim-mo
python tests/run_tests.py
```

### Running a Single Test
To run a specific test case, modify `tests/run_tests.py` or run manually:

```bash
# Compile a .vmo file
cd /Users/hk-p/repo/vim-mo/packages/vimmo-core
PYTHONPATH=src python src/vimmo/vimmo.py compile tests/cases/01_variables.vmo -o /tmp/test.vim

# Run with Vim
vim -es -V1 -c "try | source /tmp/test.vim | catch | echo v:exception | cquit 1 | endtry" -c "q"
```

### Available CLI Commands (vimmo-core)
```bash
cd /Users/hk-p/repo/vim-mo/packages/vimmo-core
PYTHONPATH=src python src/vimmo/vimmo.py <command> <file.vmo>

Commands:
  compile <input> -o <output>   Compile .vmo to .vim
  check <input>                Syntax check only
  tokens <input>               Dump token stream (debug)
  ast <input>                  Dump AST (debug)
```

### VS Code Extension Development
```bash
cd /Users/hk-p/repo/vim-mo/packages/vscode-vimmo
npm install
npm run compile  # If using TypeScript
```

## Code Style Guidelines

### General Philosophy
- Write clean, readable code with clear structure
- Follow existing conventions in each file
- Use type hints where beneficial

### Python Style

**Imports**
- Use absolute imports within packages: `from lexer import Lexer`
- Group imports: stdlib → third-party → local
- Do not use `from xxx import *`

**Naming Conventions**
- Classes: `PascalCase` (e.g., `class Parser`)
- Functions/methods: `snake_case` (e.g., `def parse_expr`)
- Constants: `SCREAMING_SNAKE_CASE`
- Private methods: prefix with `_` (e.g., `_is_lambda`)

**Type Hints**
- Use Python 3.14+ typing where appropriate
- Common types: `List`, `Optional`, `Tuple`, `Dict`

**Formatting**
- Use 4 spaces for indentation (no tabs)
- Max line length: 100 characters (soft limit)
- Use blank lines to separate logical sections
- Follow existing patterns in each file for comments

**Error Handling**
- Use custom exception classes for distinct error types:
  - `LexerError` in `lexer.py`
  - `ParseError` in `parser.py`
  - `CodegenError` in `codegen.py`
- Exceptions should include location info (line, column) when possible

### VimMo Language (.vmo files)

**Test Case Format**
- Each test has a `.vmo` source file and a `.vim` compiled output file
- Tests are in `packages/vimmo-core/tests/cases/`
- Naming: `NN_name.vmo` and `NN_name.vim` (e.g., `01_variables.vmo`)
- **注意**: `.vim` ファイルはテストランナーが毎回コンパイルして**上書き再生成**する。期待値との比較は行わず、Vim 実行時の exit code のみをチェックする。`.vim` ファイルはコミットしてよいが、テスト実行のたびに変わりうる。

**When Adding Tests**
1. Create `NN_feature.vmo` with VimMo source code
2. Run compilation and verify it produces valid VimScript
3. Ensure it runs successfully in Vim (no runtime errors)

### Project-Specific Patterns

**Lexer (`lexer.py`)**
- Use `Enum` for token types with `auto()`
- `@dataclass` for `Token` with `type`, `value`, `line`, `col`
- Implement `tokenize()` method returning `List[Token]`

**Parser (`parser.py`)**
- Use recursive descent parsing
- Helper methods: `peek()`, `advance()`, `check()`, `match()`, `expect()`
- Use `ParseError` for syntax errors with token location
- Follow precedence chain: expression → pipeline → assign → or → and → equality → comparison → addition → multiplication → unary → call → primary

**AST Nodes (`ast_nodes.py`)**
- Use `@dataclass` for all node types
- Inherit from base `Node` class
- Group by category with comments (Expressions, Statements, etc.)

**Code Generator (`codegen.py`)**
- `generate(node: Program) -> str` entry point
- Use `emit(line)` for outputting VimScript
- Track scope with `enter_scope()` / `leave_scope()`
- Handle scope prefixes: `s:` (script), `l:` (local), `a:` (argument)
- `function_depth` で現在のネスト深さを追跡（0 = スクリプトレベル）
- `scope_stack` の各エントリは `{'kind': 'fn'|'lambda', 'params': set, 'funcref_vars': set}` の構造
- funcref を保持する変数は `_register_funcref_var()` で登録し `_cap_funcref_name()` でキャピタライズ

### Git コミット規約

Conventional Commits 形式を使用する:

```
<type>(<scope>): <概要（日本語可）>

<本文（任意）>
```

| type | 用途 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `refactor` | 機能変更を伴わないリファクタリング |
| `test` | テストの追加・修正 |
| `chore` | ビルド設定・依存関係等の変更 |

scope は変更対象モジュール名（例: `codegen`, `parser`, `lexer`, `ls`）。

### Common Pitfalls

1. **Python version**: This project requires Python 3.14+ (check `.python-version`)
2. **PYTHONPATH**: When running vimmo CLI, set `PYTHONPATH=src`
3. **Vim runtime**: Some features require Vim 8+ / Neovim (e.g., lambdas, closures, jobs)
4. **Test dependencies**: Tests require `vim` command available in PATH (Docker 環境では nvim を symlink)
5. **VimScript funcref 変数名制約 (E704)**: `l:` / `s:` スコープの変数が funcref を保持する場合、変数名は**大文字で始まる必要**がある (`l:Inc` は OK、`l:inc` は NG)。codegen でラムダを変数に代入する際はキャピタライズが必要。
6. **VimScript closure (E121 / E932)**: multi-line ラムダをスクリプトトップレベルにホイストすると外側の `l:` 変数をキャプチャできない。囲む関数の**内部で定義**し `closure` キーワードを付与すること (Vim 8+ / Neovim 必須)。トップレベル関数に `closure` を付けると E932 エラーになる。
7. **VimScript E704/E121 の同時修正**: E704（funcref 変数の小文字名）を修正する際は、必ず E121（クロージャスコープ破裂）も確認すること。`l:inc = ...` を `l:Inc = ...` にするだけでは不十分で、block body lambda は inline 定義 + `closure` キーワードの戦略も合わせて確認する。
8. **pygls バージョン確認**: LSP 関連の修正を着手する前に必ず `pip show pygls` でバージョンを確認すること。pygls 2.x では `workspace.get_document()`・`show_message()`・`publish_diagnostics()` が廃止されており、互換ラッパー経由（`ls.protocol.notify()` 等）での実装が必要。
9. **"テスト PASS" ≠ "全て正常"**: `docker compose run --rm test` が成功しても、VimScript の暗黙的なエラー無視（未定義変数のサイレント化等）により実行時バグが潜む可能性がある。重要な変更後は実際に Neovim でプラグインを動作させて確認すること。

### File Locations

| File | Purpose |
|------|---------|
| `packages/vimmo-core/src/vimmo/lexer.py` | Tokenizer |
| `packages/vimmo-core/src/vimmo/parser.py` | Parser |
| `packages/vimmo-core/src/vimmo/ast_nodes.py` | AST definitions |
| `packages/vimmo-core/src/vimmo/codegen.py` | Code generator |
| `packages/vimmo-core/src/vimmo/vimmo.py` | CLI entry point |
| `packages/vimmo-core/tests/cases/*.vmo` | Test source files |
| `packages/vimmo-core/tests/cases/*.vim` | Expected Vim output |
| `tests/run_tests.py` | Test runner |
| `DESIGN.md` | Language design spec |

### ADR (Architecture Decision Records)

- 重要な設計決定を行った場合は `reports/ADR-NNN-{feature-name}.md` にADRを記録する（3桁ゼロ埋め）
- 番号は `reports/` 内の既存 ADR ファイルを確認して次の番号を使うこと
- ADRには以下を含める:
  - ステータス (草案/承認済み/Deprecated)
  - 決定事項
  - 変更されたファイル
  - テスト結果

### Issue 対応の TDD ワークフロー

GitHub Issue に取り組む際は以下のフローを守る。
詳細なチェックリストは `.github/prompts/start-issue.prompt.md` と `.github/prompts/complete-issue.prompt.md` を参照。

```
Issue open
  ↓
【調査】 Explore: 関連ファイル・既存パターン・影響範囲の特定
  ↓
【設計】 Architect に委任するか判断（下記基準参照）
  ↓
【Red】  テストを先に作成 → コンパイル/実行が失敗することを確認
  ↓
【Green】 最小実装 → テストが通ることを確認
  ↓
【文書】  DESIGN.md を更新（設計意図が変わった場合のみ）
  ↓
【記録】  ADR（設計変更あり）+ reports/ サマリー
  ↓
【PR】   gh pr create → CI → merge
```

#### Architect に委任する判断基準

以下のいずれかに該当する場合、実装前に Architect を起動する:

- 新しい構文・言語機能の追加（AST/Lexer/Parser/Codegen の変更を伴う）
- 既存インターフェースへの破壊的変更の可能性
- 複数モジュールにまたがる変更で影響範囲が不明確
- VimScript の制約（E704/E121/E932 等）が絡む複雑な設計

バグ修正・ドキュメント修正では Architect を省略して Dev Engineer に直接委任してよい。

#### ドキュメントの役割分担

| ドキュメント | 役割（何を書くか） | 更新タイミング |
|-------------|-----------------|--------------|
| **テストケース (.vmo)** | 詳細な動作仕様（正確な定義） | Red フェーズ（テスト作成時） |
| **DESIGN.md** | 設計意図・概念・言語全体の構造 | 機能の設計決定時のみ |
| **ADR** | なぜその設計にしたか | 実装完了後 |
| **reports/ サマリー** | 何をしたか・テスト結果 | Issue クローズ時 |

> **原則:** テストが「動く仕様書」として機能する。DESIGN.md に細かい動作を書くと二重管理になるため、DESIGN.md は「意図・概念・制約」に特化させる。

### 作業完了時の記録

- 作業終了時に `reports/YYYYMMDD-{topic}.md` に作業内容を記録する
- `{topic}` は作業内容を表す kebab-case（例: `closure-fix`, `lsp-hover`）
- モデル名はファイル名ではなくファイルの先頭に `**モデル:** claude-sonnet-4.6` として記載する
- 記録内容:
  - 完了したタスク
  - 新規作成/変更したファイル
  - テスト結果
  - 次のステップ

## デバッグチェックリスト

### LSP が動作しない（補完・診断・定義ジャンプが効かない）

1. `vimmo-ls.log` を確認: `cat /tmp/vimmo-ls.log` または Docker コンテナ内の `/app/vimmo-ls.log`
2. LSP サーバー自体は起動しているか確認: Neovim で `:LspInfo` を実行
3. pygls バージョンを確認: `pip show pygls`（2.x 系の API 変更に注意）
4. `packages/vimmo-ls/tests/` の pytest を実行して LSP ロジック単体の健全性を確認
5. server.py の `show_message` / `publish_diagnostics` が pygls 2.x 互換ラッパー経由か確認

### シンタックスハイライトが Neovim で表示されない

1. `queries/vimmo/` サブディレクトリが存在するか確認（`queries/` 直下ではなく `queries/vimmo/` が必要）
2. Treesitter のパーサーがインストールされているか: `:TSInstall vimmo` を実行
3. `runtimepath` に tree-sitter-vimmo のルートが含まれているか
4. `queries/vimmo/highlights.scm` の構文エラーがないか: `:TSPlaygroundToggle` で確認
5. Neovim を再起動して再確認

### VimScript 実行時エラー（E704 / E121 / E932）

| エラー | 確認箇所 | 対処 |
|--------|---------|------|
| E704 | `l:`/`s:` スコープの funcref 変数名 | `_cap_funcref_name()` が呼ばれているか確認 |
| E121 | block body lambda が外側の `l:` 変数を参照 | inline 定義 + `closure` キーワードになっているか確認 |
| E932 | トップレベル関数に `closure` が付いている | `function_depth == 0` 時の `closure` 省略ロジックを確認 |

### コンパイルエラー（ParseError / CodegenError）

```bash
# トークン列を確認
PYTHONPATH=packages/vimmo-core/src python packages/vimmo-core/src/vimmo/vimmo.py tokens <file.vmo>

# AST を確認
PYTHONPATH=packages/vimmo-core/src python packages/vimmo-core/src/vimmo/vimmo.py ast <file.vmo>
```

エラーメッセージに行・列番号が含まれているので、`ast` コマンドで部分的なパースを確認する。
