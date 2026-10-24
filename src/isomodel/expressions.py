"""Mały interpreter notacji YAML; bez eval i wykonywania kodu z modelu.

Kwantyfikator wiąże wyrażenie do końca bieżącego nawiasu/tekstu.
Całe drzewo jest sprawdzane przed oceną, także puste kwantyfikatory.
Trace: WIT1, WIT2, WIT4, G0, S2, S4, S7a, S9, L2, L4.
"""

import re

from .loader import ModelError


class UnsupportedSemantics(ModelError):
    """Reguła poza zakresem wykonawcy."""


class InputError(ModelError):
    """Brak lub błędny typ danych do wykonania reguły."""


TOKEN = re.compile(r"\s*(=>|[(){}.,:=+<]|[A-Za-z_][A-Za-z_0-9]*|[0-9]+)")
FUNCTIONS = {"deps": 1, "type": 1, "checks_ok": 1, "in_scope": 1, "snapshot": 1,
             "count": 1, "oldest": 2, "newest": 2}


class Parser:
    def __init__(self, text):
        self.tokens = []
        position = 0
        while position < len(text.rstrip()):
            match = TOKEN.match(text, position)
            if match is None:
                raise UnsupportedSemantics(f"Nieznany zapis: {text[position:]}")
            self.tokens.append(match[1])
            position = match.end()
        self.position = 0

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def take(self, expected=None):
        value = self.peek()
        if value is None or expected is not None and value != expected:
            raise UnsupportedSemantics(f"Oczekiwano {expected}, otrzymano {value}")
        self.position += 1
        return value

    def parse(self):
        node = self.implies()
        if self.peek() is not None:
            raise UnsupportedSemantics(f"Nadmiarowy zapis: {self.tokens[self.position:]}")
        return node

    def implies(self):
        node = self.disjunction()
        if self.peek() == "=>":
            self.take()
            node = ("=>", node, self.implies())
        return node

    def disjunction(self):
        node = self.conjunction()
        while self.peek() == "or":
            self.take()
            node = ("or", node, self.conjunction())
        return node

    def conjunction(self):
        node = self.negation()
        while self.peek() == "and":
            self.take()
            node = ("and", node, self.negation())
        return node

    def negation(self):
        if self.peek() == "not":
            self.take()
            return ("not", self.negation())
        return self.comparison()

    def comparison(self):
        node = self.addition()
        if self.peek() in {"=", "<", "in", "not"}:
            operator = self.take()
            if operator == "not":
                self.take("in")
                operator = "not in"
            node = (operator, node, self.addition())
        return node

    def addition(self):
        node = self.atom()
        while self.peek() == "+":
            self.take()
            node = ("+", node, self.atom())
        return node

    def atom(self):
        token = self.take()
        if token in {"forall", "exists"}:
            variable = self.take()
            if not variable.isidentifier():
                raise UnsupportedSemantics("Niepoprawna zmienna kwantyfikatora")
            if self.peek() == "in":
                self.take()
                domain = self.implies()
            else:
                if variable not in {"e", "q"}:
                    raise UnsupportedSemantics(f"Brak dziedziny dla {variable}")
                domain = ("name", "all_items" if variable == "e" else "all_questions")
            self.take(":")
            return (token, variable, domain, self.implies())
        if token == "(":
            node = self.implies()
            self.take(")")
        elif token == "{":
            values = []
            if self.peek() != "}":
                values.append(self.implies())
                while self.peek() == ",":
                    self.take()
                    values.append(self.implies())
            self.take("}")
            node = ("set", tuple(values))
        elif token.isdecimal():
            node = ("literal", int(token))
        elif token in {"true", "false"}:
            node = ("literal", token == "true")
        elif token.isidentifier():
            if self.peek() == "(":
                self.take()
                arguments = []
                if self.peek() != ")":
                    arguments.append(self.implies())
                    while self.peek() == ",":
                        self.take()
                        arguments.append(self.implies())
                self.take(")")
                node = ("call", token, tuple(arguments))
            else:
                node = ("name", token)
        else:
            raise UnsupportedSemantics(f"Nieoczekiwany token: {token}")
        while self.peek() == ".":
            self.take()
            node = ("attr", node, self.take())
        return node


def compile_expression(text, model):
    node = Parser(text).parse()
    names = {"e", "q", "release", "tests_ok", "unambiguous_answer", "blocking_first",
             "newly_suspect", "all_items", "all_questions", "none"}
    names |= set(model["parameters"]) | set(model["item_variables"]) | set(model["release_control_variables"])
    names |= set(model["question_variables"])
    names |= set().union(*(model[f"{kind}_states"] for kind in ("item", "question", "release")))
    attributes = {"id", "type", "depends_on", "requires_approval"}
    attributes |= set().union(*(model[f"{kind}_variables"] for kind in ("item", "question", "release")))

    def check(tree, available):
        op = tree[0]
        if op == "name":
            if tree[1] not in available:
                raise UnsupportedSemantics(f"Nieznana nazwa: {tree[1]}")
        elif op == "literal":
            return
        elif op == "call":
            if tree[1] not in FUNCTIONS or len(tree[2]) != FUNCTIONS[tree[1]]:
                raise UnsupportedSemantics(f"Nieobsługiwana funkcja lub liczba argumentów: {tree[1]}")
            for argument in tree[2]:
                check(argument, available)
        elif op in {"forall", "exists"}:
            check(tree[2], available)
            check(tree[3], available | {tree[1]})
        elif op == "attr":
            if tree[2] not in attributes:
                raise UnsupportedSemantics(f"Nieznany atrybut: {tree[2]}")
            check(tree[1], available)
        elif op == "set":
            for child in tree[1]:
                check(child, available)
        else:
            for child in tree[1:]:
                check(child, available)

    check(node, names)
    return node


def boolean(value):
    if type(value) is not bool:
        raise InputError(f"Oczekiwano bool, otrzymano {type(value).__name__}")
    return value


def evaluate(node, environment, functions):
    op = node[0]
    if op == "literal":
        return node[1]
    if op == "name":
        if node[1] not in environment:
            raise InputError(f"Brak wartości: {node[1]}")
        return environment[node[1]]
    if op == "attr":
        parent = evaluate(node[1], environment, functions)
        if not isinstance(parent, dict) or node[2] not in parent:
            raise InputError(f"Brak atrybutu: {node[2]}")
        return parent[node[2]]
    if op == "set":
        return {evaluate(child, environment, functions) for child in node[1]}
    if op == "call":
        return functions[node[1]](*(evaluate(arg, environment, functions) for arg in node[2]))
    if op in {"forall", "exists"}:
        domain = evaluate(node[2], environment, functions)
        values = [boolean(evaluate(node[3], environment | {node[1]: value}, functions)) for value in domain]
        return all(values) if op == "forall" else any(values)
    left = evaluate(node[1], environment, functions)
    if op == "not":
        return not boolean(left)
    right = evaluate(node[2], environment, functions)
    if op in {"and", "or", "=>"}:
        left, right = boolean(left), boolean(right)
        return {"and": left and right, "or": left or right, "=>": not left or right}[op]
    if op == "=":
        return type(left) is type(right) and left == right
    if op == "in":
        return left in right
    if op == "not in":
        return left not in right
    if op in {"<", "+"}:
        if type(left) is not int or type(right) is not int:
            raise InputError(f"{op}: oczekiwano liczb całkowitych")
        return left < right if op == "<" else left + right
    raise UnsupportedSemantics(f"Nieobsługiwany operator: {op}")
