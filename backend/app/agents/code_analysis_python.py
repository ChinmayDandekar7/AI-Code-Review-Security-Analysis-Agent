"""
Code Analysis Agent — Python side.

Detects code smells, complexity issues, and design anti-patterns using
Python's built-in `ast` module (structural analysis, not regex pattern
matching -- that distinction matters because things like "how deeply is
this nested" or "how many independent paths through this function" can't
be reliably answered by scanning text, they need the actual tree).

Every check here returns a list of RawFinding tuples; the orchestrator
converts those into full Finding objects with IDs.
"""

import ast
from dataclasses import dataclass

LONG_METHOD_LINES = 40
TOO_MANY_PARAMS = 5
GOD_CLASS_METHODS = 15
DEEP_NESTING_THRESHOLD = 4
HIGH_COMPLEXITY_THRESHOLD = 10
MAGIC_NUMBER_IGNORE = {0, 1, -1, 2, 100}


@dataclass
class RawFinding:
    category: str
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    line_start: int
    line_end: int
    description: str
    remediation: str | None = None


class _BoundedComplexityVisitor(ast.NodeVisitor):
    """
    Computes cyclomatic complexity for a single function's body, without
    descending into nested function/class definitions (those get their own
    complexity score when the outer walk reaches them separately).
    """

    def __init__(self):
        self.complexity = 1  # base path

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += max(len(node.values) - 1, 0)
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.complexity += len(node.ifs)
        self.generic_visit(node)

    def _skip_nested_scope(self, node):
        # Don't recurse into nested function/class defs -- they're scored
        # independently when the outer walk visits them.
        pass

    visit_FunctionDef = _skip_nested_scope
    visit_AsyncFunctionDef = _skip_nested_scope
    visit_ClassDef = _skip_nested_scope
    visit_Lambda = _skip_nested_scope


def _function_complexity(func_node) -> int:
    visitor = _BoundedComplexityVisitor()
    for child in ast.iter_child_nodes(func_node):
        visitor.visit(child)
    return visitor.complexity


def _max_nesting_depth(func_node) -> int:
    NESTING_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)

    def depth(node, current):
        best = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, NESTING_NODES):
                best = max(best, depth(child, current + 1))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue  # nested scope, don't count into this function's depth
            else:
                best = max(best, depth(child, current))
        return best

    return depth(func_node, 0)


def _line_span(node) -> tuple[int, int]:
    start = node.lineno
    end = getattr(node, "end_lineno", start)
    return start, end


def _all_functions(tree):
    """All function defs anywhere in the tree, including methods."""
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _all_classes(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]


def check_long_methods(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        start, end = _line_span(func)
        length = end - start + 1
        if length > LONG_METHOD_LINES:
            severity = "high" if length > LONG_METHOD_LINES * 1.75 else "medium"
            findings.append(RawFinding(
                category="Long Method",
                severity=severity,
                line_start=start,
                line_end=end,
                description=f"Function '{func.name}' is {length} lines long "
                            f"(threshold: {LONG_METHOD_LINES}). Consider extracting "
                            f"cohesive chunks into smaller, well-named helper functions.",
                remediation="Split this function by identifying logically distinct "
                            "steps and extracting each into its own function.",
            ))
    return findings


def check_too_many_parameters(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        args = func.args
        count = len(args.args) + len(args.kwonlyargs)
        # Don't penalize 'self'/'cls' as a real parameter
        if args.args and args.args[0].arg in ("self", "cls"):
            count -= 1
        if count > TOO_MANY_PARAMS:
            start, end = _line_span(func)
            findings.append(RawFinding(
                category="Too Many Parameters",
                severity="medium",
                line_start=start,
                line_end=start,
                description=f"Function '{func.name}' takes {count} parameters "
                            f"(threshold: {TOO_MANY_PARAMS}). This is often a sign the "
                            f"function is doing too much or needs a parameter object.",
                remediation="Group related parameters into a dataclass or config object.",
            ))
    return findings


def check_god_class(tree) -> list[RawFinding]:
    findings = []
    for cls in _all_classes(tree):
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(methods) > GOD_CLASS_METHODS:
            start, end = _line_span(cls)
            findings.append(RawFinding(
                category="God Class",
                severity="high",
                line_start=start,
                line_end=end,
                description=f"Class '{cls.name}' has {len(methods)} methods "
                            f"(threshold: {GOD_CLASS_METHODS}), suggesting it has "
                            f"accumulated more responsibility than a single class should hold.",
                remediation="Identify cohesive groups of methods/fields and split them "
                            "into separate, focused classes.",
            ))
    return findings


def check_deep_nesting(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        depth = _max_nesting_depth(func)
        if depth > DEEP_NESTING_THRESHOLD:
            start, end = _line_span(func)
            findings.append(RawFinding(
                category="Deep Nesting",
                severity="medium",
                line_start=start,
                line_end=end,
                description=f"Function '{func.name}' has nesting depth {depth} "
                            f"(threshold: {DEEP_NESTING_THRESHOLD}). Deeply nested control "
                            f"flow is hard to read and test.",
                remediation="Use early returns / guard clauses to flatten nested conditionals.",
            ))
    return findings


def check_high_complexity(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        complexity = _function_complexity(func)
        if complexity > HIGH_COMPLEXITY_THRESHOLD:
            start, end = _line_span(func)
            findings.append(RawFinding(
                category="High Cyclomatic Complexity",
                severity="high",
                line_start=start,
                line_end=end,
                description=f"Function '{func.name}' has cyclomatic complexity "
                            f"{complexity} (threshold: {HIGH_COMPLEXITY_THRESHOLD}), "
                            f"meaning many independent paths through the code make it "
                            f"hard to test exhaustively.",
                remediation="Break the function into smaller pieces, each testable independently.",
            ))
    return findings


def check_mutable_default_args(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        for default in func.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                start, end = _line_span(func)
                findings.append(RawFinding(
                    category="Mutable Default Argument",
                    severity="high",
                    line_start=start,
                    line_end=start,
                    description=f"Function '{func.name}' uses a mutable default argument "
                                f"(list/dict/set). Defaults are evaluated once at definition "
                                f"time and shared across all calls, causing state to leak "
                                f"between unrelated calls.",
                    remediation="Use None as the default and create the mutable object "
                                "inside the function body instead.",
                ))
                break
    return findings


def check_bare_except(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            start, end = _line_span(node)
            is_bare = node.type is None
            is_pass_only = len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
            if is_bare:
                findings.append(RawFinding(
                    category="Bare Except Clause",
                    severity="medium",
                    line_start=start,
                    line_end=end,
                    description="Bare 'except:' catches every exception including "
                                "KeyboardInterrupt and SystemExit. Catch specific exception types.",
                    remediation="Replace with 'except SpecificException:' for the errors "
                                "you actually expect and can handle.",
                ))
            elif is_pass_only:
                findings.append(RawFinding(
                    category="Silently Swallowed Exception",
                    severity="medium",
                    line_start=start,
                    line_end=end,
                    description="Exception is caught and silently discarded (except: pass), "
                                "hiding failures and making bugs much harder to diagnose later.",
                    remediation="At minimum, log the exception. Consider whether it should "
                                "be handled or re-raised.",
                ))
    return findings


def check_magic_numbers(tree) -> list[RawFinding]:
    findings = []
    for func in _all_functions(tree):
        magic_lines = set()
        for node in ast.walk(func):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not func:
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in MAGIC_NUMBER_IGNORE and not isinstance(node.value, bool):
                    magic_lines.add(node.lineno)
        if len(magic_lines) >= 2:
            start, end = _line_span(func)
            findings.append(RawFinding(
                category="Magic Numbers",
                severity="low",
                line_start=min(magic_lines),
                line_end=max(magic_lines),
                description=f"Function '{func.name}' contains {len(magic_lines)} unexplained "
                            f"numeric literals. Consider named constants to document their meaning.",
                remediation="Extract repeated or non-obvious literals into named constants.",
            ))
    return findings


def check_duplicate_functions(tree) -> list[RawFinding]:
    """
    Simple structural duplicate detection: normalizes each function body by
    stripping variable/attribute names and constants, then flags exact
    matches. This catches literal copy-paste; it won't catch semantically
    equivalent code written differently, which needs a much heavier
    analysis than is in scope here.
    """
    def normalize(node) -> str:
        class Normalizer(ast.NodeTransformer):
            def visit_Name(self, n):
                return ast.copy_location(ast.Name(id="_", ctx=n.ctx), n)

            def visit_Constant(self, n):
                return ast.copy_location(ast.Constant(value="_"), n)

            def visit_arg(self, n):
                n.arg = "_"
                self.generic_visit(n)
                return n

        copied = ast.parse(ast.unparse(node))
        func_copy = copied.body[0]
        func_copy.name = "_"  # the function's own name is a plain string, not a Name node
        Normalizer().visit(func_copy)
        return ast.dump(func_copy)

    seen: dict[str, list] = {}
    for func in _all_functions(tree):
        start, end = _line_span(func)
        if end - start + 1 < 4:
            continue  # too small to be meaningful duplication
        try:
            key = normalize(func)
        except Exception:
            continue
        seen.setdefault(key, []).append(func)

    findings = []
    for func_list in seen.values():
        if len(func_list) > 1:
            names = ", ".join(f"'{f.name}'" for f in func_list)
            start, end = _line_span(func_list[0])
            findings.append(RawFinding(
                category="Duplicate Code",
                severity="medium",
                line_start=start,
                line_end=end,
                description=f"Functions {names} have structurally identical bodies "
                            f"(same logic, different names). Duplicated logic means a fix "
                            f"in one copy is easy to forget applying to the others.",
                remediation="Extract the shared logic into a single function and call it "
                            "from both places.",
            ))
    return findings


ALL_CHECKS = [
    check_long_methods,
    check_too_many_parameters,
    check_god_class,
    check_deep_nesting,
    check_high_complexity,
    check_mutable_default_args,
    check_bare_except,
    check_magic_numbers,
    check_duplicate_functions,
]


def analyze_python(code: str) -> list[RawFinding]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # syntax validation is a separate, earlier concern

    findings = []
    for check in ALL_CHECKS:
        findings.extend(check(tree))
    return findings
