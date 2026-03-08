"""
VimMo Parser — produces AST from token stream
"""

from typing import List, Optional, Tuple

try:
    from vimmo.lexer import Token, TokenType
    from vimmo.ast_nodes import *  # noqa: F403
except ImportError:
    from lexer import Token, TokenType  # type: ignore[no-redef]
    from ast_nodes import *  # type: ignore[no-redef]  # noqa: F403


class ParseError(Exception):
    def __init__(self, msg: str, token: Token):
        super().__init__(
            f"ParseError at {token.line}:{token.col}: {msg} (got {token.type.name} {token.value!r})"
        )
        self.token = token


class Parser:
    def __init__(self, tokens: List[Token]):
        # strip newlines between certain contexts but keep them for statement separation
        self.tokens = [t for t in tokens if t.type != TokenType.COMMENT]
        self.pos = 0

    # ── Helpers ───────────────────────────────────────────────────────────────

    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, *types: TokenType) -> bool:
        return self.peek().type in types

    def match(self, *types: TokenType) -> Optional[Token]:
        if self.check(*types):
            return self.advance()
        return None

    def expect(self, type_: TokenType, msg: str = "") -> Token:
        if self.check(type_):
            return self.advance()
        raise ParseError(msg or f"Expected {type_.name}", self.peek())

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE):
            self.advance()

    def skip_newlines_and_semi(self):
        while self.check(TokenType.NEWLINE, TokenType.SEMICOLON):
            self.advance()

    # ── Program ───────────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            stmts.append(self.parse_stmt())
            self.skip_newlines_and_semi()
        return Program(stmts)

    # ── Statements ────────────────────────────────────────────────────────────

    def parse_stmt(self) -> Node:
        self.skip_newlines()
        tok = self.peek()

        if tok.type == TokenType.IMPORT:
            return self.parse_import()
        if tok.type == TokenType.CLASS:
            return self.parse_class()
        if tok.type in (TokenType.LET, TokenType.CONST):
            return self.parse_var_decl()
        if tok.type == TokenType.ASYNC:
            return self.parse_fn(is_async=True)
        if tok.type == TokenType.FN:
            return self.parse_fn()
        if tok.type == TokenType.RETURN:
            return self.parse_return()
        if tok.type == TokenType.IF:
            return self.parse_if()
        if tok.type == TokenType.FOR:
            return self.parse_for()
        if tok.type == TokenType.WHILE:
            return self.parse_while()
        if tok.type == TokenType.BREAK:
            self.advance()
            return Break()
        if tok.type == TokenType.CONTINUE:
            self.advance()
            return Continue()
        if tok.type == TokenType.ECHO:
            return self.parse_echo()

        return self.parse_expr_stmt()

    def parse_import(self) -> Import:
        self.expect(TokenType.IMPORT)
        self.expect(TokenType.LBRACE)
        names = []
        while not self.check(TokenType.RBRACE, TokenType.EOF):
            names.append(self.expect(TokenType.IDENT).value)
            self.match(TokenType.COMMA)
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.FROM)
        source = self.expect(TokenType.STRING).value
        return Import(names, source)

    def parse_class(self) -> ClassDecl:
        tok = self.peek()
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        fields = []
        methods = []
        while not self.check(TokenType.RBRACE, TokenType.EOF):
            if self.check(TokenType.LET, TokenType.CONST):
                fields.append(self.parse_var_decl())
            elif self.check(TokenType.ASYNC):
                methods.append(self.parse_fn(is_async=True))
            elif self.check(TokenType.FN):
                methods.append(self.parse_fn())
            else:
                raise ParseError("Expected field or method in class", self.peek())
            self.skip_newlines_and_semi()
        self.expect(TokenType.RBRACE)
        cls = ClassDecl(name, fields, methods)
        cls.line = tok.line
        cls.col = tok.col
        return cls

    def parse_var_decl(self) -> VarDecl:
        tok = self.peek()
        kind = self.advance().value  # let / const
        name_tok = self.expect(TokenType.IDENT)
        name = name_tok.value
        type_ann = None
        if self.match(TokenType.COLON):
            type_ann = self.parse_type()
        value = None
        if self.match(TokenType.EQ):
            value = self.parse_expr()
        decl = VarDecl(kind, name, type_ann, value)
        decl.line = tok.line
        decl.col = tok.col
        return decl

    TYPE_TOKENS = {
        TokenType.TYPE_NUMBER,
        TokenType.TYPE_STRING,
        TokenType.TYPE_BOOL,
        TokenType.TYPE_LIST,
        TokenType.TYPE_DICT,
        TokenType.TYPE_ANY,
        TokenType.TYPE_VOID,
        TokenType.IDENT,
    }

    def parse_type(self) -> str:
        tok = self.advance()
        return tok.value

    _IDENT_LIKE = {
        TokenType.IDENT,
        TokenType.TYPE_NUMBER,
        TokenType.TYPE_STRING,
        TokenType.TYPE_BOOL,
        TokenType.TYPE_LIST,
        TokenType.TYPE_DICT,
        TokenType.TYPE_ANY,
        TokenType.TYPE_VOID,
    }

    def expect_ident_like(self, msg: str = "Expected identifier") -> Token:
        if self.peek().type in self._IDENT_LIKE:
            return self.advance()
        raise ParseError(msg, self.peek())

    def parse_fn(self, is_async: bool = False) -> FnDecl:
        tok = self.peek()
        if is_async:
            self.expect(TokenType.ASYNC)
        self.expect(TokenType.FN)
        name = self.expect_ident_like().value
        params = self.parse_params()
        ret = None
        if self.match(TokenType.COLON):
            ret = self.parse_type()
        body = self.parse_block()
        fn = FnDecl(name, params, ret, body, is_async)
        fn.line = tok.line
        fn.col = tok.col
        return fn

    def parse_params(self) -> List[Tuple[str, Optional[str]]]:
        self.expect(TokenType.LPAREN)
        params = []
        while not self.check(TokenType.RPAREN, TokenType.EOF):
            pname = self.expect_ident_like().value
            ptype = None
            if self.match(TokenType.COLON):
                ptype = self.parse_type()
            params.append((pname, ptype))
            self.match(TokenType.COMMA)
        self.expect(TokenType.RPAREN)
        return params

    def parse_return(self) -> Return:
        self.expect(TokenType.RETURN)
        if self.check(
            TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF
        ):
            return Return(None)
        return Return(self.parse_expr())

    def parse_if(self) -> If:
        self.expect(TokenType.IF)
        cond = self.parse_expr()
        then = self.parse_block()
        elseifs = []
        else_ = None
        while self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                self.expect(TokenType.IF)
                ei_cond = self.parse_expr()
                ei_body = self.parse_block()
                elseifs.append((ei_cond, ei_body))
            else:
                else_ = self.parse_block()
                break
        return If(cond, then, elseifs, else_)

    def parse_for(self) -> For:
        self.expect(TokenType.FOR)
        var = self.expect(TokenType.IDENT).value
        self.expect(TokenType.IN)
        iterable = self.parse_expr()
        body = self.parse_block()
        return For(var, iterable, body)

    def parse_while(self) -> While:
        self.expect(TokenType.WHILE)
        cond = self.parse_expr()
        body = self.parse_block()
        return While(cond, body)

    def parse_echo(self) -> Echo:
        self.expect(TokenType.ECHO)
        val = self.parse_expr()
        return Echo(val)

    def parse_expr_stmt(self) -> ExprStmt:
        expr = self.parse_expr()
        return ExprStmt(expr)

    def parse_block(self) -> Block:
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        stmts = []
        while not self.check(TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_stmt())
            self.skip_newlines_and_semi()
        self.expect(TokenType.RBRACE)
        return Block(stmts)

    # ── Expressions ───────────────────────────────────────────────────────────

    def parse_expr(self) -> Node:
        return self.parse_pipeline()

    def parse_pipeline(self) -> Node:
        left = self.parse_assign()
        while True:
            self.skip_newlines()
            if self.match(TokenType.PIPE):
                self.skip_newlines()  # allow newline after pipe
                right = self.parse_assign()
                left = Pipeline(left, right)
            else:
                break
        return left

    def parse_assign(self) -> Node:
        expr = self.parse_or()
        if self.check(TokenType.EQ):
            if isinstance(expr, (Ident, Attr, Index)):
                self.advance()
                val = self.parse_expr()
                return Assign(expr, val)
        if self.check(TokenType.PLUS_EQ, TokenType.MINUS_EQ):
            op = self.advance().value
            val = self.parse_expr()
            return AugAssign(op, expr, val)
        return expr

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.check(TokenType.OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinOp(op, left, right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_equality()
        while self.check(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinOp(op, left, right)
        return left

    def parse_equality(self) -> Node:
        left = self.parse_comparison()
        while self.check(TokenType.EQEQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinOp(op, left, right)
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        while self.check(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value
            right = self.parse_addition()
            left = BinOp(op, left, right)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_multiplication()
        while self.check(TokenType.PLUS, TokenType.MINUS, TokenType.DOTDOT):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinOp(op, left, right)
        return left

    def parse_multiplication(self) -> Node:
        left = self.parse_unary()
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self) -> Node:
        if self.check(TokenType.NOT):
            op = self.advance().value
            return UnaryOp(op, self.parse_unary())
        if self.check(TokenType.MINUS):
            op = self.advance().value
            return UnaryOp(op, self.parse_unary())
        return self.parse_await()

    def parse_await(self) -> Node:
        if self.match(TokenType.AWAIT):
            return Await(self.parse_call())
        return self.parse_call()

    def parse_call(self) -> Node:
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.LPAREN):
                tok = self.peek()
                args = self.parse_args()
                call = Call(expr, args)
                call.line = tok.line
                call.col = tok.col
                expr = call
            elif self.check(TokenType.DOT):
                self.advance()
                attr = self.expect_ident_like().value
                expr = Attr(expr, attr)
            elif self.check(TokenType.LBRACKET):
                self.advance()
                idx = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = Index(expr, idx)
            else:
                break
        return expr

    def parse_args(self) -> List[Node]:
        self.expect(TokenType.LPAREN)
        args = []
        self.skip_newlines()
        while not self.check(TokenType.RPAREN, TokenType.EOF):
            args.append(self.parse_expr())
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RPAREN)
        return args

    def parse_primary(self) -> Node:
        tok = self.peek()

        # Lambda: (params) => expr_or_block
        if tok.type == TokenType.LPAREN and self._is_lambda():
            return self.parse_lambda()

        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumberLit(tok.value)

        if tok.type == TokenType.STRING:
            self.advance()
            return StringLit(tok.value)

        if tok.type == TokenType.BOOL:
            self.advance()
            return BoolLit(tok.value == "true")

        if tok.type == TokenType.NULL:
            self.advance()
            return NullLit()

        if tok.type == TokenType.SELF:
            self.advance()
            return Ident("self", tok.line, tok.col)

        if tok.type == TokenType.IDENT:
            self.advance()
            return Ident(tok.value, tok.line, tok.col)

        if tok.type == TokenType.NEW:
            self.advance()
            cname = self.expect(TokenType.IDENT).value
            args = self.parse_args()
            return New(cname, args)

        if tok.type == TokenType.LBRACKET:
            return self.parse_list_lit()

        if tok.type == TokenType.LBRACE:
            return self.parse_dict_lit()

        if tok.type == TokenType.LPAREN:
            self.advance()
            self.skip_newlines()
            expr = self.parse_expr()
            self.skip_newlines()
            self.expect(TokenType.RPAREN)
            return expr

        raise ParseError(f"Unexpected token in expression", tok)

    def _is_lambda(self) -> bool:
        """Lookahead to decide if '(' starts a lambda param list."""
        saved = self.pos
        try:
            self.advance()  # (
            depth = 1
            # Allow: () =>  OR  (ident, ...) =>  OR  (ident: type, ...) =>
            while depth > 0 and not self.check(TokenType.EOF):
                t = self.peek()
                if t.type == TokenType.LPAREN:
                    depth += 1
                    self.advance()
                elif t.type == TokenType.RPAREN:
                    depth -= 1
                    self.advance()
                else:
                    self.advance()
            # after ')' we need '=>'
            return self.check(TokenType.ARROW)
        finally:
            self.pos = saved

    def parse_lambda(self) -> Lambda:
        self.expect(TokenType.LPAREN)
        params = []
        while not self.check(TokenType.RPAREN, TokenType.EOF):
            pname = self.expect(TokenType.IDENT).value
            if self.match(TokenType.COLON):
                self.parse_type()  # consume type but ignore for now
            params.append(pname)
            self.match(TokenType.COMMA)
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ARROW)
        if self.check(TokenType.LBRACE):
            body = self.parse_block()
        else:
            body = self.parse_expr()
        return Lambda(params, body)

    def parse_list_lit(self) -> ListLit:
        self.expect(TokenType.LBRACKET)
        elements = []
        self.skip_newlines()
        while not self.check(TokenType.RBRACKET, TokenType.EOF):
            elements.append(self.parse_expr())
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACKET)
        return ListLit(elements)

    def parse_dict_lit(self) -> DictLit:
        self.expect(TokenType.LBRACE)
        pairs = []
        self.skip_newlines()
        while not self.check(TokenType.RBRACE, TokenType.EOF):
            # key can be ident or string
            if self.check(TokenType.IDENT):
                key = StringLit(self.advance().value)
            else:
                key = self.parse_primary()
            self.expect(TokenType.COLON)
            val = self.parse_expr()
            pairs.append((key, val))
            self.skip_newlines()
            self.match(TokenType.COMMA)
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return DictLit(pairs)
