"""
Code Analysis Agent — Java side.

Uses javalang's parse tree for structure (classes, methods, control flow),
combined with brace-matching against the raw source text to compute line
spans -- javalang tracks start positions but not end positions, so span
detection needs this small workaround.
"""

import re
import javalang
from .code_analysis_python import RawFinding  # reuse the same result shape

LONG_METHOD_LINES = 40
TOO_MANY_PARAMS = 5
GOD_CLASS_MEMBERS = 15
DEEP_NESTING_THRESHOLD = 4
HIGH_COMPLEXITY_THRESHOLD = 10
MAGIC_NUMBER_IGNORE = {"0", "1", "2", "100"}

NESTING_TYPES = (
    javalang.tree.IfStatement,
    javalang.tree.ForStatement,
    javalang.tree.WhileStatement,
    javalang.tree.DoStatement,
    javalang.tree.TryStatement,
    javalang.tree.SwitchStatement,
)

COMPLEXITY_TYPES = (
    javalang.tree.IfStatement,
    javalang.tree.ForStatement,
    javalang.tree.WhileStatement,
    javalang.tree.DoStatement,
    javalang.tree.CatchClause,
    javalang.tree.SwitchStatementCase,
)


def _find_block_end_line(source_lines: list[str], start_line_idx: int) -> int:
    """Given the 0-indexed line where a method/class signature starts, find
    the 1-indexed line number of its closing brace via brace counting."""
    depth = 0
    started = False
    for i in range(start_line_idx, len(source_lines)):
        for ch in source_lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return i + 1
    return len(source_lines)


def _complexity(node) -> int:
    complexity = 1
    for node_type in COMPLEXITY_TYPES:
        for _, child in node.filter(node_type):
            complexity += 1
    for _, child in node.filter(javalang.tree.BinaryOperation):
        if child.operator in ("&&", "||"):
            complexity += 1
    return complexity


def _max_nesting_depth(node) -> int:
    def depth(n, current):
        best = current
        children = getattr(n, "children", None)
        if not children:
            return best
        for child in children:
            items = child if isinstance(child, (list, tuple, set)) else [child]
            for item in items:
                if isinstance(item, NESTING_TYPES):
                    best = max(best, depth(item, current + 1))
                elif hasattr(item, "children"):
                    best = max(best, depth(item, current))
        return best

    return depth(node, 0)


def analyze_java(code: str) -> list[RawFinding]:
    try:
        tree = javalang.parse.parse(code)
    except Exception:
        return []  # syntax validation is a separate, earlier concern

    lines = code.split("\n")
    findings: list[RawFinding] = []

    for _, method in tree.filter(javalang.tree.MethodDeclaration):
        if method.position is None:
            continue
        start = method.position.line
        end = _find_block_end_line(lines, start - 1)
        length = end - start + 1

        if length > LONG_METHOD_LINES:
            severity = "high" if length > LONG_METHOD_LINES * 1.75 else "medium"
            findings.append(RawFinding(
                category="Long Method",
                severity=severity,
                line_start=start,
                line_end=end,
                description=f"Method '{method.name}' is {length} lines long "
                            f"(threshold: {LONG_METHOD_LINES}). Consider extracting "
                            f"cohesive chunks into smaller, well-named helper methods.",
                remediation="Split this method by identifying logically distinct "
                            "steps and extracting each into its own method.",
            ))

        param_count = len(method.parameters)
        if param_count > TOO_MANY_PARAMS:
            findings.append(RawFinding(
                category="Too Many Parameters",
                severity="medium",
                line_start=start,
                line_end=start,
                description=f"Method '{method.name}' takes {param_count} parameters "
                            f"(threshold: {TOO_MANY_PARAMS}). This is often a sign the "
                            f"method is doing too much or needs a parameter object.",
                remediation="Group related parameters into a dedicated class.",
            ))

        complexity = _complexity(method)
        if complexity > HIGH_COMPLEXITY_THRESHOLD:
            findings.append(RawFinding(
                category="High Cyclomatic Complexity",
                severity="high",
                line_start=start,
                line_end=end,
                description=f"Method '{method.name}' has cyclomatic complexity "
                            f"{complexity} (threshold: {HIGH_COMPLEXITY_THRESHOLD}), "
                            f"meaning many independent paths through the code make it "
                            f"hard to test exhaustively.",
                remediation="Break the method into smaller pieces, each testable independently.",
            ))

        nesting = _max_nesting_depth(method)
        if nesting > DEEP_NESTING_THRESHOLD:
            findings.append(RawFinding(
                category="Deep Nesting",
                severity="medium",
                line_start=start,
                line_end=end,
                description=f"Method '{method.name}' has nesting depth {nesting} "
                            f"(threshold: {DEEP_NESTING_THRESHOLD}). Deeply nested control "
                            f"flow is hard to read and test.",
                remediation="Use early returns / guard clauses to flatten nested conditionals.",
            ))

        magic_lines = set()
        for _, literal in method.filter(javalang.tree.Literal):
            val = literal.value
            if val and (val[0].isdigit() or (val[0] == "-" and len(val) > 1 and val[1].isdigit())):
                stripped = val.rstrip("lLfFdD")
                if stripped not in MAGIC_NUMBER_IGNORE and literal.position:
                    magic_lines.add(literal.position.line)
        if len(magic_lines) >= 2:
            findings.append(RawFinding(
                category="Magic Numbers",
                severity="low",
                line_start=min(magic_lines),
                line_end=max(magic_lines),
                description=f"Method '{method.name}' contains {len(magic_lines)} unexplained "
                            f"numeric literals. Consider named constants to document their meaning.",
                remediation="Extract repeated or non-obvious literals into named constants.",
            ))

    for _, cls in tree.filter(javalang.tree.ClassDeclaration):
        members = [m for m in cls.body if isinstance(
            m, (javalang.tree.MethodDeclaration, javalang.tree.FieldDeclaration)
        )]
        if len(members) > GOD_CLASS_MEMBERS and cls.position:
            start = cls.position.line
            end = _find_block_end_line(lines, start - 1)
            findings.append(RawFinding(
                category="God Class",
                severity="high",
                line_start=start,
                line_end=end,
                description=f"Class '{cls.name}' has {len(members)} members "
                            f"(threshold: {GOD_CLASS_MEMBERS}), suggesting it has "
                            f"accumulated more responsibility than a single class should hold.",
                remediation="Identify cohesive groups of methods/fields and split them "
                            "into separate, focused classes.",
            ))

    for _, try_stmt in tree.filter(javalang.tree.TryStatement):
        if not try_stmt.catches or try_stmt.position is None:
            continue
        # CatchClause nodes don't carry a position in javalang; find each
        # "catch (" occurrence in source order starting from the try block,
        # matching them positionally to try_stmt.catches (same order).
        catch_lines = []
        search_start = try_stmt.position.line - 1
        for i in range(search_start, len(lines)):
            if re.search(r"\bcatch\s*\(", lines[i]):
                catch_lines.append(i + 1)
                if len(catch_lines) == len(try_stmt.catches):
                    break
        for catch, line in zip(try_stmt.catches, catch_lines):
            if catch.block == []:
                findings.append(RawFinding(
                    category="Empty Catch Block",
                    severity="medium",
                    line_start=line,
                    line_end=line,
                    description="Exception is caught and the catch block is empty, silently "
                                "discarding the error and making bugs much harder to diagnose later.",
                    remediation="At minimum, log the exception. Consider whether it should "
                                "be handled or rethrown.",
                ))

    return findings
