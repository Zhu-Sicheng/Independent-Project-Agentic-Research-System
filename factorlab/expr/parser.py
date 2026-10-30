"""A small, safe expression language for factor formulas.

Grammar (lowest to highest precedence)::

    or        := and ('|' and)*
    and       := cmp ('&' cmp)*
    cmp       := add (('<'|'<='|'>'|'>='|'=='|'!=') add)?
    add       := mul (('+'|'-') mul)*
    mul       := unary (('*'|'/') unary)*
    unary     := ('-'|'+'|'!') unary | pow
    pow       := atom ('^' unary)?
    atom      := number | name | name '(' args ')' | '(' or ')'

No python is executed for expressions: they are parsed into a small AST and
interpreted operator by operator.  That keeps LLM output auditable and makes
window substitution (the grid search) a pure tree rewrite.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, Sequence, Tuple, Union


class ExpressionError(ValueError):
    def __init__(self, message: str, position: int | None = None):
        self.position = position
        super().__init__(f"{message} (at char {position})" if position is not None else message)


# --------------------------------------------------------------------------- #
# AST
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Const:
    name: str


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Call:
    name: str
    args: Tuple["Expr", ...]


@dataclass(frozen=True)
class Unary:
    op: str
    x: "Expr"


@dataclass(frozen=True)
class Bin:
    op: str
    left: "Expr"
    right: "Expr"


Expr = Union[Num, Const, Var, Call, Unary, Bin]

CONSTANTS = {
    "nan": float("nan"),
    "NaN": float("nan"),
    "inf": float("inf"),
    "true": True,
    "True": True,
    "false": False,
    "False": False,
}

_TOKEN_RE = re.compile(
    r"""
      (?P<space>\s+)
    | (?P<number>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)
    | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    | (?P<op><=|>=|==|!=|&&|\|\||[-+*/^<>!(),&|])
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    pos: int


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise ExpressionError(f"unexpected character {text[pos]!r}", pos)
        kind = m.lastgroup or ""
        if kind != "space":
            tokens.append(Token(kind, m.group(), pos))
        pos = m.end()
    return tokens


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.tokens = tokenize(text)
        self.i = 0

    # -- token helpers ---------------------------------------------------- #
    def peek(self) -> Token | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def at_end(self) -> bool:
        return self.i >= len(self.tokens)

    def take(self) -> Token:
        tok = self.peek()
        if tok is None:
            raise ExpressionError("unexpected end of expression", len(self.text))
        self.i += 1
        return tok

    def expect(self, text: str) -> Token:
        tok = self.peek()
        if tok is None or tok.text != text:
            got = tok.text if tok else "end of expression"
            raise ExpressionError(f"expected {text!r} but found {got!r}", tok.pos if tok else None)
        return self.take()

    # -- grammar ---------------------------------------------------------- #
    def parse(self) -> Expr:
        if not self.tokens:
            raise ExpressionError("empty expression", 0)
        node = self.parse_or()
        if not self.at_end():
            tok = self.peek()
            raise ExpressionError(f"unexpected token {tok.text!r}", tok.pos)
        return node

    def parse_or(self) -> Expr:
        node = self.parse_and()
        while (tok := self.peek()) and tok.text in ("|", "||"):
            self.take()
            node = Bin("|", node, self.parse_and())
        return node

    def parse_and(self) -> Expr:
        node = self.parse_cmp()
        while (tok := self.peek()) and tok.text in ("&", "&&"):
            self.take()
            node = Bin("&", node, self.parse_cmp())
        return node

    def parse_cmp(self) -> Expr:
        node = self.parse_add()
        tok = self.peek()
        if tok and tok.text in ("<", "<=", ">", ">=", "==", "!="):
            self.take()
            node = Bin(tok.text, node, self.parse_add())
            nxt = self.peek()
            if nxt and nxt.text in ("<", "<=", ">", ">=", "==", "!="):
                raise ExpressionError("chained comparisons are not supported", nxt.pos)
        return node

    def parse_add(self) -> Expr:
        node = self.parse_mul()
        while (tok := self.peek()) and tok.text in ("+", "-"):
            self.take()
            node = Bin(tok.text, node, self.parse_mul())
        return node

    def parse_mul(self) -> Expr:
        node = self.parse_unary()
        while (tok := self.peek()) and tok.text in ("*", "/"):
            self.take()
            node = Bin(tok.text, node, self.parse_unary())
        return node

    def parse_unary(self) -> Expr:
        tok = self.peek()
        if tok and tok.text in ("-", "+", "!"):
            self.take()
            operand = self.parse_unary()
            if tok.text == "+":
                return operand
            return Unary(tok.text, operand)
        return self.parse_pow()

    def parse_pow(self) -> Expr:
        node = self.parse_atom()
        if (tok := self.peek()) and tok.text == "^":
            self.take()
            node = Bin("^", node, self.parse_unary())
        return node

    def parse_atom(self) -> Expr:
        tok = self.take()
        if tok.kind == "number":
            return Num(float(tok.text))
        if tok.kind == "name":
            nxt = self.peek()
            if nxt and nxt.text == "(":
                self.take()
                args: list[Expr] = []
                if (nxt2 := self.peek()) and nxt2.text == ")":
                    self.take()
                    return Call(tok.text, tuple(args))
                while True:
                    args.append(self.parse_or())
                    sep = self.take()
                    if sep.text == ")":
                        break
                    if sep.text != ",":
                        raise ExpressionError(f"expected ',' or ')' but found {sep.text!r}", sep.pos)
                return Call(tok.text, tuple(args))
            if tok.text in CONSTANTS:
                return Const(tok.text)
            return Var(tok.text)
        if tok.text == "(":
            node = self.parse_or()
            self.expect(")")
            return node
        raise ExpressionError(f"unexpected token {tok.text!r}", tok.pos)


def parse(text: str) -> Expr:
    return Parser(text).parse()


# --------------------------------------------------------------------------- #
# utilities
# --------------------------------------------------------------------------- #
def walk(node: Expr) -> Iterator[Expr]:
    yield node
    if isinstance(node, Call):
        for a in node.args:
            yield from walk(a)
    elif isinstance(node, Unary):
        yield from walk(node.x)
    elif isinstance(node, Bin):
        yield from walk(node.left)
        yield from walk(node.right)


def to_string(node: Expr) -> str:
    if isinstance(node, Num):
        v = node.value
        return str(int(v)) if float(v).is_integer() else repr(v)
    if isinstance(node, Const):
        return node.name
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Call):
        return f"{node.name}({', '.join(to_string(a) for a in node.args)})"
    if isinstance(node, Unary):
        inner = to_string(node.x)
        return f"{node.op}({inner})" if node.op == "!" else f"{node.op}{inner}"
    if isinstance(node, Bin):
        return f"({to_string(node.left)} {node.op} {to_string(node.right)})"
    raise TypeError(node)


def collect_vars(node: Expr) -> list[str]:
    return sorted({n.name for n in walk(node) if isinstance(n, Var)})


def collect_windows(node: Expr) -> list[int]:
    """Window values in deterministic pre-order (matches :func:`substitute_windows`)."""
    from .ops import REGISTRY

    out: list[int] = []
    for n in walk(node):
        if isinstance(n, Call):
            op = REGISTRY.get(n.name)
            if op is None:
                continue
            for idx in op.window_positions():
                if idx < len(n.args) and isinstance(n.args[idx], Num):
                    out.append(int(n.args[idx].value))
    return out


def substitute_windows(node: Expr, values: Sequence[int]) -> Expr:
    """Return a copy of ``node`` with window literals replaced in order."""
    from .ops import REGISTRY

    counter = {"i": 0}

    def rec(n: Expr) -> Expr:
        if isinstance(n, Call):
            op = REGISTRY.get(n.name)
            args = list(n.args)
            if op is not None:
                for idx in op.window_positions():
                    if idx < len(args) and isinstance(args[idx], Num):
                        if counter["i"] >= len(values):
                            raise ExpressionError("not enough replacement windows")
                        args[idx] = Num(float(values[counter["i"]]))
                        counter["i"] += 1
            return Call(n.name, tuple(rec(a) if not isinstance(a, Num) else a for a in args))
        if isinstance(n, Unary):
            return Unary(n.op, rec(n.x))
        if isinstance(n, Bin):
            return Bin(n.op, rec(n.left), rec(n.right))
        return n

    out = rec(node)
    if counter["i"] != len(values):
        raise ExpressionError("replacement window count does not match the expression")
    return out
