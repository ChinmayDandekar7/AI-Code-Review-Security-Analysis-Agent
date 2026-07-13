"""
Syntax validation for submitted code.

This is intentionally the FIRST real logic in the project — it's small,
self-contained, and easy to test in isolation before anything else depends
on it.
"""

import ast
import javalang


def validate_python(code: str) -> tuple[bool, list[str]]:
    try:
        ast.parse(code)
        return True, []
    except SyntaxError as e:
        return False, [f"Line {e.lineno}: {e.msg}"]


def validate_java(code: str) -> tuple[bool, list[str]]:
    try:
        javalang.parse.parse(code)
        return True, []
    except javalang.parser.JavaSyntaxError as e:
        # javalang's JavaSyntaxError often has an empty str() -- the useful
        # info lives in .description and .at instead.
        description = getattr(e, "description", "") or "Syntax error"
        position = getattr(e, "at", None)
        message = f"{description} (near {position})" if position else description
        return False, [message]
    except Exception as e:
        # javalang raises various error types for malformed input;
        # we normalize everything into a readable string.
        return False, [f"Parse error: {str(e)}"]


def validate(code: str, language: str) -> tuple[bool, list[str]]:
    if language == "python":
        return validate_python(code)
    elif language == "java":
        return validate_java(code)
    raise ValueError(f"Unsupported language: {language}")
