"""server.py のヘルパー関数テスト"""

import pytest
from lsprotocol.types import CompletionItemKind
from vimmo_ls.symbols import SymbolTable, SymbolInfo
from vimmo_ls.server import _get_member_items, _get_ident_at_position, _BUILTIN_METHODS


def make_table_with(symbols):
    table = SymbolTable("f")
    for s in symbols:
        table.add_symbol_info(s)
    return table


# --- _get_member_items ---


def test_list_type_returns_list_methods():
    table = make_table_with(
        [SymbolInfo(name="items", kind="variable", type_ann="list", line=1, col=0)]
    )
    items = _get_member_items("items", table)
    labels = {i.label for i in items}
    expected = {"map", "filter", "push", "pop", "len", "join"}
    assert expected.issubset(labels)
    assert all(i.kind == CompletionItemKind.Method for i in items)


def test_string_type_returns_string_methods():
    table = make_table_with(
        [SymbolInfo(name="s", kind="variable", type_ann="string", line=1, col=0)]
    )
    items = _get_member_items("s", table)
    labels = {i.label for i in items}
    assert {"split", "join", "len"}.issubset(labels)
    # list 専用メソッドは含まれない
    assert "map" not in labels
    assert "filter" not in labels


def test_dict_type_returns_dict_methods():
    table = make_table_with(
        [SymbolInfo(name="d", kind="variable", type_ann="dict", line=1, col=0)]
    )
    items = _get_member_items("d", table)
    labels = {i.label for i in items}
    assert {"keys", "values", "has"}.issubset(labels)


def test_class_type_returns_fields_and_methods():
    table = make_table_with(
        [
            SymbolInfo(name="todo", kind="variable", type_ann="Todo", line=1, col=0),
            SymbolInfo(
                name="Todo",
                kind="class",
                class_fields=["title", "done"],
                class_methods=["toggle"],
                line=0,
                col=0,
            ),
        ]
    )
    items = _get_member_items("todo", table)
    labels = {i.label for i in items}
    assert labels == {"title", "done", "toggle"}
    field_items = [i for i in items if i.label in ("title", "done")]
    method_items = [i for i in items if i.label == "toggle"]
    assert all(i.kind == CompletionItemKind.Field for i in field_items)
    assert all(i.kind == CompletionItemKind.Method for i in method_items)


def test_class_type_empty_returns_nothing():
    table = make_table_with(
        [
            SymbolInfo(name="obj", kind="variable", type_ann="Empty", line=1, col=0),
            SymbolInfo(
                name="Empty",
                kind="class",
                class_fields=[],
                class_methods=[],
                line=0,
                col=0,
            ),
        ]
    )
    items = _get_member_items("obj", table)
    assert items == []


def test_no_table_returns_all_builtin_methods():
    items = _get_member_items("anything", table=None)
    labels = {i.label for i in items}
    # 全ビルトインメソッドのunion
    all_methods = set()
    for methods in _BUILTIN_METHODS.values():
        for name, _, _ in methods:
            all_methods.add(name)
    assert all_methods.issubset(labels)
    # 重複なし
    label_list = [i.label for i in items]
    assert len(label_list) == len(set(label_list))


def test_unknown_symbol_falls_back_to_all_builtins():
    table = SymbolTable("f")  # シンボルなし
    items = _get_member_items("unknown_var", table)
    labels = {i.label for i in items}
    all_methods = set()
    for methods in _BUILTIN_METHODS.values():
        for name, _, _ in methods:
            all_methods.add(name)
    assert all_methods.issubset(labels)


def test_no_type_annotation_falls_back_to_all_builtins():
    table = make_table_with(
        [SymbolInfo(name="x", kind="variable", type_ann=None, line=1, col=0)]
    )
    items = _get_member_items("x", table)
    labels = {i.label for i in items}
    assert "map" in labels
    assert "split" in labels
    assert "keys" in labels


# --- _get_ident_at_position ---


def test_get_ident_cursor_in_middle_of_word():
    assert _get_ident_at_position("let fooBar = 1", line=0, col=6) == "fooBar"


def test_get_ident_cursor_at_word_start():
    assert _get_ident_at_position("let fooBar = 1", line=0, col=4) == "fooBar"


def test_get_ident_cursor_on_space_returns_none():
    assert _get_ident_at_position("let x = 1", line=0, col=3) is None


def test_get_ident_line_out_of_range_returns_none():
    assert _get_ident_at_position("let x = 1", line=99, col=0) is None


def test_get_ident_includes_underscores():
    assert _get_ident_at_position("let my_var = 1", line=0, col=5) == "my_var"


def test_get_ident_multiline_source():
    source = "let a = 1\nlet target = 2\nlet c = 3"
    assert _get_ident_at_position(source, line=1, col=4) == "target"
