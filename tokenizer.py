# tokenizer and parser for simple arithmetic expressions
import abc
from dataclasses import dataclass, field
import typing

Tokenizer = typing.Callable[[str, "Lexer"], typing.Optional["Token"]]


class TokenizerException(Exception):
    pass


class InvalidTokenException(TokenizerException):
    pass


@dataclass
class Token:
    index: int
    type: str
    value: typing.Optional[str] = None

    __match_args__ = ("type", "value")

    def __str__(self):
        return f"{self.type}({self.value})"


class FragmentTokenizer(abc.ABC):
    def __call__(self, str, lexer) -> typing.Optional[Token]:
        raise NotImplementedError


@dataclass
class Lexer:
    tokenizers: typing.List[FragmentTokenizer]
    text: str
    index: int = 0
    skip_tokens: typing.List[str] = field(default_factory = list)

    def __iter__(self):
        return self

    def __next__(self) -> Token:
        while self.index < len(self.text):
            for tokenizer in self.tokenizers:
                token = tokenizer(self.text, self)
                if token is None:
                    continue
                if token.type in self.skip_tokens:
                    continue
                return token
            self.index += 1
        raise StopIteration

    def peek(self, n: int = 1) -> str:
        if self.index + n > len(self.text):
            return "\0"
        return self.text[self.index:self.index + n]

    def consume(self, n: int = 1) -> str:
        if self.index + n > len(self.text):
            return "\0"
        self.index += n
        return self.text[self.index - n:self.index]

    def skip(self, n: int = 1) -> None:
        if self.index + n > len(self.text):
            return
        self.index += n

    # __new__ takes a list of tokenizers, tokens to skip, and the string to tokenize
    def __new__(cls, tokenizers, text, *skip_tokens):
        self = super().__new__(cls)
        getattr(self, "__init__")(tokenizers, text, 0, skip_tokens)
        return list(self)


# predicates for reuse
def is_digit(char: str) -> bool:
    return char.isdigit()


def is_alpha(char: str) -> bool:
    return char.isalpha()


def is_alnum(char: str) -> bool:
    return char.isalnum()


def is_whitespace(char: str) -> bool:
    return char.isspace()


def is_operator(char: str) -> bool:
    return char in "+-*/"


def is_paren(char: str) -> bool:
    return char in "()"


def is_quote(char: str) -> bool:
    return char in '"\''


def is_escape(char: str) -> bool:
    return char == '\\'


def is_eof(char: str) -> bool:
    return char == '\0'


class WhitespacesTokenizer(FragmentTokenizer):
    def __call__(self, text, lexer) -> typing.Optional[Token]:
        if not is_whitespace(lexer.peek()):
            return None
        while is_whitespace(lexer.peek()):
            lexer.skip()
        return Token(lexer.index, "whitespace")


class NumberTokenizer(FragmentTokenizer):
    def __call__(self, text, lexer) -> typing.Optional[Token]:
        if not is_digit(lexer.peek()):
            return None
        value = ""
        while is_digit(lexer.peek()):
            value += lexer.consume()
            if lexer.peek() == ".":
                value += lexer.consume()
                while is_digit(lexer.peek()):
                    value += lexer.consume()
                break
        return Token(lexer.index, "number", value)


class OperatorTokenizer(FragmentTokenizer):
    def __call__(self, text, lexer) -> typing.Optional[Token]:
        if not is_operator(lexer.peek()):
            return None
        return Token(lexer.index, "operator", lexer.consume())


class ParenTokenizer(FragmentTokenizer):
    def __call__(self, text, lexer) -> typing.Optional[Token]:
        if not is_paren(lexer.peek()):
            return None
        return Token(lexer.index, "paren", lexer.consume())
