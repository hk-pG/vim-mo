# vimmo-core 内 parser.py / codegen.py のベアインポートを解決するための
# sys.modules エイリアス登録。これを他の vimmo.* インポートより先に実行する必要がある。
import sys as _sys
import importlib as _importlib


def _register_vimmo_bare_imports():
    """vimmo.* を先にロードし、bare name でも参照できるよう sys.modules に登録する。"""
    for _mod in ("lexer", "ast_nodes", "parser", "codegen"):
        _full = f"vimmo.{_mod}"
        if _full not in _sys.modules:
            _importlib.import_module(_full)
        if _mod not in _sys.modules:
            _sys.modules[_mod] = _sys.modules[_full]


_register_vimmo_bare_imports()

import logging as _logging

# LSP サーバーのデバッグログを /app/vimmo-ls.log に出力する
# Docker 環境では /app が .:/app でホストにマウントされているため、
# ホスト側 /Users/hk-p/repo/vim-mo/vimmo-ls.log から直接参照できる
_logging.basicConfig(
    level=_logging.DEBUG,
    filename="/app/vimmo-ls.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

try:
    from pygls.server import LanguageServer
except ImportError:
    from pygls.lsp.server import LanguageServer

from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_COMPLETION,
    WINDOW_SHOW_MESSAGE,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    InsertTextFormat,
    Diagnostic,
    PublishDiagnosticsParams,
    ShowMessageParams,
    MessageType,
    Position,
    Range,
    Location,
)
from vimmo.lexer import Lexer, LexerError
from vimmo.parser import Parser, ParseError
from vimmo_ls.symbols import build_symbol_table


class VimMoLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


_logger = _logging.getLogger("vimmo-ls")


def _show_message(ls, message):
    """pygls バージョン互換 show_message"""
    if hasattr(ls, "show_message"):
        ls.show_message(message)
        return
    # pygls 2.x: protocol.notify 経由
    if hasattr(ls, "protocol") and hasattr(ls.protocol, "notify"):
        try:
            ls.protocol.notify(
                WINDOW_SHOW_MESSAGE,
                ShowMessageParams(type=MessageType.Info, message=message),
            )
            return
        except Exception as e:
            _logger.debug("_show_message via protocol.notify failed: %s", e)
    _logger.info(message)


def _publish_diagnostics(ls, uri, diagnostics):
    """pygls バージョン互換 publish_diagnostics"""
    if hasattr(ls, "publish_diagnostics"):
        ls.publish_diagnostics(uri, diagnostics)
        return
    params = PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
    # pygls 2.x: protocol.notify 経由
    if hasattr(ls, "protocol") and hasattr(ls.protocol, "notify"):
        try:
            ls.protocol.notify("textDocument/publishDiagnostics", params)
            return
        except Exception as e:
            _logger.debug("_publish_diagnostics via protocol.notify failed: %s", e)
    # pygls 1.x: send_notification 直接
    for method_name in ("send_notification", "_send_notification"):
        fn = getattr(ls, method_name, None)
        if fn is not None:
            try:
                fn("textDocument/publishDiagnostics", params)
                return
            except Exception as e:
                _logger.debug(
                    "_publish_diagnostics via ls.%s failed: %s", method_name, e
                )
    _logger.warning("publish_diagnostics: no compatible API found in pygls")


server = VimMoLanguageServer("vimmo-ls", "v0.1.0")


_KEYWORDS = [
    "let",
    "const",
    "fn",
    "async",
    "await",
    "return",
    "if",
    "else",
    "for",
    "in",
    "while",
    "break",
    "continue",
    "import",
    "from",
    "class",
    "self",
    "echo",
    "new",
    "true",
    "false",
    "null",
]

_TYPE_KEYWORDS = ["number", "string", "bool", "list", "dict", "any", "void"]

_BUILTIN_METHODS = {
    "list": [
        ("map", "map(callback)", "map(callback: fn) -> list"),
        ("filter", "filter(callback)", "filter(callback: fn) -> list"),
        ("push", "push(value)", "push(value: any) -> void"),
        ("pop", "pop()", "pop() -> any"),
        ("len", "len()", "len() -> number"),
        ("join", "join(separator)", "join(separator: string) -> string"),
    ],
    "string": [
        ("split", "split(separator)", "split(separator: string) -> list"),
        ("join", "join(separator)", "join(separator: string) -> string"),
        ("len", "len()", "len() -> number"),
    ],
    "dict": [
        ("keys", "keys()", "keys() -> list"),
        ("values", "values()", "values() -> list"),
        ("has", "has(key)", "has(key: string) -> bool"),
    ],
}

_BUILTIN_FUNCTIONS = [
    (
        "autocmd",
        "autocmd(event, pattern, callback)",
        "autocmd(event: string, pattern: string, callback: fn) -> void",
    ),
    (
        "command",
        "command(name, callback)",
        "command(name: string, callback: fn) -> void",
    ),
    (
        "map",
        "map(mode, lhs, callback)",
        "map(mode: string, lhs: string, callback: fn) -> void",
    ),
    ("job", "job(cmd)", "job(cmd: string) -> any"),
]


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: VimMoLanguageServer, params):
    _show_message(ls, "VimMo Language Server connected")
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: VimMoLanguageServer, params):
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: VimMoLanguageServer, params):
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DEFINITION)
async def definition(ls: VimMoLanguageServer, params):
    uri = params.text_document.uri
    doc = ls.workspace.text_documents.get(uri)
    if doc is None:
        _logger.debug("definition: doc is None for uri=%s", uri)
        return None

    source = doc.source if hasattr(doc, "source") else getattr(doc, "text", None)
    if source is None:
        _logger.debug("definition: doc has neither .source nor .text")
        return None

    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
    except (LexerError, ParseError) as e:
        _logger.debug("definition: parse/lex error: %s", e)
        return None
    except Exception as e:
        _logger.debug("definition: unexpected error during parse: %s", e)
        return None

    table = build_symbol_table(uri, program)

    line = params.position.line
    col = params.position.character
    _logger.debug("definition: line=%d col=%d", line, col)

    ident = _get_ident_at_position(source, line, col)
    _logger.debug("definition: ident=%r", ident)
    if not ident:
        return None

    loc = table.find_definition(ident, line, col)
    _logger.debug(
        "definition: ident=%r find_definition result=%r defs=%r",
        ident,
        loc,
        table.definitions.get(ident),
    )
    if loc:
        return Location(
            uri=loc.uri,
            range=Range(
                start=Position(line=loc.line, character=loc.col),
                end=Position(line=loc.line, character=loc.col + 10),
            ),
        )
    return None


@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["."]))
async def completion(ls: VimMoLanguageServer, params: CompletionParams):
    doc = ls.workspace.text_documents.get(params.text_document.uri)
    if doc is None:
        return CompletionList(is_incomplete=False, items=[])
    line = params.position.line
    col = params.position.character

    program = None
    try:
        tokens = Lexer(doc.source).tokenize()
        program = Parser(tokens).parse()
    except Exception:
        pass

    table = None
    if program is not None:
        table = build_symbol_table(params.text_document.uri, program)

    lines = doc.source.split("\n")
    current_line = lines[line] if line < len(lines) else ""
    before_cursor = current_line[:col]

    import re

    dot_match = re.search(r"(\w+)\.$", before_cursor)
    if dot_match:
        obj_name = dot_match.group(1)
        return CompletionList(
            is_incomplete=False, items=_get_member_items(obj_name, table)
        )

    items = []

    for kw in _KEYWORDS + _TYPE_KEYWORDS:
        items.append(
            CompletionItem(
                label=kw,
                kind=CompletionItemKind.Keyword,
            )
        )

    for name, insert_text, detail in _BUILTIN_FUNCTIONS:
        items.append(
            CompletionItem(
                label=name,
                kind=CompletionItemKind.Function,
                insert_text=insert_text,
                insert_text_format=InsertTextFormat.PlainText,
                detail=detail,
            )
        )

    if table is not None:
        visible = table.get_symbols_visible_at(line, col)
        for sym in visible:
            if sym.kind == "variable":
                items.append(
                    CompletionItem(
                        label=sym.name,
                        kind=CompletionItemKind.Variable,
                        detail=f": {sym.type_ann}" if sym.type_ann else None,
                    )
                )
            elif sym.kind == "function":
                param_str = ", ".join(
                    p[0] if isinstance(p, (list, tuple)) else str(p)
                    for p in (sym.params or [])
                )
                items.append(
                    CompletionItem(
                        label=sym.name,
                        kind=CompletionItemKind.Function,
                        insert_text=f"{sym.name}({param_str})",
                        insert_text_format=InsertTextFormat.PlainText,
                        detail=f"fn {sym.name}({param_str})",
                    )
                )
            elif sym.kind == "class":
                items.append(
                    CompletionItem(
                        label=sym.name,
                        kind=CompletionItemKind.Class,
                    )
                )
            elif sym.kind == "parameter":
                items.append(
                    CompletionItem(
                        label=sym.name,
                        kind=CompletionItemKind.Variable,
                        detail=f": {sym.type_ann}" if sym.type_ann else ": any",
                    )
                )

    return CompletionList(is_incomplete=False, items=items)


def _get_member_items(obj_name: str, table) -> list:
    """Return dot-completion candidates."""
    items = []

    type_ann = None
    class_name = None
    if table is not None:
        sym = table.get_symbol_info(obj_name)
        if sym is not None:
            type_ann = sym.type_ann
            if type_ann and type_ann not in (
                "number",
                "string",
                "bool",
                "list",
                "dict",
                "any",
                "void",
            ):
                class_name = type_ann

    if class_name and table is not None:
        class_info = table.get_class_info(class_name)
        if class_info:
            for field_name in class_info.class_fields or []:
                items.append(
                    CompletionItem(label=field_name, kind=CompletionItemKind.Field)
                )
            for method_name in class_info.class_methods or []:
                items.append(
                    CompletionItem(label=method_name, kind=CompletionItemKind.Method)
                )
            return items

    methods_list = []
    if type_ann in _BUILTIN_METHODS:
        methods_list = _BUILTIN_METHODS[type_ann]
    else:
        for methods in _BUILTIN_METHODS.values():
            methods_list.extend(methods)

    seen = set()
    for name, insert_text, detail in methods_list:
        if name not in seen:
            seen.add(name)
            items.append(
                CompletionItem(
                    label=name,
                    kind=CompletionItemKind.Method,
                    insert_text=insert_text,
                    insert_text_format=InsertTextFormat.PlainText,
                    detail=detail,
                )
            )

    return items


def _get_ident_at_position(source: str, line: int, col: int) -> str:
    """Extract identifier at given position."""
    lines = source.split("\n")
    if line >= len(lines):
        return None

    target_line = lines[line]

    if col >= len(target_line) or not (
        target_line[col].isalnum() or target_line[col] == "_"
    ):
        return None

    start = col
    end = col

    while start > 0 and (
        target_line[start - 1].isalnum() or target_line[start - 1] == "_"
    ):
        start -= 1

    while end < len(target_line) and (
        target_line[end].isalnum() or target_line[end] == "_"
    ):
        end += 1

    if start == end:
        return None

    return target_line[start:end]


def _validate(ls: VimMoLanguageServer, uri: str):
    doc = ls.workspace.text_documents.get(uri)
    if doc is None:
        return
    diagnostics = []

    try:
        tokens = Lexer(doc.source).tokenize()
        Parser(tokens).parse()
    except (LexerError, ParseError) as e:
        # Simple error position mapping
        # E.g., ParseError at 3:5: ...
        import re

        match = re.search(r"at (\d+):(\d+): (.*)", str(e))
        if match:
            line = int(match.group(1)) - 1
            col = int(match.group(2)) - 1
            msg = match.group(3)

            diagnostics.append(
                Diagnostic(
                    range=Range(
                        start=Position(line=line, character=col),
                        end=Position(line=line, character=col + 5),  # approximation
                    ),
                    message=msg,
                    source="vimmo-ls",
                )
            )
        else:
            # Fallback if regex fails
            diagnostics.append(
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 1)),
                    message=str(e),
                    source="vimmo-ls",
                )
            )

    _publish_diagnostics(ls, uri, diagnostics)


def main():
    server.start_io()


if __name__ == "__main__":
    main()
