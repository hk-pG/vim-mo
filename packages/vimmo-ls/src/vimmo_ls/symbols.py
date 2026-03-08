from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Location:
    uri: str
    line: int
    col: int


@dataclass
class SymbolInfo:
    name: str
    kind: str  # 'variable', 'function', 'class', 'parameter'
    type_ann: Optional[str] = None
    params: Optional[List[Tuple[str, Optional[str]]]] = None
    class_fields: Optional[List[str]] = None
    class_methods: Optional[List[str]] = None
    line: int = 0
    col: int = 0


class SymbolTable:
    def __init__(self, uri: str):
        self.uri = uri
        self.definitions: Dict[str, List[Location]] = {}
        self.symbol_infos: List[SymbolInfo] = []

    def add_definition(self, name: str, line: int, col: int):
        if name not in self.definitions:
            self.definitions[name] = []
        self.definitions[name].append(Location(self.uri, line, col))

    def add_symbol_info(self, info: SymbolInfo) -> None:
        self.symbol_infos.append(info)

    def get_symbols_visible_at(self, line: int, col: int) -> List[SymbolInfo]:
        """Return symbols defined before the given position."""
        result = []
        for info in self.symbol_infos:
            if info.line < line or (info.line == line and info.col < col):
                result.append(info)
        return result

    def get_symbol_info(self, name: str) -> Optional[SymbolInfo]:
        """Search symbol info by name (returns first match)."""
        for info in self.symbol_infos:
            if info.name == name:
                return info
        return None

    def get_class_info(self, class_name: str) -> Optional[SymbolInfo]:
        """Return SymbolInfo for a class definition."""
        for info in self.symbol_infos:
            if info.kind == "class" and info.name == class_name:
                return info
        return None

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


def _to_lsp_line(n):
    """Lexer の 1-ベース行番号を LSP 0-ベースに変換する。"""
    return max(0, (n or 1) - 1)


def _to_lsp_col(n):
    """Lexer の 1-ベース列番号を LSP 0-ベースに変換する。"""
    return max(0, (n or 1) - 1)


def build_symbol_table(uri: str, node) -> SymbolTable:
    """Build symbol table from AST."""
    table = SymbolTable(uri)
    _walk(node, table)
    return table


def _walk(node, table: SymbolTable):
    """Walk AST and collect definitions."""
    from vimmo.ast_nodes import (
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
        table.add_definition(node.name, _to_lsp_line(node.line), _to_lsp_col(node.col))
        table.add_symbol_info(
            SymbolInfo(
                name=node.name,
                kind="variable",
                type_ann=node.type_ann,
                line=_to_lsp_line(node.line),
                col=_to_lsp_col(node.col),
            )
        )

    elif isinstance(node, FnDecl):
        table.add_definition(node.name, _to_lsp_line(node.line), _to_lsp_col(node.col))
        table.add_symbol_info(
            SymbolInfo(
                name=node.name,
                kind="function",
                params=list(node.params),
                line=_to_lsp_line(node.line),
                col=_to_lsp_col(node.col),
            )
        )
        for param in node.params:
            param_name = param[0] if isinstance(param, (list, tuple)) else str(param)
            param_type = (
                param[1]
                if isinstance(param, (list, tuple)) and len(param) > 1
                else None
            )
            table.add_symbol_info(
                SymbolInfo(
                    name=param_name,
                    kind="parameter",
                    type_ann=param_type,
                    line=_to_lsp_line(node.line),
                    col=_to_lsp_col(node.col),
                )
            )
        _walk(node.body, table)

    elif isinstance(node, ClassDecl):
        table.add_definition(node.name, _to_lsp_line(node.line), _to_lsp_col(node.col))
        table.add_symbol_info(
            SymbolInfo(
                name=node.name,
                kind="class",
                class_fields=[f.name for f in node.fields],
                class_methods=[m.name for m in node.methods],
                line=_to_lsp_line(node.line),
                col=_to_lsp_col(node.col),
            )
        )
        for field in node.fields:
            _walk(field, table)
        for method in node.methods:
            _walk(method, table)

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
        table.add_symbol_info(
            SymbolInfo(
                name=node.var,
                kind="variable",
                line=0,
                col=0,
            )
        )
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
