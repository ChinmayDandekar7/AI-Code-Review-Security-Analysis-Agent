"""
Detection logic shared across languages. Hardcoded secrets don't have a
meaningfully different AST shape in Python vs. Java -- a credential
assigned to a suspiciously-named variable is a text pattern, not a
structural one -- so this check runs identically for both.
"""

import re
from .code_analysis_python import RawFinding

SECRET_PATTERN = re.compile(
    r"(?i)\b[a-zA-Z_]*(api[_-]?key|secret[_-]?key|password|passwd|access[_-]?key|"
    r"auth[_-]?token|private[_-]?key)[a-zA-Z0-9_]*\s*[=:]\s*[\"']([^\"']{8,})[\"']"
)
PLACEHOLDER_VALUES = {
    "changeme", "your_password_here", "xxxxxxxx", "placeholder", "example",
    "your-api-key-here", "insert_key_here", "todo", "fixme", "test", "dummy",
}


def check_hardcoded_secrets(code: str) -> list[RawFinding]:
    findings = []
    for i, line in enumerate(code.split("\n"), start=1):
        match = SECRET_PATTERN.search(line)
        if match:
            value = match.group(2).lower()
            if value in PLACEHOLDER_VALUES or value.startswith("<") or value.startswith("${"):
                continue
            findings.append(RawFinding(
                category="Hardcoded Secret",
                severity="critical",
                line_start=i,
                line_end=i,
                description=f"Line {i} appears to assign a hardcoded credential "
                            f"('{match.group(1)}') directly in source code. Committed "
                            f"secrets remain recoverable from version control history "
                            f"even after later removal.",
                remediation="Load secrets from environment variables or a secrets "
                            "manager instead of hardcoding them.",
            ))
    return findings
