"""SymbolTable クラスの単体テスト"""

import pytest
from vimmo_ls.symbols import SymbolTable, SymbolInfo


def make_table(uri="file:///a.vmo"):
    return SymbolTable(uri)


# --- find_definition ---


def test_add_and_find_definition_basic():
    table = make_table()
    table.add_definition("x", line=5, col=0)
    loc = table.find_definition("x", line=6, col=0)
    assert loc is not None
    assert loc.uri == "file:///a.vmo"
    assert loc.line == 5
    assert loc.col == 0


def test_find_definition_returns_none_for_unknown_name():
    table = make_table()
    assert table.find_definition("y", line=1, col=0) is None


def test_find_definition_excludes_same_position():
    table = make_table()
    table.add_definition("x", line=5, col=0)
    # 同一行・同一列は「前」ではないので除外される
    result = table.find_definition("x", line=5, col=0)
    assert result is None


def test_find_definition_returns_latest_before_position():
    table = make_table()
    table.add_definition("x", line=2, col=0)
    table.add_definition("x", line=7, col=0)
    loc = table.find_definition("x", line=10, col=0)
    assert loc.line == 7


def test_find_definition_skips_definitions_after_query():
    table = make_table()
    table.add_definition("x", line=2, col=0)
    table.add_definition("x", line=10, col=0)
    loc = table.find_definition("x", line=5, col=0)
    assert loc.line == 2


# --- get_symbols_visible_at ---


def test_get_symbols_visible_at_filters_by_line():
    table = make_table()
    table.add_symbol_info(SymbolInfo(name="a", kind="variable", line=3, col=0))
    table.add_symbol_info(SymbolInfo(name="b", kind="variable", line=8, col=0))
    visible = table.get_symbols_visible_at(line=5, col=0)
    names = [s.name for s in visible]
    assert "a" in names
    assert "b" not in names


def test_get_symbols_visible_at_same_line_uses_col():
    table = make_table()
    table.add_symbol_info(SymbolInfo(name="a", kind="variable", line=5, col=3))
    table.add_symbol_info(SymbolInfo(name="b", kind="variable", line=5, col=10))
    visible = table.get_symbols_visible_at(line=5, col=7)
    names = [s.name for s in visible]
    assert "a" in names
    assert "b" not in names


# --- get_symbol_info ---


def test_get_symbol_info_returns_first_match():
    table = make_table()
    table.add_symbol_info(SymbolInfo(name="foo", kind="function", line=1, col=0))
    sym = table.get_symbol_info("foo")
    assert sym is not None
    assert sym.kind == "function"
    assert sym.name == "foo"


def test_get_symbol_info_returns_none_for_missing():
    table = make_table()
    assert table.get_symbol_info("not_defined") is None


# --- get_class_info ---


def test_get_class_info_returns_class_symbol():
    table = make_table()
    table.add_symbol_info(
        SymbolInfo(
            name="Person",
            kind="class",
            class_fields=["name", "age"],
            class_methods=["greet"],
            line=1,
            col=0,
        )
    )
    info = table.get_class_info("Person")
    assert info is not None
    assert info.class_fields == ["name", "age"]
    assert info.class_methods == ["greet"]


def test_get_class_info_ignores_non_class_symbols():
    table = make_table()
    table.add_symbol_info(SymbolInfo(name="Person", kind="variable", line=1, col=0))
    assert table.get_class_info("Person") is None
