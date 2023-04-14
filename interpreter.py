def _visit_string(node):
    result = "visit"
    for c in type(node).__name__:
        if c.isupper():
            result += "_"
        result += c.lower()
    return result


class NodeVisitor:
    def visit(self, node):
        method_name = _visit_string(node)
        method = getattr(self, method_name, self.generic_visit)
        return method(node)  # noqa

    def generic_visit(self, node):
        raise Exception(f"No {_visit_string(node)} method defined")

    # __new__ visits the nodes in the AST
    def __new__(cls, ast, *args, **kwargs):
        return (super().__new__(cls)).visit(ast)


class Interpreter(NodeVisitor):
    def __call__(self, ast):
        return self.visit(ast)

    def visit_binary_operation_node(self, node):
        if node.operator.value == "+":
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator.value == "-":
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator.value == "*":
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator.value == "/":
            return self.visit(node.left) / self.visit(node.right)

    def visit_number_node(self, node):
        if "." in node.token.value:
            return float(node.token.value)
        return int(node.token.value)
