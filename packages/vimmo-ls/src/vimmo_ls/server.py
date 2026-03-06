from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    Diagnostic,
    Position,
    Range,
)
from vimmo.lexer import Lexer, LexerError
from vimmo.parser import Parser, ParseError

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
            
            diagnostics.append(Diagnostic(
                range=Range(
                    start=Position(line=line, character=col),
                    end=Position(line=line, character=col + 5) # approximation
                ),
                message=msg,
                source="vimmo-ls"
            ))
        else:
            # Fallback if regex fails
            diagnostics.append(Diagnostic(
                range=Range(start=Position(0,0), end=Position(0,1)),
                message=str(e),
                source="vimmo-ls"
            ))

    ls.publish_diagnostics(uri, diagnostics)

def main():
    server.start_io()

if __name__ == "__main__":
    main()
