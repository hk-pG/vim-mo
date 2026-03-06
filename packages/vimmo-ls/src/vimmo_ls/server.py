from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_DEFINITION,
    Diagnostic,
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


server = VimMoLanguageServer("vimmo-ls", "v0.1.0")


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: VimMoLanguageServer, params):
    ls.show_message("VimMo Language Server connected")
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: VimMoLanguageServer, params):
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: VimMoLanguageServer, params):
    _validate(ls, params.text_document.uri)


@server.feature(TEXT_DOCUMENT_DEFINITION)
async def definition(ls: VimMoLanguageServer, params):
    doc = ls.workspace.get_document(params.text_document.uri)

    try:
        tokens = Lexer(doc.source).tokenize()
        program = Parser(tokens).parse()
    except (LexerError, ParseError):
        return None

    table = build_symbol_table(params.text_document.uri, program)

    line = params.position.line
    col = params.position.character

    ident = _get_ident_at_position(doc.source, line, col)
    if not ident:
        return None

    loc = table.find_definition(ident, line, col)
    if loc:
        return Location(
            uri=loc.uri,
            range=Range(
                start=Position(line=loc.line, character=loc.col),
                end=Position(line=loc.line, character=loc.col + 10),
            ),
        )
    return None


def _get_ident_at_position(source: str, line: int, col: int) -> str:
    """Extract identifier at given position."""
    lines = source.split("\n")
    if line >= len(lines):
        return None

    target_line = lines[line]

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
    doc = ls.workspace.get_document(uri)
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

    ls.publish_diagnostics(uri, diagnostics)


def main():
    server.start_io()


if __name__ == "__main__":
    main()
