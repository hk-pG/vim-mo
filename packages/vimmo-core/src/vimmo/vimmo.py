#!/usr/bin/env python3
"""
vimmo — VimMo transpiler CLI
Usage:
  vimmo compile <file.vmo>           Compile to <file.vim>
  vimmo compile <file.vmo> -o <out>  Compile to specified output
  vimmo check   <file.vmo>           Syntax check only
  vimmo tokens  <file.vmo>           Dump tokens (debug)
  vimmo ast     <file.vmo>           Dump AST (debug)
  vimmo watch   <dir>                Watch directory and auto-compile on save
"""

import sys
import os
import argparse
from pathlib import Path

try:
    from vimmo.lexer import Lexer, LexerError
    from vimmo.parser import Parser, ParseError
    from vimmo.codegen import Codegen, CodegenError
except ImportError:
    from lexer import Lexer, LexerError  # type: ignore[no-redef]
    from parser import Parser, ParseError  # type: ignore[no-redef]
    from codegen import Codegen, CodegenError  # type: ignore[no-redef]


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)


def compile_source(source: str, filename: str = "<input>") -> str:
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        return Codegen().generate(ast)
    except LexerError as e:
        print(f"[{filename}] {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"[{filename}] {e}", file=sys.stderr)
        sys.exit(1)
    except CodegenError as e:
        print(f"[{filename}] CodegenError: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_compile(args):
    source = read_file(args.input)
    vim_code = compile_source(source, args.input)
    if args.output:
        out_path = args.output
    else:
        out_path = str(Path(args.input).with_suffix(".vim"))
    Path(out_path).write_text(vim_code, encoding="utf-8")
    print(f"✓ Compiled: {args.input} → {out_path}")


def cmd_check(args):
    source = read_file(args.input)
    compile_source(source, args.input)  # will sys.exit on error
    print(f"✓ Syntax OK: {args.input}")


def cmd_tokens(args):
    source = read_file(args.input)
    try:
        tokens = Lexer(source).tokenize()
        for tok in tokens:
            print(tok)
    except LexerError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def cmd_ast(args):
    import pprint

    source = read_file(args.input)
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        pprint.pprint(ast)
    except (LexerError, ParseError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def _compile_file_safe(vmo_path: Path) -> tuple[bool, str]:
    """コンパイルを試みる。成功時は (True, vim_code)、失敗時は (False, error_message) を返す。"""
    try:
        source = vmo_path.read_text(encoding="utf-8")
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        vim_code = Codegen().generate(ast)
        return True, vim_code
    except (LexerError, ParseError, CodegenError) as e:
        return False, str(e)


def _compile_and_report(vmo_path: Path) -> None:
    """ファイルをコンパイルして結果をターミナルに表示する。"""
    ok, result = _compile_file_safe(vmo_path)
    out_path = vmo_path.with_suffix(".vim")
    if ok:
        out_path.write_text(result, encoding="utf-8")
        print(f"  ✓  {vmo_path.name} → {out_path.name}", flush=True)
    else:
        print(f"  ✗  {vmo_path.name}: {result}", file=sys.stderr, flush=True)


def cmd_watch(args):
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print(
            "Error: 'watchdog' is not installed. Run: pip install watchdog",
            file=sys.stderr,
        )
        sys.exit(1)

    watch_dir = Path(args.directory).resolve()
    if not watch_dir.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    class _Handler(FileSystemEventHandler):
        def _handle(self, path_str: str) -> None:
            if path_str.endswith(".vmo"):
                _compile_and_report(Path(path_str))

        def on_modified(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

        def on_created(self, event):
            if not event.is_directory:
                self._handle(event.src_path)

    import time

    observer = Observer()
    observer.schedule(_Handler(), str(watch_dir), recursive=args.recursive)
    observer.start()
    print(f"Watching {watch_dir} for .vmo changes... (Ctrl+C to stop)", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(
        prog="vimmo",
        description="VimMo — Modern scripting language for Vim plugin development",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # compile
    p_compile = sub.add_parser("compile", help="Compile .vmo → .vim")
    p_compile.add_argument("input", help="Input .vmo file")
    p_compile.add_argument("-o", "--output", help="Output .vim file")
    p_compile.set_defaults(func=cmd_compile)

    # check
    p_check = sub.add_parser("check", help="Syntax check only")
    p_check.add_argument("input", help="Input .vmo file")
    p_check.set_defaults(func=cmd_check)

    # tokens
    p_tokens = sub.add_parser("tokens", help="Dump token stream")
    p_tokens.add_argument("input", help="Input .vmo file")
    p_tokens.set_defaults(func=cmd_tokens)

    # ast
    p_ast = sub.add_parser("ast", help="Dump AST")
    p_ast.add_argument("input", help="Input .vmo file")
    p_ast.set_defaults(func=cmd_ast)

    # watch
    p_watch = sub.add_parser(
        "watch", help="Watch directory and auto-compile .vmo on save"
    )
    p_watch.add_argument("directory", help="Directory to watch")
    p_watch.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Watch subdirectories recursively",
    )
    p_watch.set_defaults(func=cmd_watch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
