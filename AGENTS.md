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

- 重要な設計決定を行った場合は `reports/ADR-XXX-{feature-name}.md` にADRを記録する
- ADRには以下を含める:
  - ステータス (草案/承認済み/Deprecated)
  - 決定事項
  - 変更されたファイル
  - テスト結果

### 作業完了時の記録

- 作業終了時に `reports/` にmarkdown形式で作業内容を記録する
- ファイル名: `YYYYMMDD-{model-name}-summary.md`
- 記録内容:
  - 完了したタスク
  - 新規作成/変更したファイル
  - テスト結果
  - 次のステップ
