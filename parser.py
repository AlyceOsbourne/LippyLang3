import abc

from tokenizer import Token

UNARY_OP_TOKENS = {"+", "-"}
BINARY_OP_TOKENS = {"+", "-", "*", "/"}


class ASTNode(abc.ABC):
    @abc.abstractmethod
    def __iter__(self):
        ...

    # str provides a way of printing the AST as a tree
    @abc.abstractmethod
    def __str__(self):
        ...


class NumberNode(ASTNode):
    def __init__(
            self,
            token: Token,
    ):
        self.token = token

    def __iter__(self):
        yield self.token

    def __str__(self):
        return f"NumberNode({self.token.value})"


class BinaryOperationNode(ASTNode):
    def __init__(
            self,
            left,
            operator,
            right
    ):
        self.left = left
        self.operator = operator
        self.right = right

    def __iter__(self):
        if isinstance(self.left, ASTNode):
            yield from self.left
        else:
            yield self.left
        yield self.operator
        if isinstance(self.right, ASTNode):
            yield from self.right
        else:
            yield self.right

    def __str__(self):
        return f"BinaryOperationNode({self.left}, {self.operator}, {self.right})"


class UnaryOperationNode(ASTNode):
    def __init__(
            self,
            operator,
            operand
    ):
        self.operator = operator
        self.operand = operand

    def __iter__(self):
        yield self.operator
        if isinstance(self.operand, ASTNode):
            yield from self.operand
        else:
            yield self.operand

    def __str__(self):
        return f"UnaryOperationNode({self.operator}, {self.operand})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self, n: int):
        if self.index + n >= len(self.tokens):
            return None
        return self.tokens[self.index + n]

    @property
    def current_token(self):
        return self.peek(0)

    @property
    def next_token(self):
        return self.peek(1)

    @property
    def at_end(self):
        return self.current_token is None

    def consume(self, n: int = 1):
        self.index += n

    def parse(self):
        return self.parse_expression()

    def parse_expression(self):
        return self.parse_binary_operation()

    def parse_binary_operation(self):
        left = self.parse_unary_operation()
        while not self.at_end and self.current_token.type == "operator":
            operator = self.parse_binary_operator()
            self.consume()
            right = self.parse_unary_operation()
            left = BinaryOperationNode(left, operator, right)
        return left

    def parse_unary_operation(self):
        # if self.current_token is not None and self.current_token.type == "operator":
        if not self.at_end and self.current_token.type == "operator":
            operator = self.parse_unary_operator()
            self.consume()
            operand = self.parse_unary_operation()
            return UnaryOperationNode(operator, operand)
        return self.parse_primary()

    def parse_primary(self):
        if self.current_token is None:
            raise ValueError("Unexpected end of input")
        if self.current_token.type == "number":
            token = self.current_token
            self.consume()
            return NumberNode(token)
        elif self.current_token.type == "paren" and self.current_token.value == "(":
            self.consume()
            expr = self.parse_expression()
            if self.current_token is None or self.current_token.type != "paren" or self.current_token.value != ")":
                raise ValueError("Expected closing parenthesis")
            self.consume()
            return expr
        raise ValueError(f"Unexpected token: {self.current_token}")

    def parse_binary_operator(self):
        if self.current_token is None or self.current_token.type != "operator":
            raise ValueError("Expected binary operator")
        if self.current_token.value not in BINARY_OP_TOKENS:
            raise ValueError(f"Unexpected binary operator: {self.current_token.value}")
        return self.current_token

    def parse_unary_operator(self):
        if self.current_token is None or self.current_token.type != "operator":
            raise ValueError("Expected unary operator")
        if self.current_token.value not in UNARY_OP_TOKENS:
            raise ValueError(f"Unexpected unary operator: {self.current_token.value}")
        return self.current_token

    def __new__(cls, tokens):
        # we hide the internal workings of the parser from the user, and return the result of the parse method
        self = super().__new__(cls)
        self.__init__(tokens)
        return self.parse()
