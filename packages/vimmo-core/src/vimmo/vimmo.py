#!/usr/bin/env python3
"""
vimmo — VimMo transpiler CLI
Usage:
  vimmo compile <file.vmo>           Compile to <file.vim>
  vimmo compile <file.vmo> -o <out>  Compile to specified output
  vimmo check   <file.vmo>           Syntax check only
  vimmo tokens  <file.vmo>           Dump tokens (debug)
  vimmo ast     <file.vmo>           Dump AST (debug)
"""

import sys
import os
import argparse
from pathlib import Path

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from codegen import Codegen, CodegenError


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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
