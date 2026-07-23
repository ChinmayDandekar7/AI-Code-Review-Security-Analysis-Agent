"""
Auto-detect whether pasted code is Python or Java using weighted pattern
matching (not a full parse, since it needs to work on broken code too).
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
    python_score = sum(weight for pattern, weight in PYTHON_PATTERNS if pattern.search(code))
    java_score = sum(weight for pattern, weight in JAVA_PATTERNS if pattern.search(code))

    if java_score > python_score:
        return "java"
    return "python"
