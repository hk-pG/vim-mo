import sys
import pathlib

_REPO_ROOT = pathlib.Path(__file__).parents[3]  # vim-mo/


def _prepend(p: pathlib.Path) -> None:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


def _append(p: pathlib.Path) -> None:
    s = str(p)
    if s not in sys.path:
        sys.path.append(s)


# 1. vimmo パッケージ (namespace package) が先に解決されるよう src を prepend
_prepend(_REPO_ROOT / "packages/vimmo-core/src")
_prepend(_REPO_ROOT / "packages/vimmo-ls/src")

# 2. vimmo.lexer と vimmo.ast_nodes を先にロードし、bare name でエイリアス登録する。
#    parser.py / codegen.py が `from lexer import ...` などを使うため、
#    それらをインポートする前にエイリアスを sys.modules に登録する必要がある。
import vimmo.lexer  # noqa: E402
import vimmo.ast_nodes  # noqa: E402

# 3. vimmo-core 内部の bare import (`from lexer import ...` 等) が
#    同じモジュールインスタンスを参照するよう、bare name でもエイリアスを登録する。
#    これにより TokenType などの Enum 同一性が保たれる。
for _bare in ("lexer", "ast_nodes"):
    if _bare not in sys.modules:
        sys.modules[_bare] = sys.modules[f"vimmo.{_bare}"]

# 4. bare alias を登録した後で parser / codegen をロードする
import vimmo.parser  # noqa: E402
import vimmo.codegen  # noqa: E402

for _bare in ("parser", "codegen"):
    if _bare not in sys.modules:
        sys.modules[_bare] = sys.modules[f"vimmo.{_bare}"]

# 4. src/vimmo/ を末尾に追加しておく（直接インポートが必要な場合のフォールバック）
import importlib as _importlib  # noqa: E402

_append(_REPO_ROOT / "packages/vimmo-core/src/vimmo")
_importlib.invalidate_caches()
