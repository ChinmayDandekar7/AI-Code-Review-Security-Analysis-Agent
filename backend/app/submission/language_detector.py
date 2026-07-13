"""
Auto-detect whether pasted code is Python or Java.

Approach: weighted regex scoring, not a full parse. This matters because the
whole point is to detect language on code that might be syntactically broken
(that's exactly when a developer needs validation most) -- so we can't rely
on "try parsing it and see what succeeds", since broken code fails to parse
in both languages.

Each pattern below is something that's either impossible or highly unusual
in the other language. Weights roughly reflect how strong a signal each
pattern is.
"""

import re

PYTHON_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"^\s*def\s+\w+\s*\(.*\)\s*:", re.MULTILINE), 4),
    (re.compile(r"^\s*elif\s+.+:", re.MULTILINE), 4),
    (re.compile(r"^\s*class\s+\w+(\(.*\))?\s*:", re.MULTILINE), 3),
    (re.compile(r"\bself\b"), 3),
    (re.compile(r"^\s*import\s+\w+\s*$", re.MULTILINE), 2),
    (re.compile(r"^\s*from\s+\S+\s+import\s+"), 2),
    (re.compile(r"\bprint\s*\("), 2),
    (re.compile(r"^\s*#"), 1),
    (re.compile(r":\s*$", re.MULTILINE), 1),
]

JAVA_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"\bpublic\s+class\s+\w+"), 4),
    (re.compile(r"\bpublic\s+static\s+void\s+main\s*\("), 5),
    (re.compile(r"\bSystem\.out\.println"), 4),
    (re.compile(r"^\s*import\s+java\.", re.MULTILINE), 4),
    (re.compile(r"\b(public|private|protected)\s+\w+.*\(.*\)\s*\{"), 3),
    (re.compile(r";\s*$", re.MULTILINE), 2),
    (re.compile(r"\bnew\s+\w+\s*\("), 2),
    (re.compile(r"^\s*//"), 1),
]


def detect_language(code: str) -> str:
    """
    Returns "python" or "java". Defaults to "python" on a tie or when the
    input has no strong signal either way (e.g. an empty snippet).
    """
    python_score = sum(weight for pattern, weight in PYTHON_PATTERNS if pattern.search(code))
    java_score = sum(weight for pattern, weight in JAVA_PATTERNS if pattern.search(code))

    if java_score > python_score:
        return "java"
    return "python"
