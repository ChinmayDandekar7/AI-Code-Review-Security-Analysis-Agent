"""
Security Vulnerability Agent — Python side.

Uses AST analysis where it buys real precision (e.g. "is this argument a
literal string or something built at runtime?"), and falls back to
pattern matching for secrets, which don't have a meaningful AST shape --
a hardcoded API key looks like any other string literal syntactically, so
detecting it is inherently a text/pattern problem, not a structural one.
"""

import ast
from .code_analysis_python import RawFinding
from .security_common import check_hardcoded_secrets

HASH_FUNCS = {"md5", "sha1"}
DANGEROUS_CALLS = {"eval", "exec"}
SUBPROCESS_FUNCS = {"run", "call", "check_call", "check_output", "Popen"}


def _is_dynamic_string(node) -> bool:
    """True if a node builds a string at runtime (f-string, concatenation,
    .format()) rather than being a plain literal -- the key signal for
    injection-style vulnerabilities."""
    if isinstance(node, ast.JoinedStr):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == "format":
            return True
    return False


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def check_eval_exec(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) in DANGEROUS_CALLS:
            findings.append(RawFinding(
                category="Dangerous Dynamic Execution",
                severity="critical",
                line_start=node.lineno,
                line_end=node.lineno,
                description=f"Use of '{_call_name(node)}()' executes arbitrary Python "
                            f"code. If any part of the argument is influenced by "
                            f"untrusted input, this is a remote code execution risk.",
                remediation="Avoid eval/exec entirely, or if truly unavoidable, "
                            "ensure the input is fully trusted and never derived from "
                            "user input.",
            ))
    return findings


def _build_assignment_map(func_node) -> dict:
    """
    Lightweight same-function variable tracking: maps a variable name to
    the most recent value assigned to it within this function, in source
    order. This is NOT full dataflow/taint analysis -- it doesn't follow
    branches, reassignment inside loops, or cross-function flow -- but it
    catches the extremely common real-world pattern of building a query
    string into a variable a few lines before passing it to .execute().
    """
    assignments = {}
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                assignments[target.id] = node.value
    return assignments


def _resolve_dynamic(node, assignments: dict) -> bool:
    """True if `node` is dynamic directly, or is a variable name that was
    last assigned a dynamic value in the same function."""
    if _is_dynamic_string(node):
        return True
    if isinstance(node, ast.Name) and node.id in assignments:
        return _is_dynamic_string(assignments[node.id])
    return False


def check_sql_injection(tree) -> list[RawFinding]:
    findings = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        assignments = _build_assignment_map(func)
        for node in ast.walk(func):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("execute", "executemany") and node.args:
                    first_arg = node.args[0]
                    if _resolve_dynamic(first_arg, assignments):
                        findings.append(RawFinding(
                            category="SQL Injection",
                            severity="critical",
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            description="A query string is being built dynamically "
                                        "(f-string, concatenation, or .format()) and passed "
                                        "to .execute(), either directly or via a variable "
                                        "assigned a few lines earlier. This allows an "
                                        "attacker to alter the query's logic via crafted input.",
                            remediation="Use parameterized queries: pass placeholders "
                                        "(e.g. '%s' or '?') in the query string and supply "
                                        "values as a separate tuple argument.",
                        ))
    return findings


def check_insecure_hashing(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "hashlib":
                if node.func.attr in HASH_FUNCS:
                    findings.append(RawFinding(
                        category="Insecure Hashing Algorithm",
                        severity="high",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        description=f"hashlib.{node.func.attr}() is a fast, general-purpose "
                                    f"hash -- unsuitable for passwords since it can be "
                                    f"brute-forced at high speed. Also cryptographically "
                                    f"broken for collision resistance.",
                        remediation="Use a slow, salted password-hashing algorithm "
                                    "(bcrypt, scrypt, or Argon2) instead.",
                    ))
    return findings


def check_command_injection(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)

        if name == "system" and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                if node.args and _is_dynamic_string(node.args[0]):
                    findings.append(RawFinding(
                        category="Command Injection",
                        severity="critical",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        description="os.system() is called with a dynamically built "
                                    "string, invoking a shell with attacker-influenceable "
                                    "input if any part of it comes from untrusted data.",
                        remediation="Use subprocess.run() with a list of arguments and "
                                    "shell=False instead of building a shell command string.",
                    ))

        if name in SUBPROCESS_FUNCS:
            has_shell_true = any(
                kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                for kw in node.keywords
            )
            dynamic_arg = bool(node.args) and _is_dynamic_string(node.args[0])
            if has_shell_true and dynamic_arg:
                findings.append(RawFinding(
                    category="Command Injection",
                    severity="critical",
                    line_start=node.lineno,
                    line_end=node.lineno,
                    description=f"subprocess.{name}() is called with shell=True and a "
                                f"dynamically built command string -- this invokes a "
                                f"shell and is vulnerable to command injection if any "
                                f"part of the string comes from untrusted input.",
                    remediation="Pass the command as a list of arguments with "
                                "shell=False, avoiding shell interpretation entirely.",
                ))
    return findings


def check_insecure_deserialization(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "loads" and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "pickle":
                    findings.append(RawFinding(
                        category="Insecure Deserialization",
                        severity="critical",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        description="pickle.loads() on untrusted data can execute "
                                    "arbitrary code as a side effect of deserialization.",
                        remediation="Use a data format without executable semantics "
                                    "(JSON) for any data crossing a trust boundary.",
                    ))
            if node.func.attr == "load" and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "yaml":
                    has_safe_loader = any(
                        kw.arg == "Loader" for kw in node.keywords
                    )
                    if not has_safe_loader:
                        findings.append(RawFinding(
                            category="Insecure Deserialization",
                            severity="high",
                            line_start=node.lineno,
                            line_end=node.lineno,
                            description="yaml.load() without an explicit Loader defaults "
                                        "to the unsafe full loader in older PyYAML versions, "
                                        "which can construct arbitrary Python objects.",
                            remediation="Use yaml.safe_load() or pass Loader=yaml.SafeLoader.",
                        ))
    return findings


def check_flask_xss(tree) -> list[RawFinding]:
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node) == "render_template_string":
            if node.args and _is_dynamic_string(node.args[0]):
                findings.append(RawFinding(
                    category="Cross-Site Scripting (XSS)",
                    severity="high",
                    line_start=node.lineno,
                    line_end=node.lineno,
                    description="render_template_string() is called with a dynamically "
                                "built template string. If any part comes from user "
                                "input, this allows server-side template injection and/or "
                                "XSS, since the input is parsed as template syntax.",
                    remediation="Use render_template() with a static template file and "
                                "pass user data as context variables, which Jinja2 "
                                "auto-escapes by default.",
                ))
    return findings


def check_broken_access_control(tree) -> list[RawFinding]:
    """
    Low-confidence heuristic: flags route handlers whose name/path suggests
    a sensitive action (delete/admin/update) but whose decorators show no
    obvious authorization dependency. Broken access control is fundamentally
    a business-logic concern that static analysis can't fully verify --
    this is a "worth a human look" signal, not a confirmed vulnerability,
    and is reported at low severity accordingly.
    """
    findings = []
    sensitive_words = ("delete", "admin", "remove")
    auth_hints = ("auth", "login", "permission", "current_user", "require")

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        route_decorators = [
            d for d in node.decorator_list
            if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
            and d.func.attr in ("get", "post", "put", "delete", "patch", "route")
        ]
        if not route_decorators:
            continue

        name_lower = node.name.lower()
        decorator_text = ast.dump(node).lower()
        looks_sensitive = any(w in name_lower for w in sensitive_words)
        has_auth_hint = any(h in decorator_text for h in auth_hints)

        if looks_sensitive and not has_auth_hint:
            findings.append(RawFinding(
                category="Possible Broken Access Control",
                severity="low",
                line_start=node.lineno,
                line_end=node.lineno,
                description=f"Route handler '{node.name}' appears to perform a "
                            f"sensitive action but shows no obvious authorization "
                            f"check in its signature or decorators. This is a "
                            f"heuristic, not a confirmed vulnerability -- please "
                            f"verify manually.",
                remediation="Confirm this endpoint enforces an authorization check "
                            "(e.g. a Depends() on a current-user/permission function) "
                            "before performing the action.",
            ))
    return findings


ALL_CHECKS_AST = [
    check_eval_exec,
    check_sql_injection,
    check_insecure_hashing,
    check_command_injection,
    check_insecure_deserialization,
    check_flask_xss,
    check_broken_access_control,
]


def analyze_python_security(code: str) -> list[RawFinding]:
    findings = check_hardcoded_secrets(code)  # text-based, works even if parse fails
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return findings
    for check in ALL_CHECKS_AST:
        findings.extend(check(tree))
    return findings
