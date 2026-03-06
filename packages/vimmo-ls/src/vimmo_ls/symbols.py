from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Location:
    uri: str
    line: int
    col: int


class SymbolTable:
    def __init__(self, uri: str):
        self.uri = uri
        self.definitions: Dict[str, List[Location]] = {}

    def add_definition(self, name: str, line: int, col: int):
        if name not in self.definitions:
            self.definitions[name] = []
        self.definitions[name].append(Location(self.uri, line, col))

    def find_definition(self, name: str, line: int, col: int) -> Optional[Location]:
        """Find definition of identifier at given position.

        Returns the most recent definition that appears before the given position.
        """
        if name not in self.definitions:
            return None

        candidates = []
        for loc in self.definitions[name]:
            if loc.line < line or (loc.line == line and loc.col < col):
                candidates.append(loc)

        if not candidates:
            return None

        candidates.sort(key=lambda x: (x.line, x.col), reverse=True)
        return candidates[0]


def build_symbol_table(uri: str, node) -> SymbolTable:
    """Build symbol table from AST."""
    table = SymbolTable(uri)
    _walk(node, table)
    return table


def _walk(node, table: SymbolTable):
    """Walk AST and collect definitions."""
    from ast_nodes import (
        Program,
        VarDecl,
        FnDecl,
        ClassDecl,
        Block,
        If,
        For,
        While,
        Return,
        Echo,
        ExprStmt,
        Assign,
        AugAssign,
        BinOp,
        UnaryOp,
        Ident,
        Call,
        Lambda,
        Pipeline,
        New,
        Import,
        ListLit,
        DictLit,
        Index,
        Attr,
        NumberLit,
        StringLit,
        BoolLit,
        NullLit,
        Await,
        Break,
        Continue,
    )

    if node is None:
        return

    if isinstance(node, VarDecl):
        table.add_definition(node.name, node.line or 0, node.col or 0)

    elif isinstance(node, FnDecl):
        table.add_definition(node.name, node.line or 0, node.col or 0)

    elif isinstance(node, ClassDecl):
        table.add_definition(node.name, node.line or 0, node.col or 0)

    elif isinstance(node, Program):
        for stmt in node.body:
            _walk(stmt, table)

    elif isinstance(node, Block):
        for stmt in node.stmts:
            _walk(stmt, table)

    elif isinstance(node, If):
        _walk(node.condition, table)
        _walk(node.then, table)
        for cond, block in node.elseifs:
            _walk(cond, table)
            _walk(block, table)
        if node.else_:
            _walk(node.else_, table)

    elif isinstance(node, For):
        _walk(node.iterable, table)
        _walk(node.body, table)

    elif isinstance(node, While):
        _walk(node.condition, table)
        _walk(node.body, table)

    elif isinstance(node, Return):
        if node.value:
            _walk(node.value, table)

    elif isinstance(node, Echo):
        _walk(node.value, table)

    elif isinstance(node, ExprStmt):
        _walk(node.expr, table)

    elif isinstance(node, Assign):
        _walk(node.target, table)
        _walk(node.value, table)

    elif isinstance(node, AugAssign):
        _walk(node.target, table)
        _walk(node.value, table)

    elif isinstance(node, BinOp):
        _walk(node.left, table)
        _walk(node.right, table)

    elif isinstance(node, UnaryOp):
        _walk(node.operand, table)

    elif isinstance(node, Lambda):
        _walk(node.body, table)

    elif isinstance(node, Pipeline):
        _walk(node.left, table)
        _walk(node.right, table)

    elif isinstance(node, Call):
        _walk(node.callee, table)
        for arg in node.args:
            _walk(arg, table)

    elif isinstance(node, New):
        for arg in node.args:
            _walk(arg, table)

    elif isinstance(node, Import):
        pass

    elif isinstance(node, ListLit):
        for elem in node.elements:
            _walk(elem, table)

    elif isinstance(node, DictLit):
        for key, val in node.pairs:
            _walk(key, table)
            _walk(val, table)

    elif isinstance(node, Index):
        _walk(node.obj, table)
        _walk(node.index, table)

    elif isinstance(node, Attr):
        _walk(node.obj, table)

    elif isinstance(node, Await):
        _walk(node.expr, table)

    elif isinstance(node, (NumberLit, StringLit, BoolLit, NullLit, Break, Continue)):
        pass
