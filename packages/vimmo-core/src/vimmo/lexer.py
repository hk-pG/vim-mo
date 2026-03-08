"""
VimMo Lexer - Tokenizer for VimMo language
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    NULL = auto()

    # Identifiers & Keywords
    IDENT = auto()
    LET = auto()
    CONST = auto()
    FN = auto()
    ASYNC = auto()
    AWAIT = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    IN = auto()
    WHILE = auto()
    BREAK = auto()
    CONTINUE = auto()
    IMPORT = auto()
    FROM = auto()
    CLASS = auto()
    SELF = auto()
    ECHO = auto()
    NEW = auto()

    # Types
    TYPE_NUMBER = auto()
    TYPE_STRING = auto()
    TYPE_BOOL = auto()
    TYPE_LIST = auto()
    TYPE_DICT = auto()
    TYPE_ANY = auto()
    TYPE_VOID = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    ARROW = auto()  # =>
    PIPE = auto()  # |>
    PLUS_EQ = auto()  # +=
    MINUS_EQ = auto()  # -=
    DOT = auto()
    DOTDOT = auto()  # ..  (string concat)

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    NEWLINE = auto()

    # Special
    EOF = auto()
    COMMENT = auto()


KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "class": TokenType.CLASS,
    "self": TokenType.SELF,
    "echo": TokenType.ECHO,
    "new": TokenType.NEW,
    "true": TokenType.BOOL,
    "false": TokenType.BOOL,
    "null": TokenType.NULL,
    "number": TokenType.TYPE_NUMBER,
    "string": TokenType.TYPE_STRING,
    "bool": TokenType.TYPE_BOOL,
    "list": TokenType.TYPE_LIST,
    "dict": TokenType.TYPE_DICT,
    "any": TokenType.TYPE_ANY,
    "void": TokenType.TYPE_VOID,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


class LexerError(Exception):
    def __init__(self, msg: str, line: int, col: int):
        super().__init__(f"LexerError at {line}:{col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def error(self, msg: str) -> LexerError:
        return LexerError(msg, self.line, self.col)

    def peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in " \t\r":
            self.advance()

    def read_string(self) -> Token:
        start_line, start_col = self.line, self.col
        quote = self.advance()  # " or '
        buf = []
        while self.pos < len(self.source):
            ch = self.peek()
            if ch == "\\":
                self.advance()
                esc = self.advance()
                buf.append(
                    {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'"}.get(
                        esc, "\\" + esc
                    )
                )
            elif ch == quote:
                self.advance()
                break
            elif ch == "\n":
                raise self.error("Unterminated string literal")
            else:
                buf.append(self.advance())
        return Token(TokenType.STRING, "".join(buf), start_line, start_col)

    def read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        buf = []
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            buf.append(self.advance())
        if self.pos < len(self.source) and self.source[self.pos] == ".":
            buf.append(self.advance())
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                buf.append(self.advance())
        return Token(TokenType.NUMBER, "".join(buf), start_line, start_col)

    def read_ident(self) -> Token:
        start_line, start_col = self.line, self.col
        buf = []
        while self.pos < len(self.source) and (
            self.source[self.pos].isalnum() or self.source[self.pos] == "_"
        ):
            buf.append(self.advance())
        word = "".join(buf)
        tok_type = KEYWORDS.get(word, TokenType.IDENT)
        return Token(tok_type, word, start_line, start_col)

    def read_comment(self) -> Optional[Token]:
        # // line comment
        if self.peek() == "/" and self.peek(1) == "/":
            start_line, start_col = self.line, self.col
            self.advance()
            self.advance()
            buf = []
            while self.pos < len(self.source) and self.source[self.pos] != "\n":
                buf.append(self.advance())
            return Token(TokenType.COMMENT, "".join(buf).strip(), start_line, start_col)
        return None

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.peek()
            start_line, start_col = self.line, self.col

            # Comment
            if ch == "/" and self.peek(1) == "/":
                self.read_comment()
                # skip comments (don't emit)
                continue

            # Newline
            if ch == "\n":
                self.advance()
                self.tokens.append(
                    Token(TokenType.NEWLINE, "\\n", start_line, start_col)
                )
                continue

            # String
            if ch in ('"', "'"):
                self.tokens.append(self.read_string())
                continue

            # Number
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Identifier / keyword
            if ch.isalpha() or ch == "_":
                self.tokens.append(self.read_ident())
                continue

            # Operators & delimiters
            self.advance()
            if ch == "+":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.PLUS_EQ, "+=", start_line, start_col)
                    )
                else:
                    self.tokens.append(
                        Token(TokenType.PLUS, "+", start_line, start_col)
                    )
            elif ch == "-":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.MINUS_EQ, "-=", start_line, start_col)
                    )
                elif self.match(">"):
                    self.tokens.append(
                        Token(TokenType.ARROW, "->", start_line, start_col)
                    )
                else:
                    self.tokens.append(
                        Token(TokenType.MINUS, "-", start_line, start_col)
                    )
            elif ch == "*":
                self.tokens.append(Token(TokenType.STAR, "*", start_line, start_col))
            elif ch == "/":
                self.tokens.append(Token(TokenType.SLASH, "/", start_line, start_col))
            elif ch == "%":
                self.tokens.append(Token(TokenType.PERCENT, "%", start_line, start_col))
            elif ch == "=":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.EQEQ, "==", start_line, start_col)
                    )
                elif self.match(">"):
                    self.tokens.append(
                        Token(TokenType.ARROW, "=>", start_line, start_col)
                    )
                else:
                    self.tokens.append(Token(TokenType.EQ, "=", start_line, start_col))
            elif ch == "!":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.NEQ, "!=", start_line, start_col)
                    )
                else:
                    self.tokens.append(Token(TokenType.NOT, "!", start_line, start_col))
            elif ch == "<":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.LTE, "<=", start_line, start_col)
                    )
                else:
                    self.tokens.append(Token(TokenType.LT, "<", start_line, start_col))
            elif ch == ">":
                if self.match("="):
                    self.tokens.append(
                        Token(TokenType.GTE, ">=", start_line, start_col)
                    )
                else:
                    self.tokens.append(Token(TokenType.GT, ">", start_line, start_col))
            elif ch == "&":
                if self.match("&"):
                    self.tokens.append(
                        Token(TokenType.AND, "&&", start_line, start_col)
                    )
            elif ch == "|":
                if self.match("|"):
                    self.tokens.append(Token(TokenType.OR, "||", start_line, start_col))
                elif self.match(">"):
                    self.tokens.append(
                        Token(TokenType.PIPE, "|>", start_line, start_col)
                    )
                else:
                    self.tokens.append(
                        Token(TokenType.PIPE, "|", start_line, start_col)
                    )
            elif ch == ".":
                if self.match("."):
                    self.tokens.append(
                        Token(TokenType.DOTDOT, "..", start_line, start_col)
                    )
                else:
                    self.tokens.append(Token(TokenType.DOT, ".", start_line, start_col))
            elif ch == "(":
                self.tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
            elif ch == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
            elif ch == "{":
                self.tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col))
            elif ch == "}":
                self.tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col))
            elif ch == "[":
                self.tokens.append(
                    Token(TokenType.LBRACKET, "[", start_line, start_col)
                )
            elif ch == "]":
                self.tokens.append(
                    Token(TokenType.RBRACKET, "]", start_line, start_col)
                )
            elif ch == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", start_line, start_col))
            elif ch == ":":
                self.tokens.append(Token(TokenType.COLON, ":", start_line, start_col))
            elif ch == ";":
                self.tokens.append(
                    Token(TokenType.SEMICOLON, ";", start_line, start_col)
                )
            else:
                raise self.error(f"Unexpected character: {ch!r}")

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return self.tokens
