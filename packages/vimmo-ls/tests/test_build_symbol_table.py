"""build_symbol_table / _walk のテスト"""

import sys
import pathlib
import pytest

# conftest.py で sys.path 設定済み
from vimmo_ls.symbols import build_symbol_table, SymbolTable, SymbolInfo
from vimmo.ast_nodes import (
    Program,
    Block,
    VarDecl,
    FnDecl,
    ClassDecl,
    If,
    For,
    While,
    BoolLit,
    NullLit,
)


def make_program(*stmts):
    """ヘルパー: stmts を持つ Program ノードを返す"""
    return Program(body=list(stmts))


def make_var(name, type_ann=None, kind="let", line=1, col=0):
    node = VarDecl(kind=kind, name=name, type_ann=type_ann, value=None)
    node.line = line
    node.col = col
    return node


def make_fn(name, params=None, line=1, col=0):
    if params is None:
        params = []
    node = FnDecl(
        name=name, params=params, return_type=None, body=Block(stmts=[]), is_async=False
    )
    node.line = line
    node.col = col
    return node


def make_class(name, fields=None, methods=None, line=1, col=0):
    if fields is None:
        fields = []
    if methods is None:
        methods = []
    node = ClassDecl(name=name, fields=fields, methods=methods)
    node.line = line
    node.col = col
    return node


def build(uri="file:///a.vmo", *stmts):
    return build_symbol_table(uri, make_program(*stmts))


# --- VarDecl ---


def test_var_decl_produces_variable_symbol():
    table = build_symbol_table("f", make_program(make_var("x", line=1)))
    sym = table.get_symbol_info("x")
    assert sym is not None
    assert sym.kind == "variable"
    assert sym.line == 1


def test_var_decl_preserves_type_annotation():
    table = build_symbol_table("f", make_program(make_var("count", type_ann="number")))
    assert table.get_symbol_info("count").type_ann == "number"


def test_var_decl_no_type_annotation():
    table = build_symbol_table("f", make_program(make_var("x")))
    assert table.get_symbol_info("x").type_ann is None


# --- FnDecl ---


def test_fn_decl_produces_function_symbol():
    fn = make_fn("greet", params=[("name", "string")], line=3)
    table = build_symbol_table("f", make_program(fn))
    sym = table.get_symbol_info("greet")
    assert sym is not None
    assert sym.kind == "function"
    assert sym.params == [("name", "string")]


def test_fn_params_added_as_parameter_symbols():
    fn = make_fn("add", params=[("a", "number"), ("b", "number")])
    table = build_symbol_table("f", make_program(fn))
    for pname in ("a", "b"):
        sym = table.get_symbol_info(pname)
        assert sym is not None
        assert sym.kind == "parameter"
        assert sym.type_ann == "number"


def test_fn_param_without_type():
    fn = make_fn("f", params=[("x", None)])
    table = build_symbol_table("f", make_program(fn))
    assert table.get_symbol_info("x").type_ann is None


# --- ClassDecl ---


def test_class_decl_produces_class_symbol():
    cls = make_class(
        "Todo",
        fields=[make_var("title"), make_var("done")],
        methods=[make_fn("toggle")],
    )
    table = build_symbol_table("f", make_program(cls))
    info = table.get_class_info("Todo")
    assert info is not None
    assert info.kind == "class"
    assert "title" in info.class_fields
    assert "done" in info.class_fields
    assert "toggle" in info.class_methods


# --- Block / ネスト ---


def test_var_inside_block():
    program = make_program(Block(stmts=[make_var("inner")]))
    table = build_symbol_table("f", program)
    assert table.get_symbol_info("inner") is not None


# --- For ループ変数 ---


def test_for_loop_var_is_collected():
    node = For(var="item", iterable=NullLit(), body=Block(stmts=[]))
    table = build_symbol_table("f", make_program(node))
    sym = table.get_symbol_info("item")
    assert sym is not None
    assert sym.kind == "variable"


# --- 空 ---


def test_empty_program():
    table = build_symbol_table("f", Program(body=[]))
    assert table.symbol_infos == []
    assert table.definitions == {}


# --- find_definition との連携 ---


def test_var_decl_adds_definition_for_lookup():
    table = build_symbol_table("f", make_program(make_var("x", line=2)))
    loc = table.find_definition("x", line=5, col=0)
    assert loc is not None
    assert loc.line == 2


# --- If 両ブランチ ---


def test_if_both_branches_walked():
    node = If(
        condition=BoolLit(value=True),
        then=Block(stmts=[make_var("a")]),
        elseifs=[],
        else_=Block(stmts=[make_var("b")]),
    )
    table = build_symbol_table("f", make_program(node))
    assert table.get_symbol_info("a") is not None
    assert table.get_symbol_info("b") is not None


# --- 統合テスト (ソースパース) ---


def test_integration_basic_source():
    from vimmo.lexer import Lexer
    from vimmo.parser import Parser

    source = """
let x: number = 1
fn add(a: number, b: number): number { return a + b }
""".strip()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    table = build_symbol_table("f", program)
    assert table.get_symbol_info("x").kind == "variable"
    assert table.get_symbol_info("add").kind == "function"
    assert table.get_symbol_info("a").kind == "parameter"


def test_integration_class_source():
    from vimmo.lexer import Lexer
    from vimmo.parser import Parser

    source = """
class Person {
  let name: string = ""
  fn greet(): void {}
}
""".strip()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    table = build_symbol_table("f", program)
    info = table.get_class_info("Person")
    assert info is not None
    assert "name" in info.class_fields
    assert "greet" in info.class_methods
