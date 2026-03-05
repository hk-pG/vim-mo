"""
VimMo AST Node definitions
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Union


# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass
class Node:
    pass


# ── Expressions ───────────────────────────────────────────────────────────────

@dataclass
class NumberLit(Node):
    value: str

@dataclass
class StringLit(Node):
    value: str

@dataclass
class BoolLit(Node):
    value: bool

@dataclass
class NullLit(Node):
    pass

@dataclass
class Ident(Node):
    name: str

@dataclass
class ListLit(Node):
    elements: List[Node]

@dataclass
class DictLit(Node):
    pairs: List[tuple]  # (key_expr, value_expr)

@dataclass
class BinOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class Assign(Node):
    target: Node
    value: Node

@dataclass
class AugAssign(Node):
    op: str        # '+=' or '-='
    target: Node
    value: Node

@dataclass
class Index(Node):
    obj: Node
    index: Node

@dataclass
class Attr(Node):
    obj: Node
    attr: str

@dataclass
class Call(Node):
    callee: Node
    args: List[Node]

@dataclass
class Lambda(Node):
    params: List[str]
    body: Node  # expr or Block

@dataclass
class Await(Node):
    expr: Node

@dataclass
class Pipeline(Node):
    left: Node
    right: Node   # must be callable expr

@dataclass
class New(Node):
    class_name: str
    args: List[Node]


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class VarDecl(Node):
    kind: str          # 'let' or 'const'
    name: str
    type_ann: Optional[str]
    value: Optional[Node]

@dataclass
class FnDecl(Node):
    name: str
    params: List[tuple]   # (name, type_ann_or_None)
    return_type: Optional[str]
    body: 'Block'
    is_async: bool = False

@dataclass
class Return(Node):
    value: Optional[Node]

@dataclass
class If(Node):
    condition: Node
    then: 'Block'
    elseifs: List[tuple]   # (condition, Block)
    else_: Optional['Block']

@dataclass
class For(Node):
    var: str
    iterable: Node
    body: 'Block'

@dataclass
class While(Node):
    condition: Node
    body: 'Block'

@dataclass
class Break(Node):
    pass

@dataclass
class Continue(Node):
    pass

@dataclass
class Echo(Node):
    value: Node

@dataclass
class ExprStmt(Node):
    expr: Node

@dataclass
class Block(Node):
    stmts: List[Node]

@dataclass
class Import(Node):
    names: List[str]
    source: str

@dataclass
class ClassDecl(Node):
    name: str
    fields: List[VarDecl]
    methods: List[FnDecl]

@dataclass
class Program(Node):
    body: List[Node]
